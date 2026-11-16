from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errores import ErrorDominio, registrar_errores


class _TurnoOcupado(ErrorDominio):
    def __init__(self) -> None:
        super().__init__(409, "turno_ocupado", "Ese horario se acaba de ocupar")


def _cliente() -> TestClient:
    app = FastAPI()
    registrar_errores(app)

    @app.get("/ocupado")
    async def ocupado() -> None:
        raise _TurnoOcupado()

    @app.get("/maximo")
    async def maximo() -> None:
        raise ErrorDominio(409, "maximo_citas", "Ya tienes el máximo de citas", {"citas_futuras": 2})

    return TestClient(app)


def test_un_error_de_dominio_responde_su_status_codigo_y_mensaje() -> None:
    respuesta = _cliente().get("/ocupado")

    assert respuesta.status_code == 409
    assert respuesta.json() == {"codigo": "turno_ocupado", "mensaje": "Ese horario se acaba de ocupar"}


def test_un_error_de_dominio_con_datos_los_incluye() -> None:
    # CU-01 9b: la web muestra cuántas citas tiene, sin detalles.
    respuesta = _cliente().get("/maximo")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "codigo": "maximo_citas",
        "mensaje": "Ya tienes el máximo de citas",
        "datos": {"citas_futuras": 2},
    }
