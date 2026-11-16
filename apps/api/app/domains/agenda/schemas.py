"""Entrada y salida de la API de la agenda."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ServicioPublico(BaseModel):
    id: UUID
    nombre: str
    duracion_min: int
    precio_cop: int


class BarberoPublico(BaseModel):
    id: UUID
    nombre: str
    proximo_turno: datetime | None  # null: sin turnos libres en toda la ventana de reserva


class BarberiaPublica(BaseModel):
    slug: str
    nombre: str
    direccion: str
    zona: str
    servicios: list[ServicioPublico]
    barberos: list[BarberoPublico]
