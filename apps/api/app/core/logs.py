"""Logs JSON con ID de petición y teléfonos enmascarados (doc 03 §7.2 y §11, F0.07)."""

import json
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response

from app.core.errores import ERROR_INTERNO, respuesta

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

_ID_VALIDO = re.compile(r"[A-Za-z0-9_-]{1,64}")
_log_peticion = logging.getLogger("app.peticion")
_log_errores = logging.getLogger("app.errores")

# [0-9] y no \d: en Python \d acepta dígitos Unicode (igual que en shared/telefono.py).
# El "+" es opcional porque Meta manda `wa_id` sin él; sin letras ni dígitos alrededor, para no tocar IDs.
_TELEFONO = re.compile(r"(?<![0-9A-Za-z])(\+?)([0-9]{10,15})(?![0-9A-Za-z])")
# Campos propios de LogRecord (y el `color_message` de uvicorn): todo lo demás es un `extra=` y va al JSON.
_CAMPOS_DEL_REGISTRO = set(logging.makeLogRecord({}).__dict__) | {"message", "asctime", "color_message"}


def enmascarar(texto: str) -> str:
    """`+573001234567` → `+57300***4567` (y `573001234567` → `57300***4567`) en cualquier parte del texto."""
    return _TELEFONO.sub(lambda m: f"{m[1]}{m[2][:5]}***{m[2][-4:]}", texto)


class FormatoJSON(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        datos: dict[str, object] = {
            "momento": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "nivel": record.levelname,
            "logger": record.name,
            "mensaje": record.getMessage(),
            "request_id": request_id.get(),
        }
        datos.update({k: v for k, v in record.__dict__.items() if k not in _CAMPOS_DEL_REGISTRO})
        if record.exc_info:
            datos["error"] = self.formatException(record.exc_info)
        # Se enmascara la línea ya armada: cubre mensaje, campos extra y tracebacks.
        return enmascarar(json.dumps(datos, ensure_ascii=False, default=str))


def configurar_logs() -> None:
    """Todo a stdout en JSON, nivel INFO. La llaman `main.py` y `worker.py` al arrancar."""
    handler = logging.StreamHandler()
    handler.setFormatter(FormatoJSON())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    # uvicorn trae sus propios handlers: que pasen por el raíz (JSON). Su access log imprime la ruta real
    # con el token de gestión; la línea por petición la escribe `registrar_peticiones` con la plantilla.
    for nombre in ("uvicorn", "uvicorn.error"):
        logging.getLogger(nombre).handlers.clear()
        logging.getLogger(nombre).propagate = True
    logging.getLogger("uvicorn.access").disabled = True


def registrar_peticiones(app: FastAPI) -> None:
    """Middleware: ID de petición, una línea de log por petición y 500 genérico ante errores no controlados.

    Regístralo antes que CORS: así CORS lo envuelve y el navegador puede leer también el 500.
    """

    @app.middleware("http")
    async def _peticion(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        entrante = request.headers.get("X-Request-ID", "")
        rid = entrante if _ID_VALIDO.fullmatch(entrante) else uuid.uuid4().hex
        marca = request_id.set(rid)
        inicio = time.perf_counter()
        try:
            try:
                salida = await call_next(request)
            except Exception:
                _log_errores.exception("error no controlado")
                salida = respuesta(ERROR_INTERNO)
            # La plantilla (`/public/citas/{token}`), nunca la ruta real: llevaría el token de gestión.
            ruta = getattr(request.scope.get("route"), "path", None)
            _log_peticion.info(
                "peticion",
                extra={
                    "metodo": request.method,
                    "ruta": ruta,
                    "status": salida.status_code,
                    "duracion_ms": round((time.perf_counter() - inicio) * 1000, 1),
                },
            )
            salida.headers["X-Request-ID"] = rid
            return salida
        finally:
            request_id.reset(marca)
