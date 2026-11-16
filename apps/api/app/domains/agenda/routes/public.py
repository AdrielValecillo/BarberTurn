"""/public/*: sin sesión y con la conexión de servicio, así que toda consulta filtra por la barbería del slug."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.db import Conexion, conexion_servicio
from app.core.errores import RespuestaError
from app.domains.agenda import service
from app.domains.agenda.schemas import BarberiaPublica

router = APIRouter(prefix="/public", tags=["público"])

ConServicio = Annotated[Conexion, Depends(conexion_servicio)]


@router.get(
    "/barberias/{slug}",
    responses={404: {"model": RespuestaError, "description": "No existe o está suspendida (CU-01 1a)"}},
)
async def obtener_barberia(slug: str, con: ConServicio, servicio: UUID | None = None) -> BarberiaPublica:
    """Con `servicio`, solo los barberos que lo prestan y su próximo turno para ese servicio (RF-03)."""
    return await service.barberia_publica(con, slug, servicio)
