"""F1.02 · clientes.registrar: alta por (barbería, teléfono) y consentimientos (RF-06, RF-07, RN-10)."""

from uuid import UUID

import asyncpg
import pytest

from app.domains.clientes import service as clientes

pytestmark = pytest.mark.integracion

type Con = "asyncpg.Connection[asyncpg.Record]"

NORTE = UUID("00000000-0000-4000-8000-00000000b001")


async def _otra_barberia(con: Con) -> UUID:
    otra: UUID = await con.fetchval(
        "insert into barberias (nombre, slug, direccion) values ('Otra', 'otra', 'Cra 1') returning id"
    )
    return otra


@pytest.mark.parametrize("escrito", ["300 123 4567", "+57 300-123-4567", "(300) 1234567", "573001234567"])
async def test_normaliza_el_telefono_y_reutiliza_al_cliente(con: Con, escrito: str) -> None:
    primero = await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=False)
    segundo = await clientes.registrar(con, NORTE, "Juan", escrito, marketing=False)

    assert segundo == primero
    assert await con.fetchval("select telefono_e164 from clientes where id = $1", primero) == "+573001234567"


async def test_el_nombre_queda_con_el_ultimo_usado(con: Con) -> None:
    cliente = await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=False)
    await clientes.registrar(con, NORTE, "Juan Pérez", "3001234567", marketing=False)

    assert await con.fetchval("select nombre from clientes where id = $1", cliente) == "Juan Pérez"


async def test_el_mismo_numero_en_dos_barberias_son_dos_clientes(con: Con) -> None:
    otra = await _otra_barberia(con)

    en_norte = await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=False)
    en_otra = await clientes.registrar(con, otra, "Juan", "3001234567", marketing=False)

    assert en_norte != en_otra


async def test_un_telefono_invalido_no_registra_nada(con: Con) -> None:
    with pytest.raises(clientes.TelefonoInvalido):
        await clientes.registrar(con, NORTE, "Juan", "12345", marketing=False)


async def test_guarda_la_autorizacion_de_datos_con_la_version_del_texto(con: Con) -> None:
    cliente = await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=False)

    filas = await con.fetch(
        "select tipo, otorgado, version_texto, origen from consentimientos where cliente_id = $1", cliente
    )
    assert [dict(f) for f in filas] == [
        {"tipo": "tratamiento_datos", "otorgado": True, "version_texto": clientes.VERSION_POLITICA, "origen": "web"}
    ]
    assert await con.fetchval("select acepta_marketing from clientes where id = $1", cliente) is False


async def test_la_casilla_de_marketing_marcada_se_guarda(con: Con) -> None:
    cliente = await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=True)

    tipos = await con.fetch("select tipo from consentimientos where cliente_id = $1 and otorgado", cliente)
    assert sorted(f["tipo"] for f in tipos) == ["mensajes_marketing", "tratamiento_datos"]
    assert await con.fetchval("select acepta_marketing from clientes where id = $1", cliente) is True


async def test_no_marcar_marketing_en_otra_reserva_no_lo_retira(con: Con) -> None:
    # RF-07: la casilla va desmarcada por defecto; dejarla así no es retirar lo que aceptó antes (RN-12).
    cliente = await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=True)
    await clientes.registrar(con, NORTE, "Juan", "3001234567", marketing=False)

    assert await con.fetchval("select acepta_marketing from clientes where id = $1", cliente) is True
