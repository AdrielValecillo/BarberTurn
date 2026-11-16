"""F1.05 y F1.06 · POST /public/citas (RF-05, RF-06, RN-01, RN-02, RN-10, RN-11, RN-13, RNF-05, RNF-10)."""

import asyncio
import hashlib
from collections.abc import AsyncIterator
from datetime import datetime, time
from typing import Any
from uuid import UUID

import asyncpg
import httpx
import pytest

from app.core.config import get_settings
from app.core.db import Conexion, Pool, crear_pool
from app.core.eventos import escuchar
from app.core.limites import LimitePorIP
from app.domains import agenda
from app.domains.agenda.routes.public import limite_reservas
from app.main import app

pytestmark = pytest.mark.integracion

type Con = "asyncpg.Connection[asyncpg.Record]"

NORTE = UUID("00000000-0000-4000-8000-00000000b001")
CARLOS = UUID("00000000-0000-4000-8000-00000000a001")
CORTE = UUID("00000000-0000-4000-8000-00000000c001")  # 30 min, $25.000


async def _turno_libre(cliente: httpx.AsyncClient, con: Conexion, slug: str = "barberia-norte", **ids: UUID) -> str:
    fecha = await con.fetchval("select (now() at time zone 'America/Bogota')::date + 7")
    servicio, miembro = ids.get("servicio", CORTE), ids.get("miembro", CARLOS)
    consulta = {"servicio": str(servicio), "miembro": str(miembro), "fecha": str(fecha)}
    turnos = (await cliente.get(f"/public/barberias/{slug}/turnos", params=consulta)).json()
    assert turnos, "el seed debería tener turnos libres en una semana"
    inicio: str = turnos[0]["inicio"]
    return inicio


def _reserva(inicio: str, **cambios: Any) -> dict[str, Any]:
    return {
        "slug": "barberia-norte",
        "servicio_id": str(CORTE),
        "miembro_id": str(CARLOS),
        "inicio": inicio,
        "nombre": "Juan Pérez",
        "telefono": "300 123 4567",
        "acepta_politica": True,
        "acepta_marketing": False,
    } | cambios


async def test_crea_la_cita_y_devuelve_el_token_una_sola_vez(cliente: httpx.AsyncClient, con: Con) -> None:
    inicio = await _turno_libre(cliente, con)

    respuesta = await cliente.post("/public/citas", json=_reserva(inicio))

    assert respuesta.status_code == 201, respuesta.text
    token = respuesta.json()["token"]
    assert len(token) >= 43  # 32 bytes aleatorios
    cita = await con.fetchrow("select * from citas where token_hash = $1", hashlib.sha256(token.encode()).hexdigest())
    assert cita is not None  # RNF-10: solo se guarda el hash
    assert (cita["estado"], cita["origen"], cita["miembro_id"]) == ("pendiente", "web", CARLOS)
    # RN-13: copia del servicio
    assert (cita["servicio_nombre"], cita["duracion_min"], cita["precio_cop"]) == ("Corte", 30, 25000)
    eventos = await con.fetch("select tipo, actor from cita_eventos where cita_id = $1", cita["id"])
    assert [tuple(e) for e in eventos] == [("creada", "cliente")]


async def test_el_turno_reservado_deja_de_ofrecerse(cliente: httpx.AsyncClient, con: Con) -> None:
    inicio = await _turno_libre(cliente, con)
    await cliente.post("/public/citas", json=_reserva(inicio))

    assert await _turno_libre(cliente, con) != inicio


async def test_publica_cita_creada_en_la_misma_transaccion(cliente: httpx.AsyncClient, con: Con) -> None:
    recibidos: list[tuple[UUID, UUID, bool]] = []

    @escuchar(agenda.CitaCreada)
    async def oyente(con_evento: Con, evento: agenda.CitaCreada) -> None:
        existe = await con_evento.fetchval("select exists(select 1 from citas where id = $1)", evento.cita_id)
        recibidos.append((evento.cita_id, evento.barberia_id, existe))

    await cliente.post("/public/citas", json=_reserva(await _turno_libre(cliente, con)))

    assert len(recibidos) == 1
    assert recibidos[0][1:] == (NORTE, True)


