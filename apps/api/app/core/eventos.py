"""Bus de eventos de dominio en proceso (doc 11 §5). No conoce ningún dominio."""

from collections import defaultdict
from collections.abc import Awaitable, Callable
from typing import Any

Manejador = Callable[[Any, Any], Awaitable[None]]  # (conexión, evento)
_manejadores: dict[type, list[Manejador]] = defaultdict(list)


def escuchar(tipo_evento: type) -> Callable[[Manejador], Manejador]:
    def registrar(funcion: Manejador) -> Manejador:
        _manejadores[tipo_evento].append(funcion)
        return funcion

    return registrar


async def publicar(con: Any, evento: object) -> None:
    """Ejecuta los manejadores dentro de la transacción de quien publica."""
    for manejador in _manejadores[type(evento)]:
        await manejador(con, evento)
