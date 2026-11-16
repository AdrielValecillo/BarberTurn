"""Eventos que publica la agenda (doc 11 §5). Los manejadores corren en la misma transacción."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CitaCreada:
    cita_id: UUID
    barberia_id: UUID
