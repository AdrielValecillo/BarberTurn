"""Escribe el OpenAPI de la API para generar los tipos de la web: `python -m app.export_openapi <destino>`."""

import json
import sys
from pathlib import Path

from app.main import app

if __name__ == "__main__":
    Path(sys.argv[1]).write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
