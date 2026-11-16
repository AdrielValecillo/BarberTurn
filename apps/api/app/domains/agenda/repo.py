"""SQL de las tablas de la agenda: `citas` y `cita_eventos` (y más adelante `horarios` y `bloqueos`)."""

from datetime import datetime
from uuid import UUID

import asyncpg

from app.core.db import Conexion


async def citas_futuras(con: Conexion, barberia_id: UUID, cliente_id: UUID) -> int:
    """Citas activas por venir del cliente en la barbería (RN-11)."""
    n: int = await con.fetchval(
        """
        select count(*) from citas
        where barberia_id = $1 and cliente_id = $2 and estado in ('pendiente', 'confirmada') and inicio > now()
        """,
        barberia_id,
        cliente_id,
    )
    return n


async def insertar_cita(
    con: Conexion,
    *,
    barberia_id: UUID,
    miembro_id: UUID,
    cliente_id: UUID,
    servicio: asyncpg.Record,
    inicio: datetime,
    token_hash: str,
) -> UUID:
    """Inserta la cita con la copia del servicio (RN-13). Un cruce lanza `ExclusionViolationError` (23P01)."""
    cita_id: UUID = await con.fetchval(
        """
        insert into citas (barberia_id, miembro_id, servicio_id, cliente_id, inicio, fin,
                           servicio_nombre, duracion_min, precio_cop, token_hash)
        values ($1, $2, $3, $4, $5::timestamptz, $5::timestamptz + make_interval(mins => $7), $6, $7, $8, $9)
        returning id
        """,
        barberia_id,
        miembro_id,
        servicio["id"],
        cliente_id,
        inicio,
        servicio["nombre"],
        servicio["duracion_min"],
        servicio["precio_cop"],
        token_hash,
    )
    return cita_id


async def registrar_evento(con: Conexion, barberia_id: UUID, cita_id: UUID, tipo: str, actor: str) -> None:
    await con.execute(
        "insert into cita_eventos (barberia_id, cita_id, tipo, actor) values ($1, $2, $3, $4)",
        barberia_id,
        cita_id,
        tipo,
        actor,
    )


async def turno_libre(con: Conexion, miembro_id: UUID, inicio: datetime, duracion_min: int, zona: str) -> bool:
    """¿`inicio` está entre los turnos de `turnos_disponibles()`? (grilla, horario, anticipación, solapes)."""
    libre: bool = await con.fetchval(
        """
        select exists(
          select 1 from turnos_disponibles($1, ($2::timestamptz at time zone $4)::date, $3) t where t.inicio = $2
        )
        """,
        miembro_id,
        inicio,
        duracion_min,
        zona,
    )
    return libre