async def test_un_turno_ocupado_o_fuera_de_la_grilla_responde_409(cliente: httpx.AsyncClient, con: Con) -> None:
    inicio = await _turno_libre(cliente, con)
    await cliente.post("/public/citas", json=_reserva(inicio))

    otra = await cliente.post("/public/citas", json=_reserva(inicio, telefono="3110000000"))
    fuera = await cliente.post("/public/citas", json=_reserva(inicio.replace(":00", ":07", 1), telefono="3110000000"))

    for respuesta in (otra, fuera):
        assert respuesta.status_code == 409
        assert respuesta.json()["codigo"] == "turno_ocupado"
        assert respuesta.json()["mensaje"] == "Ese horario se acaba de ocupar."


async def test_un_servicio_que_el_barbero_no_presta_o_de_otra_barberia_responde_409(
    cliente: httpx.AsyncClient, con: Con
) -> None:
    inicio = await _turno_libre(cliente, con)
    await con.execute("delete from miembro_servicios where miembro_id = $1 and servicio_id = $2", CARLOS, CORTE)
    otra = await con.fetchval(
        "insert into barberias (nombre, slug, direccion) values ('Otra', 'otra', 'Cra 1') returning id"
    )
    ajeno = await con.fetchval(
        "insert into servicios (barberia_id, nombre, duracion_min, precio_cop)"
        " values ($1, 'Tinte', 30, 1) returning id",
        otra,
    )

    for servicio in (CORTE, ajeno):
        respuesta = await cliente.post("/public/citas", json=_reserva(inicio, servicio_id=str(servicio)))
        assert respuesta.status_code == 409
        assert respuesta.json()["codigo"] == "seleccion_no_disponible"


async def test_un_telefono_invalido_responde_422(cliente: httpx.AsyncClient, con: Con) -> None:
    respuesta = await cliente.post("/public/citas", json=_reserva(await _turno_libre(cliente, con), telefono="12345"))

    assert respuesta.status_code == 422
    assert respuesta.json()["codigo"] == "telefono_invalido"


async def test_sin_aceptar_la_politica_no_reserva(cliente: httpx.AsyncClient, con: Con) -> None:
    # RF-06: la casilla es obligatoria.
    respuesta = await cliente.post(
        "/public/citas", json=_reserva(await _turno_libre(cliente, con), acepta_politica=False)
    )

    assert respuesta.status_code == 422


async def test_el_maximo_de_citas_futuras_no_muestra_detalles(cliente: httpx.AsyncClient, con: Con) -> None:
    # RN-11: 2 por cliente en el seed. CU-01 9b: dice cuántas tiene, sin mostrar cuáles.
    for _ in range(2):
        creada = await cliente.post("/public/citas", json=_reserva(await _turno_libre(cliente, con)))
        assert creada.status_code == 201

    respuesta = await cliente.post("/public/citas", json=_reserva(await _turno_libre(cliente, con)))

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "codigo": "maximo_citas",
        "mensaje": "Ya tienes 2 citas próximas en esta barbería. Revisa tu WhatsApp para gestionarlas.",
        "datos": {"citas": 2},
    }


async def test_una_barberia_suspendida_no_acepta_reservas(cliente: httpx.AsyncClient, con: Con) -> None:
    inicio = await _turno_libre(cliente, con)
    await con.execute("update barberias set estado = 'suspendida' where id = $1", NORTE)

    respuesta = await cliente.post("/public/citas", json=_reserva(inicio))

    assert respuesta.status_code == 404


async def test_la_sexta_reserva_de_una_ip_en_una_hora_responde_429(cliente: httpx.AsyncClient, con: Con) -> None:
    # F1.06. Solo cuentan las reservas que se guardan: el 422 del principio no gasta cupo.
    app.dependency_overrides[limite_reservas] = LimitePorIP(5, 3600)
    estados = [(await cliente.post("/public/citas", json={})).status_code]
    for n in range(6):
        cuerpo = _reserva(await _turno_libre(cliente, con), telefono=f"31000000{n:02d}")  # RN-11: 2 por cliente
        estados.append((await cliente.post("/public/citas", json=cuerpo)).status_code)

    assert estados == [422] + [201] * 5 + [429]
    assert (await cliente.post("/public/citas", json=cuerpo)).json()["codigo"] == "demasiadas_solicitudes"


# Concurrencia: dos transacciones reales que se confirman, así que aquí no sirve la fixture `con`.


@pytest.fixture
async def pool() -> AsyncIterator[Pool]:
    pool = await crear_pool(get_settings().database_url)
    app.state.pool = pool
    app.dependency_overrides[limite_reservas] = lambda: None
    try:
        yield pool
    finally:
        app.dependency_overrides.clear()
        del app.state.pool
        await pool.close()


