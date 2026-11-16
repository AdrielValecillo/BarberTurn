import io
import json
import logging
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.logs import FormatoJSON, registrar_peticiones


@pytest.fixture
def salida() -> Iterator[io.StringIO]:
    """Lo que el formateador escribe, como en producción, para todos los loggers."""
    buffer = io.StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(FormatoJSON())
    raiz = logging.getLogger()
    nivel = raiz.level
    raiz.addHandler(handler)
    raiz.setLevel(logging.INFO)
    yield buffer
    raiz.removeHandler(handler)
    raiz.setLevel(nivel)


def _app() -> FastAPI:
    app = FastAPI()
    registrar_peticiones(app)

    @app.get("/public/citas/{token}")
    async def ver(token: str) -> dict[str, str]:
        logging.getLogger("prueba").info("dentro de la ruta")
        return {"ok": token}

    @app.get("/roto")
    async def roto() -> None:
        raise RuntimeError("se cayó con +573001234567")

    return app


def _lineas(salida: io.StringIO) -> list[dict[str, object]]:
    return [json.loads(linea) for linea in salida.getvalue().splitlines()]


def test_cada_registro_es_una_linea_json_con_nivel_mensaje_y_campos_extra(salida: io.StringIO) -> None:
    logging.getLogger("prueba").info("cita creada", extra={"cita_id": "c-1"})

    [linea] = _lineas(salida)
    assert linea["nivel"] == "INFO"
    assert linea["mensaje"] == "cita creada"
    assert linea["cita_id"] == "c-1"
    assert linea["request_id"] is None  # fuera de una petición


def test_los_telefonos_se_enmascaran_en_el_mensaje_y_en_los_campos(salida: io.StringIO) -> None:
    logging.getLogger("prueba").info("enviando a +573001234567", extra={"telefono": "+573109876543"})

    [linea] = _lineas(salida)
    assert linea["mensaje"] == "enviando a +57300***4567"
    assert linea["telefono"] == "+57310***6543"


def test_los_telefonos_sin_mas_tambien_se_enmascaran_pero_no_los_ids(salida: io.StringIO) -> None:
    # Meta manda `wa_id` sin "+" (F3); un ID hexadecimal con dígitos seguidos no es un teléfono.
    logging.getLogger("prueba").info("webhook de 573001234567", extra={"id": "a1234567890123b"})

    [linea] = _lineas(salida)
    assert linea["mensaje"] == "webhook de 57300***4567"
    assert linea["id"] == "a1234567890123b"


def test_los_telefonos_tambien_se_enmascaran_en_el_traceback(salida: io.StringIO) -> None:
    try:
        raise ValueError("teléfono duplicado: +573001234567")
    except ValueError:
        logging.getLogger("prueba").exception("falló el registro")

    [linea] = _lineas(salida)
    assert "+57300***4567" in str(linea["error"])
    assert "+573001234567" not in salida.getvalue()


def _de(salida: io.StringIO, logger: str) -> list[dict[str, object]]:
    return [linea for linea in _lineas(salida) if linea["logger"] == logger]


def _de_la_app(salida: io.StringIO) -> list[dict[str, object]]:
    """Sin las líneas del propio TestClient (httpx/httpx2), que registra la URL completa."""
    return [linea for linea in _lineas(salida) if not str(linea["logger"]).startswith("httpx")]


def test_la_peticion_se_registra_con_la_plantilla_de_ruta_y_nunca_con_el_token(salida: io.StringIO) -> None:
    respuesta = TestClient(_app()).get("/public/citas/token-secreto-123")

    assert respuesta.status_code == 200
    [linea] = _de(salida, "app.peticion")
    assert linea["metodo"] == "GET"
    assert linea["ruta"] == "/public/citas/{token}"
    assert linea["status"] == 200
    assert isinstance(linea["duracion_ms"], (int, float))
    assert "token-secreto-123" not in json.dumps(_de_la_app(salida))


def test_cada_peticion_tiene_un_id_que_sale_en_el_header_y_en_sus_logs(salida: io.StringIO) -> None:
    respuesta = TestClient(_app()).get("/public/citas/t")

    request_id = respuesta.headers["X-Request-ID"]
    assert len(request_id) == 32
    lineas = _de_la_app(salida)
    assert [linea["logger"] for linea in lineas] == ["prueba", "app.peticion"]
    assert {linea["request_id"] for linea in lineas} == {request_id}


def test_un_x_request_id_valido_se_respeta_y_uno_raro_se_reemplaza(salida: io.StringIO) -> None:
    cliente = TestClient(_app())

    assert cliente.get("/public/citas/t", headers={"X-Request-ID": "abc-123"}).headers["X-Request-ID"] == "abc-123"
    raro = '"}<x>' * 30  # largo y con caracteres que no son de un ID
    reemplazado = cliente.get("/public/citas/t", headers={"X-Request-ID": raro}).headers["X-Request-ID"]
    assert reemplazado != raro and len(reemplazado) == 32


def test_un_error_no_controlado_responde_500_generico_y_deja_el_traceback_en_el_log(salida: io.StringIO) -> None:
    respuesta = TestClient(_app()).get("/roto")

    assert respuesta.status_code == 500
    assert respuesta.json() == {"codigo": "error_interno", "mensaje": "Algo salió mal. Intenta de nuevo."}
    assert "RuntimeError" not in respuesta.text
    [error] = _de(salida, "app.errores")
    assert error["request_id"] == respuesta.headers["X-Request-ID"]
    assert "RuntimeError: se cayó con +57300***4567" in str(error["error"])
    [peticion] = _de(salida, "app.peticion")
    assert peticion["status"] == 500
