from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.db import crear_pool
from app.core.errores import ErrorDominio, registrar_errores
from app.core.logs import configurar_logs, registrar_peticiones
from app.domains.agenda.routes import public as agenda_public

configurar_logs()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.pool = await crear_pool(settings.database_url)
    yield
    await app.state.pool.close()


app = FastAPI(title="Turnero API", lifespan=lifespan)
registrar_errores(app)
# Antes que CORS, para que CORS envuelva también el 500 genérico.
registrar_peticiones(app)

# Solo el dominio de la web puede llamar a la API desde el navegador.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.web_origin],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],  # para que la web pueda citarlo al reportar un error
)

app.include_router(agenda_public.router)


@app.get("/health")
async def health(request: Request) -> dict[str, str]:
    try:
        async with request.app.state.pool.acquire() as con:
            await con.fetchval("select 1")
    except (OSError, asyncpg.PostgresError) as error:
        raise ErrorDominio(503, "base_no_disponible", "Base de datos no disponible") from error
    return {"estado": "ok"}
