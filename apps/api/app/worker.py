import asyncio
import logging

from app.core.config import get_settings
from app.core.db import crear_pool
from app.core.logs import configurar_logs

INTERVALO_SEGUNDOS = 60  # cada minuto (doc 04 §5.2, RNF-06)


async def main() -> None:
    configurar_logs()
    pool = await crear_pool(get_settings().database_url)
    logging.getLogger("app.worker").info("worker iniciado", extra={"intervalo_s": INTERVALO_SEGUNDOS})
    try:
        while True:
            # shortcut: aún no envía nada; implementar en domains/notificaciones/envio.py (CU-13, fase F3)
            await asyncio.sleep(INTERVALO_SEGUNDOS)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
