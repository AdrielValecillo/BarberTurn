import asyncio

from app.core.config import get_settings
from app.core.db import crear_pool

INTERVALO_SEGUNDOS = 60


async def main() -> None:
    pool = await crear_pool(get_settings().database_url)
    try:
        while True:
            # shortcut: aún no envía nada; implementar en domains/notificaciones/envio.py (CU-13, fase F3)
            await asyncio.sleep(INTERVALO_SEGUNDOS)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
