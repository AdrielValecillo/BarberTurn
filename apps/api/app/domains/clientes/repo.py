"""SQL de las tablas de clientes: `clientes` y `consentimientos`."""

from uuid import UUID

from app.core.db import Conexion


async def guardar_cliente(con: Conexion, barberia_id: UUID, nombre: str, telefono_e164: str, marketing: bool) -> UUID:
    """Alta o actualización por (barbería, teléfono): el nombre queda con el último usado (RN-10).

    `acepta_marketing` solo pasa a true aquí; retirarlo es otro flujo (RN-12).
    """
    cliente_id: UUID = await con.fetchval(
        """
        insert into clientes (barberia_id, nombre, telefono_e164, acepta_marketing)
        values ($1, $2, $3, $4)
        on conflict (barberia_id, telefono_e164) do update
          set nombre = excluded.nombre,
              acepta_marketing = clientes.acepta_marketing or excluded.acepta_marketing
        returning id
        """,
        barberia_id,
        nombre,
        telefono_e164,
        marketing,
    )
    return cliente_id


async def guardar_consentimientos(
    con: Conexion, barberia_id: UUID, cliente_id: UUID, tipos: list[str], version: str, origen: str
) -> None:
    await con.executemany(
        """
        insert into consentimientos (barberia_id, cliente_id, tipo, otorgado, version_texto, origen)
        values ($1, $2, $3, true, $4, $5)
        """,
        [(barberia_id, cliente_id, tipo, version, origen) for tipo in tipos],
    )
