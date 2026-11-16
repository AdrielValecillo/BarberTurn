"""F1.04 · GET /public/barberias/{slug}/turnos (RF-03, RF-04, RN-02 a RN-05)."""

from datetime import date, datetime, time, timedelta, timezone
from time import perf_counter
from uuid import UUID

import asyncpg
import httpx
import pytest

pytestmark = pytest.mark.integracion

type Con = "asyncpg.Connection[asyncpg.Record]"

BOGOTA = timezone(timedelta(hours=-5))  # sin horario de verano: sirve para leer las horas en las pruebas
NORTE = UUID("00000000-0000-4000-8000-00000000b001")
CARLOS = UUID("00000000-0000-4000-8000-00000000a001")
CORTE_Y_BARBA = UUID("00000000-0000-4000-8000-00000000c003")  # 45 min


async def _en_una_semana(con: Con) -> date:
    # Dentro de la ventana (30 días) y lejos de la anticipación (60 min).
    fecha: date = await con.fetchval("select (now() at time zone 'America/Bogota')::date + 7")
    return fecha


def _local(fecha: date, hhmm: str) -> datetime:
    return datetime.fromisoformat(f"{fecha}T{hhmm}").replace(tzinfo=BOGOTA)


async def _barberia(
    con: Con, slug: str, duracion: int, barberos: dict[str, tuple[int, str, str]], fecha: date
) -> dict[str, UUID]:
    """Barbería nueva con un servicio y barberos {nombre: (orden, desde, hasta)} que lo prestan el día de `fecha`."""
    ids: dict[str, UUID] = {}
    ids["barberia"] = await con.fetchval(
        "insert into barberias (nombre, slug, direccion) values ($1, $1, 'Cra 1') returning id", slug
    )
    ids["servicio"] = await con.fetchval(
        "insert into servicios (barberia_id, nombre, duracion_min, precio_cop)"
        " values ($1, 'Corte', $2, 20000) returning id",
        ids["barberia"],
        duracion,
    )
    for nombre, (orden, desde, hasta) in barberos.items():
        ids[nombre] = await _barbero(con, ids["barberia"], ids["servicio"], nombre, orden, fecha, desde, hasta)
    return ids


async def _barbero(
    con: Con, barberia: UUID, servicio: UUID, nombre: str, orden: int, fecha: date, desde: str, hasta: str
) -> UUID:
    miembro: UUID = await con.fetchval(
        "insert into miembros (barberia_id, nombre, orden) values ($1, $2, $3) returning id", barberia, nombre, orden
    )
    await con.execute(
        "insert into miembro_servicios (barberia_id, miembro_id, servicio_id) values ($1, $2, $3)",
        barberia,
        miembro,
        servicio,
    )
    await con.execute(
        "insert into horarios (barberia_id, miembro_id, dia_semana, hora_inicio, hora_fin) values ($1, $2, $3, $4, $5)",
        barberia,
        miembro,
        fecha.isoweekday(),
        time.fromisoformat(desde),
        time.fromisoformat(hasta),
    )
    return miembro


async def _cita(con: Con, barberia: UUID, miembro: UUID, servicio: UUID, inicio: datetime, duracion: int) -> None:
    cliente = await con.fetchval(
        "insert into clientes (barberia_id, nombre, telefono_e164) values ($1, 'Ana', '+573009998877')"
        " on conflict (barberia_id, telefono_e164) do update set nombre = excluded.nombre returning id",
        barberia,
    )
    await con.execute(
        """
        insert into citas (barberia_id, miembro_id, servicio_id, cliente_id, inicio, fin,
                           servicio_nombre, duracion_min, precio_cop, token_hash)
        values ($1, $2, $3, $4, $5::timestamptz, $5::timestamptz + make_interval(mins => $6), 'Corte', $6, 20000,
                gen_random_uuid()::text)
        """,
        barberia,
        miembro,
        servicio,
        cliente,
        inicio,
        duracion,
    )


async def _turnos(cliente: httpx.AsyncClient, slug: str, **consulta: object) -> list[tuple[str, str]]:
    params = {k: str(v) for k, v in consulta.items()}
    respuesta = await cliente.get(f"/public/barberias/{slug}/turnos", params=params)
    assert respuesta.status_code == 200, respuesta.text
    return [
        (datetime.fromisoformat(t["inicio"]).astimezone(BOGOTA).strftime("%H:%M"), t["miembro_id"])
        for t in respuesta.json()
    ]


