"""Fixtures de las pruebas de la agenda."""

from collections.abc import AsyncIterator

import asyncpg
import httpx
import pytest

from app.core.db import conexion_servicio
from app.domains.agenda.routes.public import limite_reservas
from app.main import app


@pytest.fixture
async def cliente(con: "asyncpg.Connection[asyncpg.Record]") -> AsyncIterator[httpx.AsyncClient]:
    # La ruta usa la misma transacción de la prueba, así lo que inserta la prueba se deshace al final.
    app.dependency_overrides[conexion_servicio] = lambda: con
    app.dependency_overrides[limite_reservas] = lambda: None  # todas salen de la misma IP; F1.06 se prueba aparte
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
            yield c
    finally:
        app.dependency_overrides.clear()
