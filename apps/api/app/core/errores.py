"""Errores de dominio y su respuesta HTTP (doc 03 §7.2, F0.07).

Cada dominio define sus errores concretos heredando de `ErrorDominio` (p. ej. `TurnoOcupado` en agenda)
y traduce sus propios errores de Postgres: aquí no hay traducción global de `23P01`.
"""

from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class RespuestaError(BaseModel):
    """Cuerpo de todo error de dominio. La web decide con `codigo`; `mensaje` se puede mostrar tal cual."""

    codigo: str
    mensaje: str
    datos: dict[str, Any] | None = None


class ErrorDominio(Exception):
    def __init__(self, status: int, codigo: str, mensaje: str, datos: dict[str, Any] | None = None) -> None:
        super().__init__(mensaje)
        self.status = status
        self.codigo = codigo
        self.mensaje = mensaje
        self.datos = datos


# Lo que ve el cliente ante cualquier excepción no controlada; el detalle va solo al log.
ERROR_INTERNO = ErrorDominio(500, "error_interno", "Algo salió mal. Intenta de nuevo.")


def respuesta(error: ErrorDominio) -> JSONResponse:
    cuerpo = RespuestaError(codigo=error.codigo, mensaje=error.mensaje, datos=error.datos)
    return JSONResponse(cuerpo.model_dump(exclude_none=True), status_code=error.status)


async def _manejar(_: Request, error: Exception) -> JSONResponse:
    return respuesta(cast(ErrorDominio, error))  # Starlette solo lo llama con ErrorDominio


def registrar_errores(app: FastAPI) -> None:
    app.add_exception_handler(ErrorDominio, _manejar)
