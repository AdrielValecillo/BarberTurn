"""F1.06 · Límite por IP (RN-11: 5 reservas por hora). Solo cuentan las solicitudes que salen bien."""

from contextlib import asynccontextmanager

import pytest
from starlette.requests import Request

from app.core.errores import ErrorDominio
from app.core.limites import LimitePorIP


class Reloj:
    def __init__(self) -> None:
        self.ahora = 1000.0

    def __call__(self) -> float:
        return self.ahora


def peticion(ip: str = "10.0.0.1", reenviada: str | None = None) -> Request:
    headers = [(b"x-forwarded-for", reenviada.encode())] if reenviada else []
    return Request({"type": "http", "headers": headers, "client": (ip, 1234)})


async def reservar(limite: LimitePorIP, request: Request, sale_bien: bool = True) -> None:
    """Como la usa FastAPI: entra antes del endpoint y sale después, con su error si falló."""
    try:
        async with asynccontextmanager(limite)(request):
            if not sale_bien:
                raise ValueError("la reserva falló")
    except ValueError:
        assert not sale_bien


async def test_la_sexta_reserva_en_la_ventana_responde_429() -> None:
    limite = LimitePorIP(5, 3600, reloj=Reloj())
    for _ in range(5):
        await reservar(limite, peticion())

    with pytest.raises(ErrorDominio) as error:
        await reservar(limite, peticion())
    assert error.value.status == 429


async def test_los_intentos_que_fallan_no_cuentan() -> None:
    # Un teléfono mal escrito o un turno que se acaba de ocupar (CU-01 8a, 9a) no gastan el cupo.
    limite = LimitePorIP(1, 3600, reloj=Reloj())
    for _ in range(3):
        await reservar(limite, peticion(), sale_bien=False)

    await reservar(limite, peticion())


async def test_cada_ip_lleva_su_propia_cuenta() -> None:
    limite = LimitePorIP(1, 3600, reloj=Reloj())
    await reservar(limite, peticion("10.0.0.1"))
    await reservar(limite, peticion("10.0.0.2"))


async def test_pasada_la_ventana_vuelve_a_aceptar() -> None:
    reloj = Reloj()
    limite = LimitePorIP(1, 3600, reloj=reloj)
    await reservar(limite, peticion())

    reloj.ahora += 3600
    await reservar(limite, peticion())


async def test_detras_del_proxy_cuenta_la_ip_que_agrega_el_proxy() -> None:
    # El cliente puede inventar el principio de X-Forwarded-For, no el final (lo agrega el proxy de Railway).
    limite = LimitePorIP(1, 3600, reloj=Reloj())
    await reservar(limite, peticion("100.64.0.1", reenviada="1.1.1.1, 200.1.1.1"))

    with pytest.raises(ErrorDominio):
        await reservar(limite, peticion("100.64.0.1", reenviada="9.9.9.9, 200.1.1.1"))
    await reservar(limite, peticion("100.64.0.1", reenviada="200.2.2.2"))