async def test_el_ejemplo_del_doc_01(cliente: httpx.AsyncClient, con: Con) -> None:
    # Doc 01 §4: horario de 14:00 a 19:00, cita de 15:00 a 15:45, servicio de 45 min y grilla de 15.
    fecha = await _en_una_semana(con)
    ids = await _barberia(con, "ejemplo", 45, {"pedro": (0, "14:00", "19:00")}, fecha)
    await _cita(con, ids["barberia"], ids["pedro"], ids["servicio"], _local(fecha, "15:00"), 45)

    turnos = await _turnos(cliente, "ejemplo", servicio=ids["servicio"], miembro=ids["pedro"], fecha=fecha)

    esperadas = ["14:00", "14:15"] + [f"{m // 60}:{m % 60:02d}" for m in range(15 * 60 + 45, 18 * 60 + 30, 15)]
    assert [h for h, _ in turnos] == esperadas
    assert esperadas[-1] == "18:15"
    assert {m for _, m in turnos} == {str(ids["pedro"])}


async def test_el_primero_disponible_reparte_segun_rn05(cliente: httpx.AsyncClient, con: Con) -> None:
    # RN-05: el turno más cercano; empate → menos citas ese día; sigue el empate → menor `orden`.
    fecha = await _en_una_semana(con)
    ids = await _barberia(con, "dos", 30, {"ana": (0, "14:00", "17:00"), "beto": (1, "14:00", "16:00")}, fecha)
    await _cita(con, ids["barberia"], ids["ana"], ids["servicio"], _local(fecha, "15:00"), 30)

    turnos = dict(await _turnos(cliente, "dos", servicio=ids["servicio"], fecha=fecha))

    assert turnos["14:00"] == str(ids["beto"])  # empate de hora: Ana ya tiene una cita ese día
    assert turnos["15:00"] == str(ids["beto"])  # Ana está ocupada
    assert turnos["16:00"] == str(ids["ana"])  # Beto ya no trabaja
    assert list(turnos) == sorted(turnos)  # una sola vez cada hora, en orden


async def test_sin_citas_el_empate_lo_gana_el_menor_orden(cliente: httpx.AsyncClient, con: Con) -> None:
    fecha = await _en_una_semana(con)
    ids = await _barberia(con, "empate", 30, {"ana": (1, "14:00", "15:00"), "beto": (0, "14:00", "15:00")}, fecha)

    turnos = await _turnos(cliente, "empate", servicio=ids["servicio"], fecha=fecha)

    assert {m for _, m in turnos} == {str(ids["beto"])}


async def test_un_barbero_o_servicio_de_otra_barberia_no_devuelve_nada(cliente: httpx.AsyncClient, con: Con) -> None:
    # RNF-08: /public/* salta la RLS, y turnos_disponibles() no mira la barbería del miembro.
    fecha = await _en_una_semana(con)
    ids = await _barberia(con, "otra", 30, {"pedro": (0, "08:00", "20:00")}, fecha)

    assert await _turnos(cliente, "barberia-norte", servicio=ids["servicio"], fecha=fecha) == []
    assert await _turnos(cliente, "barberia-norte", servicio=CORTE_Y_BARBA, miembro=ids["pedro"], fecha=fecha) == []
    assert await _turnos(cliente, "otra", servicio=CORTE_Y_BARBA, fecha=fecha) == []


async def test_un_barbero_que_no_presta_el_servicio_no_devuelve_nada(cliente: httpx.AsyncClient, con: Con) -> None:
    fecha = await _en_una_semana(con)
    await con.execute("delete from miembro_servicios where miembro_id = $1 and servicio_id = $2", CARLOS, CORTE_Y_BARBA)

    assert await _turnos(cliente, "barberia-norte", servicio=CORTE_Y_BARBA, miembro=CARLOS, fecha=fecha) == []


async def test_una_barberia_suspendida_no_esta_disponible(cliente: httpx.AsyncClient, con: Con) -> None:
    await con.execute("update barberias set estado = 'suspendida' where id = $1", NORTE)
    fecha = await _en_una_semana(con)

    respuesta = await cliente.get(
        "/public/barberias/barberia-norte/turnos", params={"servicio": str(CORTE_Y_BARBA), "fecha": str(fecha)}
    )

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "barberia_no_disponible"


async def test_responde_en_menos_de_500_ms(cliente: httpx.AsyncClient, con: Con) -> None:
    # RNF-04, con los barberos del seed y "el primero disponible".
    fecha = await _en_una_semana(con)
    inicio = perf_counter()
    await _turnos(cliente, "barberia-norte", servicio=CORTE_Y_BARBA, fecha=fecha)
    assert perf_counter() - inicio < 0.5