@pytest.fixture
async def barberia_real(pool: Pool) -> AsyncIterator[dict[str, UUID]]:
    """Una barbería confirmada en la base con un barbero que atiende todos los días; se borra al terminar."""
    async with pool.acquire() as con:
        barberia = await con.fetchval(
            "insert into barberias (nombre, slug, direccion) values ('Carrera', 'carrera', 'Cra 1') returning id"
        )
        try:
            servicio = await con.fetchval(
                "insert into servicios (barberia_id, nombre, duracion_min, precio_cop) values ($1, 'Corte', 30, 1)"
                " returning id",
                barberia,
            )
            miembro = await con.fetchval(
                "insert into miembros (barberia_id, nombre) values ($1, 'Rápido') returning id", barberia
            )
            await con.execute(
                "insert into miembro_servicios (barberia_id, miembro_id, servicio_id) values ($1, $2, $3)",
                barberia,
                miembro,
                servicio,
            )
            await con.executemany(
                "insert into horarios (barberia_id, miembro_id, dia_semana, hora_inicio, hora_fin)"
                " values ($1, $2, $3, $4, $5)",
                [(barberia, miembro, dia, time(8), time(20)) for dia in range(1, 8)],
            )
            yield {"barberia": barberia, "servicio": servicio, "miembro": miembro}
        finally:
            await con.execute("delete from barberias where id = $1", barberia)


async def test_dos_reservas_simultaneas_al_mismo_turno_solo_una_gana(
    pool: Pool, barberia_real: dict[str, UUID]
) -> None:
    # RNF-05 (criterio de F1.05): exactamente un 201 y un 409.
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cliente:
        async with pool.acquire() as con:
            inicio = await _turno_libre(
                cliente, con, "carrera", servicio=barberia_real["servicio"], miembro=barberia_real["miembro"]
            )
        cuerpo = _reserva(
            inicio, slug="carrera", servicio_id=str(barberia_real["servicio"]), miembro_id=str(barberia_real["miembro"])
        )

        respuestas = await asyncio.gather(
            cliente.post("/public/citas", json=cuerpo),
            cliente.post("/public/citas", json=cuerpo | {"telefono": "3110000000"}),
        )

    assert sorted(r.status_code for r in respuestas) == [201, 409]


async def test_si_otro_toma_el_turno_despues_de_validarlo_responde_409(
    pool: Pool, barberia_real: dict[str, UUID]
) -> None:
    # Doc 04 §5.1: la validación no ve una reserva sin confirmar; la exclusión `citas_sin_solape` (23P01) sí.
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as cliente:
        async with pool.acquire() as otro:
            inicio = await _turno_libre(
                cliente, otro, "carrera", servicio=barberia_real["servicio"], miembro=barberia_real["miembro"]
            )
            transaccion = otro.transaction()
            await transaccion.start()
            cliente_id = await otro.fetchval(
                "insert into clientes (barberia_id, nombre, telefono_e164)"
                " values ($1, 'Otro', '+573120000000') returning id",
                barberia_real["barberia"],
            )
            await otro.execute(
                """
                insert into citas (barberia_id, miembro_id, servicio_id, cliente_id, inicio, fin,
                                   servicio_nombre, duracion_min, precio_cop, token_hash)
                values ($1, $2, $3, $4, $5::timestamptz, $5::timestamptz + interval '30 minutes', 'Corte', 30, 1, 'x')
                """,
                barberia_real["barberia"],
                barberia_real["miembro"],
                barberia_real["servicio"],
                cliente_id,
                datetime.fromisoformat(inicio),
            )
            cuerpo = _reserva(
                inicio,
                slug="carrera",
                servicio_id=str(barberia_real["servicio"]),
                miembro_id=str(barberia_real["miembro"]),
            )
            reserva = asyncio.create_task(cliente.post("/public/citas", json=cuerpo))
            # Espera a que la reserva quede bloqueada por la fila sin confirmar y entonces confirma la otra.
            for _ in range(100):
                if await otro.fetchval("select count(*) from pg_stat_activity where wait_event_type = 'Lock'"):
                    break
                await asyncio.sleep(0.05)
            await transaccion.commit()
            respuesta = await reserva

    assert respuesta.status_code == 409
    assert respuesta.json()["codigo"] == "turno_ocupado"
