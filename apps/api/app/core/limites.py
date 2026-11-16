"""Límite de solicitudes por IP contra abuso (RN-11, F1.06). Se usa como dependencia de FastAPI."""

import time
from collections.abc import AsyncIterator, Callable

from fastapi import Request

from app.core.errores import ErrorDominio


def ip_cliente(request: Request) -> str:
    """La IP que vio el proxy de Railway: el último valor de X-Forwarded-For (el cliente puede inventar los demás).

    shortcut: supone un solo proxy delante de la API (Railway); con un CDN delante habría que saltar sus IPs.
    """
    reenviada = request.headers.get("x-forwarded-for")
    if reenviada:
        return reenviada.rsplit(",", 1)[-1].strip()
    return request.client.host if request.client else "desconocida"


class LimitePorIP:
    """Ventana deslizante en memoria: `maximo` solicitudes que salen bien cada `ventana_s` segundos por IP.

    Es una dependencia con `yield`: revisa antes del endpoint y cuenta al salir, solo si no hubo error
    (un teléfono mal escrito o un turno recién ocupado no gastan el cupo). Úsala con `scope="function"`
    para que cuente después del commit y no después de enviar la respuesta.

    shortcut: en memoria, sirve con una sola instancia de la API; si se escala a varias, mover la cuenta a la base.
    """

    def __init__(self, maximo: int, ventana_s: float, reloj: Callable[[], float] = time.monotonic) -> None:
        self._maximo = maximo
        self._ventana = ventana_s
        self._reloj = reloj
        self._registros: dict[str, list[float]] = {}

    def _recientes(self, ip: str, ahora: float) -> list[float]:
        return [t for t in self._registros.get(ip, []) if ahora - t < self._ventana]

    async def __call__(self, request: Request) -> AsyncIterator[None]:
        ip = ip_cliente(request)
        ahora = self._reloj()
        if len(self._registros) > 10_000:  # que las IP que no vuelven no crezcan sin fin
            self._registros = {k: v for k, v in self._registros.items() if ahora - v[-1] < self._ventana}
        if len(self._recientes(ip, ahora)) >= self._maximo:
            raise ErrorDominio(429, "demasiadas_solicitudes", "Hiciste muchas reservas seguidas. Intenta más tarde.")
        yield  # si el endpoint falla, la excepción sale aquí y no se cuenta
        self._registros[ip] = [*self._recientes(ip, ahora), ahora]
