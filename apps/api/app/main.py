from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import crear_pool

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.pool = await crear_pool(settings.database_url)
    yield
    await app.state.pool.close()


app = FastAPI(title="Turnero API", lifespan=lifespan)

# Solo el dominio de la web puede llamar a la API desde el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    try:
        async with request.app.state.pool.acquire() as con:
            await con.fetchval("select 1")
    except (OSError, asyncpg.PostgresError) as error:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from error
    return {"estado": "ok"}
