"""/public/*: sin sesión y con la conexión de servicio, así que toda consulta filtra por la barbería del slug."""

from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.db import Conexion, conexion_servicio
from app.core.errores import RespuestaError
from app.core.limites import LimitePorIP
from app.domains.agenda import service
from app.domains.agenda.schemas import BarberiaPublica, CitaCreadaPublica, NuevaCitaPublica, TurnoPublico

router = APIRouter(prefix="/public", tags=["público"])

# scope="function": la transacción se confirma antes de enviar la respuesta. Con el scope por defecto
# FastAPI la cerraría después, y el cliente podría recibir el token de una cita que no se guardó.
ConServicio = Annotated[Conexion, Depends(conexion_servicio, scope="function")]

# RN-11: 5 reservas por IP por hora (F1.06). Solo cuentan las que se guardan.
limite_reservas = LimitePorIP(5, 3600)


@router.get(
    "/barberias/{slug}",
    responses={404: {"model": RespuestaError, "description": "No existe o está suspendida (CU-01 1a)"}},
)
async def obtener_barberia(slug: str, con: ConServicio, servicio: UUID | None = None) -> BarberiaPublica:
    """Con `servicio`, solo los barberos que lo prestan y su próximo turno para ese servicio (RF-03)."""
    return await service.barberia_publica(con, slug, servicio)


@router.get(
    "/barberias/{slug}/turnos",
    responses={404: {"model": RespuestaError, "description": "No existe o está suspendida (CU-01 1a)"}},
)
async def obtener_turnos(
    slug: str, servicio: UUID, fecha: date, con: ConServicio, miembro: UUID | None = None
) -> list[TurnoPublico]:
    """Turnos libres de `fecha` (local de la barbería). Sin `miembro` es "el primero disponible" (RN-05).

    Un servicio o barbero que no es de la barbería, o que no se prestan entre sí, da una lista vacía.
    """
    return await service.turnos_publicos(con, slug, servicio, miembro, fecha)


@router.post(
    "/citas",
    status_code=201,
    dependencies=[Depends(limite_reservas, scope="function")],
    responses={
        404: {"model": RespuestaError, "description": "La barbería no existe o está suspendida (RN-16)"},
        409: {
            "model": RespuestaError,
            "description": "`turno_ocupado` (CU-01 9a), `maximo_citas` (9b) o `seleccion_no_disponible`",
        },
        422: {"description": "`telefono_invalido` (CU-01 8a) o datos inválidos (sin aceptar la política, RF-06)"},
        429: {"model": RespuestaError, "description": "Límite de reservas por IP (CU-01 9c)"},
    },
)
async def crear_cita(datos: NuevaCitaPublica, con: ConServicio) -> CitaCreadaPublica:
    """CU-01 · Reserva sin cuenta. El token se devuelve solo esta vez."""
    return CitaCreadaPublica(token=await service.crear_cita_publica(con, datos))
