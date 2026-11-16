"""Casos de uso de la agenda."""

from uuid import UUID

from app.core.db import Conexion
from app.core.errores import ErrorDominio
from app.domains.agenda import queries
from app.domains.agenda.schemas import BarberiaPublica, BarberoPublico, ServicioPublico


class BarberiaNoDisponible(ErrorDominio):
    def __init__(self) -> None:
        super().__init__(404, "barberia_no_disponible", "Esta barbería no está disponible.")


async def barberia_publica(con: Conexion, slug: str, servicio_id: UUID | None) -> BarberiaPublica:
    """F1.01 · Página pública: datos, servicios activos y barberos con su próximo turno (RF-01, RF-03, RN-16)."""
    barberia = await queries.barberia_activa(con, slug)
    if barberia is None:
        raise BarberiaNoDisponible()
    barberos = await queries.barberos_con_proximo_turno(con, barberia["id"], servicio_id)
    return BarberiaPublica(
        **barberia,
        servicios=[ServicioPublico(**s) for s in await queries.servicios_activos(con, barberia["id"])],
        barberos=[BarberoPublico(**b) for b in barberos],
    )
