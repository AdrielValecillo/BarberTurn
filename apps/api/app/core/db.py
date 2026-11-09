import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import asyncpg

# `type` se evalúa de forma perezosa: no hace falta que asyncpg sea subscriptable en tiempo de ejecución.
type Pool = asyncpg.Pool[asyncpg.Record]
type Conexion = asyncpg.pool.PoolConnectionProxy[asyncpg.Record]


async def crear_pool(dsn: str) -> Pool:
    return await asyncpg.create_pool(dsn, min_size=1, max_size=10)


@asynccontextmanager
async def transaccion_servicio(pool: Pool) -> AsyncIterator[Conexion]:
    """Conexión de servicio: salta la RLS. Toda consulta debe filtrar por barberia_id (público y admin)."""
    async with pool.acquire() as con, con.transaction():
        yield con


@asynccontextmanager
async def transaccion_panel(pool: Pool, claims: dict[str, Any]) -> AsyncIterator[Conexion]:
    """Transacción con la RLS de la base aplicada al usuario del panel (ADR-0008).

    `claims` son los del JWT de Supabase ya verificado; `auth.uid()` lee el `sub`.
    `set local` y `set_config(..., true)` duran solo la transacción: la conexión vuelve limpia al pool.
    """
    async with pool.acquire() as con, con.transaction():
        await con.execute("set local role authenticated")
        await con.execute("select set_config('request.jwt.claims', $1, true)", json.dumps(claims))
        yield con
