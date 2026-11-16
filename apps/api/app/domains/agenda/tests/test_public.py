"""F1.01 · GET /public/barberias/{slug} contra el seed (RF-01, RF-03, RN-16, CU-01)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import asyncpg
import httpx
import pytest

pytestmark = pytest.mark.integracion

type Con = "asyncpg.Connection[asyncpg.Record]"

# IDs del seed
NORTE = UUID("00000000-0000-4000-8000-00000000b001")
CARLOS = UUID("00000000-0000-4000-8000-00000000a001")
ANDRES = UUID("00000000-0000-4000-8000-00000000a002")
CORTE = UUID("00000000-0000-4000-8000-00000000c001")  # 30 min
BARBA = UUID("00000000-0000-4000-8000-00000000c002")  # 20 min
CORTE_Y_BARBA = UUID("00000000-0000-4000-8000-00000000c003")


async def test_devuelve_la_barberia_del_seed_con_servicios_y_barberos_en_orden(cliente: httpx.AsyncClient) -> None:
    respuesta = await cliente.get("/public/barberias/barberia-norte")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["slug"] == "barberia-norte"
    assert cuerpo["nombre"] == "Barbería Norte"
    assert cuerpo["direccion"] == "Calle 85 #15-20, Bogotá"
    assert cuerpo["zona"] == "America/Bogota"
    assert cuerpo["telefono_contacto"] == "+573001112233"  # CU-01 5a: contacto si no hay turnos
    assert cuerpo["servicios"] == [
        {"id": str(CORTE), "nombre": "Corte", "duracion_min": 30, "precio_cop": 25000},
        {"id": str(BARBA), "nombre": "Barba", "duracion_min": 20, "precio_cop": 15000},
        {"id": str(CORTE_Y_BARBA), "nombre": "Corte + barba", "duracion_min": 45, "precio_cop": 35000},
    ]
    assert [b["nombre"] for b in cuerpo["barberos"]] == ["Carlos", "Andrés"]


async def test_un_slug_nunca_devuelve_datos_de_otra_barberia(cliente: httpx.AsyncClient, con: Con) -> None:
    # RNF-08, ADR-0008: /public/* salta la RLS, así que el filtro por barbería lo hace la consulta.
    otra = await con.fetchval(
        "insert into barberias (nombre, slug, direccion) values ('Otra', 'otra', 'Cra 1') returning id"
    )
    servicio = await con.fetchval(
        "insert into servicios (barberia_id, nombre, duracion_min, precio_cop) values ($1, 'Tinte', 60, 50000)"
        " returning id",
        otra,
    )
    miembro = await con.fetchval(
        "insert into miembros (barberia_id, nombre) values ($1, 'Pedro') returning id",
        otra,
    )
    await con.execute(
        "insert into miembro_servicios (barberia_id, miembro_id, servicio_id) values ($1, $2, $3)",
        otra,
        miembro,
        servicio,
    )

    norte = (await cliente.get("/public/barberias/barberia-norte")).json()
    de_otra = (await cliente.get("/public/barberias/otra")).json()

    assert str(servicio) not in [s["id"] for s in norte["servicios"]]
    assert str(miembro) not in [b["id"] for b in norte["barberos"]]
    assert [s["nombre"] for s in de_otra["servicios"]] == ["Tinte"]
    assert [b["nombre"] for b in de_otra["barberos"]] == ["Pedro"]


async def test_omite_servicios_inactivos_y_miembros_que_no_atienden(cliente: httpx.AsyncClient, con: Con) -> None:
    await con.execute("update servicios set activo = false where nombre = 'Barba'")
    await con.execute("update miembros set atiende = false where nombre = 'Carlos'")
    await con.execute("insert into miembros (barberia_id, nombre, activo) values ($1, 'Inactivo', false)", NORTE)

    cuerpo = (await cliente.get("/public/barberias/barberia-norte")).json()

    assert [s["nombre"] for s in cuerpo["servicios"]] == ["Corte", "Corte + barba"]
    assert [b["nombre"] for b in cuerpo["barberos"]] == ["Andrés"]


async def _proximos(cliente: httpx.AsyncClient, consulta: str = "") -> dict[str, datetime | None]:
    barberos = (await cliente.get(f"/public/barberias/barberia-norte{consulta}")).json()["barberos"]
    return {b["nombre"]: b["proximo_turno"] and datetime.fromisoformat(b["proximo_turno"]) for b in barberos}


async def _bloquear(con: Con, miembro: UUID, inicio: datetime, fin: datetime) -> None:
    sql = "insert into bloqueos (barberia_id, miembro_id, inicio, fin) values ($1, $2, $3, $4)"
    await con.execute(sql, NORTE, miembro, inicio, fin)


async def test_el_proximo_turno_respeta_anticipacion_grilla_y_horario(cliente: httpx.AsyncClient, con: Con) -> None:
    # RF-03 con las reglas del seed: 60 min de anticipación (RN-04), grilla de 15 (RN-03), sin domingos.
    turno = (await _proximos(cliente))["Carlos"]

    assert turno is not None
    assert turno >= await con.fetchval("select now() + interval '60 minutes'")
    local = await con.fetchval("select $1::timestamptz at time zone 'America/Bogota'", turno)
    assert local.minute % 15 == 0
    assert local.isoweekday() != 7


async def test_el_proximo_turno_salta_lo_ocupado(cliente: httpx.AsyncClient, con: Con) -> None:
    # RN-02: si se bloquea hasta media hora después del próximo turno, el nuevo queda después del bloqueo.
    antes = (await _proximos(cliente))["Carlos"]
    assert antes is not None
    await _bloquear(con, CARLOS, datetime.now(UTC), antes + timedelta(minutes=30))

    despues = (await _proximos(cliente))["Carlos"]

    assert despues is not None
    assert despues >= antes + timedelta(minutes=30)


async def test_sin_turnos_en_toda_la_ventana_el_proximo_turno_es_nulo(cliente: httpx.AsyncClient, con: Con) -> None:
    await _bloquear(con, ANDRES, datetime.now(UTC), datetime.now(UTC) + timedelta(days=200))

    assert (await _proximos(cliente))["Andrés"] is None


async def test_con_servicio_solo_lista_a_quienes_lo_prestan(cliente: httpx.AsyncClient, con: Con) -> None:
    # RF-03: el cliente elige entre los barberos que prestan el servicio.
    await con.execute("delete from miembro_servicios where miembro_id = $1 and servicio_id = $2", ANDRES, CORTE)

    assert list(await _proximos(cliente, f"?servicio={CORTE}")) == ["Carlos"]


async def test_sin_servicio_omite_a_quien_no_presta_ningun_servicio_activo(
    cliente: httpx.AsyncClient, con: Con
) -> None:
    await con.execute("delete from miembro_servicios where miembro_id = $1", ANDRES)

    assert list(await _proximos(cliente)) == ["Carlos"]


async def test_con_servicio_el_proximo_turno_es_uno_donde_cabe_completo(cliente: httpx.AsyncClient, con: Con) -> None:
    # Se deja libre solo [turno, turno + 20 min): cabe la barba (20 min) y no el corte (30 min).
    turno = (await _proximos(cliente, f"?servicio={BARBA}"))["Carlos"]
    assert turno is not None
    await _bloquear(con, CARLOS, turno - timedelta(days=1), turno)
    await _bloquear(con, CARLOS, turno + timedelta(minutes=20), turno + timedelta(days=200))

    assert (await _proximos(cliente, f"?servicio={BARBA}"))["Carlos"] == turno
    assert (await _proximos(cliente, f"?servicio={CORTE}"))["Carlos"] is None


async def test_un_slug_inexistente_responde_no_disponible(cliente: httpx.AsyncClient) -> None:
    respuesta = await cliente.get("/public/barberias/no-existe")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "barberia_no_disponible"


async def test_una_barberia_suspendida_responde_no_disponible(cliente: httpx.AsyncClient, con: Con) -> None:
    # RN-16
    await con.execute("update barberias set estado = 'suspendida' where slug = 'barberia-norte'")

    respuesta = await cliente.get("/public/barberias/barberia-norte")

    assert respuesta.status_code == 404
    assert respuesta.json()["codigo"] == "barberia_no_disponible"
