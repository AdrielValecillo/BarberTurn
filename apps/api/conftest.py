"""Base de prueba: el Supabase local con las migraciones y el seed (`make dev-db` y `make db-reset`).

Vive en la raíz de apps/api para que lo vean también las pruebas de cada dominio (app/domains/*/tests).
"""

import os
from collections.abc import AsyncIterator

import asyncpg
import pytest

from app.core.config import Settings, get_settings

# `.env` puede apuntar a la nube: las pruebas usan la base local (o la DATABASE_URL del entorno), nunca la de `.env`.
os.environ.setdefault("DATABASE_URL", Settings.model_fields["database_url"].default)


@pytest.fixture
async def con(request: pytest.FixtureRequest) -> AsyncIterator["asyncpg.Connection[asyncpg.Record]"]:
    """Conexión dentro de una transacción que se deshace al terminar: la prueba no deja rastro en la base.

    Sirve para leer el seed y escribir datos propios. No sirve para concurrencia (dos transacciones
    confirmadas a la vez): esa fixture llega con su prueba en F1.05.
    """
    if request.node.get_closest_marker("integracion") is None:
        pytest.fail("Una prueba que usa la base lleva @pytest.mark.integracion (la CI las corre aparte).")
    try:
        conexion = await asyncpg.connect(get_settings().database_url)
    except (OSError, asyncpg.PostgresError) as error:
        pytest.fail(f"No responde la base de prueba; levanta Supabase local con `make dev-db` ({error!r}).")
    try:
        if await conexion.fetchval("select to_regclass('public.citas')") is None:
            pytest.fail("La base no tiene las migraciones; corre `make db-reset`.")
        transaccion = conexion.transaction()
        await transaccion.start()
        try:
            yield conexion
        finally:
            await transaccion.rollback()
    finally:
        await conexion.close()
