"""SQL de las tablas de barberias: `barberias`, `miembros`, `servicios` y `miembro_servicios`."""

from uuid import UUID

import asyncpg

from app.core.db import Conexion


async def servicio_prestado(
    con: Conexion, barberia_id: UUID, servicio_id: UUID, miembro_id: UUID
) -> asyncpg.Record | None:
    """El servicio activo, solo si el barbero (activo y que atiende) lo presta y ambos son de la barbería."""
    return await con.fetchrow(
        """
        select s.id, s.nombre, s.duracion_min, s.precio_cop
        from servicios s
        join miembro_servicios ms on ms.barberia_id = s.barberia_id and ms.servicio_id = s.id
        join miembros m on m.barberia_id = ms.barberia_id and m.id = ms.miembro_id
        where s.barberia_id = $1 and s.id = $2 and m.id = $3 and s.activo and m.activo and m.atiende
        """,
        barberia_id,
        servicio_id,
        miembro_id,
    )
