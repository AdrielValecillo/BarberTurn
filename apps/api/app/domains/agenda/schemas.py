"""Entrada y salida de la API de la agenda."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, Field, StringConstraints


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
    telefono_contacto: str | None  # E.164; CU-01 5a: se muestra si no hay turnos en toda la ventana
    zona: str
    servicios: list[ServicioPublico]
    barberos: list[BarberoPublico]


class TurnoPublico(BaseModel):
    inicio: datetime
    miembro_id: UUID  # quién atiende: con "el primero disponible" lo elige la API (RN-05)


class NuevaCitaPublica(BaseModel):
    slug: str
    servicio_id: UUID
    miembro_id: UUID  # con "el primero disponible", el que asignó GET /turnos
    inicio: AwareDatetime
    nombre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]
    telefono: str = Field(max_length=30)  # como lo escribió; la API lo normaliza a E.164
    acepta_politica: Literal[True]  # RF-06: casilla obligatoria
    acepta_marketing: bool = False  # RF-07


class CitaCreadaPublica(BaseModel):
    token: str  # para el enlace de gestión /c/{token}; no se puede volver a pedir
