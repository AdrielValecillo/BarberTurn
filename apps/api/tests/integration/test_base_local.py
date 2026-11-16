import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.integracion


async def test_la_base_de_prueba_tiene_las_migraciones_y_el_seed(con: "asyncpg.Connection[asyncpg.Record]") -> None:
    nombre = await con.fetchval("select nombre from barberias where slug = 'barberia-norte'")

    assert nombre == "Barbería Norte"


def test_health_responde_ok_contra_la_base_real() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.get("/health")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}
