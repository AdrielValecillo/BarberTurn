"""Lecturas para pantallas: pueden unir tablas de los dominios de abajo, solo para leer (doc 11)."""

from uuid import UUID

import asyncpg

from app.core.db import Conexion


async def barberia_activa(con: Conexion, slug: str) -> asyncpg.Record | None:
    """RN-16: una barbería suspendida es como si no existiera para el público."""
    return await con.fetchrow(
        "select id, slug, nombre, direccion, zona_horaria as zona from barberias where slug = $1 and estado = 'activa'",
        slug,
    )


async def servicios_activos(con: Conexion, barberia_id: UUID) -> list[asyncpg.Record]:
    return await con.fetch(
        """
        select id, nombre, duracion_min, precio_cop from servicios
        where barberia_id = $1 and activo
        order by orden, nombre
        """,
        barberia_id,
    )


async def barberos_con_proximo_turno(
    con: Conexion, barberia_id: UUID, servicio_id: UUID | None
) -> list[asyncpg.Record]:
    """Barberos que atienden y prestan algún servicio activo, con su primer turno libre en la ventana (RF-03).

    Con `servicio_id`, solo los que lo prestan y con su duración; sin él, con el servicio más corto
    que presta cada uno (el primer hueco donde cabe algo). El paso 2 de la reserva siempre lo pasa.
    """
    return await con.fetch(
        """
        select m.id, m.nombre,
          (select min(t.inicio)
             from generate_series(0, b.ventana_max_dias) as d,
                  turnos_disponibles(m.id, (now() at time zone b.zona_horaria)::date + d, dur.duracion_min) as t
          ) as proximo_turno
        from miembros m
        join barberias b on b.id = m.barberia_id
        cross join lateral (
          select min(s.duracion_min)::int as duracion_min
          from miembro_servicios ms
          join servicios s on s.barberia_id = ms.barberia_id and s.id = ms.servicio_id
          where ms.miembro_id = m.id and s.activo and ($2::uuid is null or s.id = $2)
        ) dur
        where m.barberia_id = $1 and m.activo and m.atiende and dur.duracion_min is not null
        order by m.orden, m.nombre
        """,
        barberia_id,
        servicio_id,
    )
