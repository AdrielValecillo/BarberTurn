"""Casos de uso de la agenda."""

import hashlib
import secrets
from datetime import date
from itertools import groupby
from operator import itemgetter
from uuid import UUID

import asyncpg

from app.core.db import Conexion
from app.core.errores import ErrorDominio
from app.core.eventos import publicar
from app.domains import barberias, clientes
from app.domains.agenda import queries, repo
from app.domains.agenda.events import CitaCreada
from app.domains.agenda.rules import Candidato, primero_disponible
from app.domains.agenda.schemas import (
    BarberiaPublica,
    BarberoPublico,
    NuevaCitaPublica,
    ServicioPublico,
    TurnoPublico,
)


class BarberiaNoDisponible(ErrorDominio):
    def __init__(self) -> None:
        super().__init__(404, "barberia_no_disponible", "Esta barbería no está disponible.")


class TurnoOcupado(ErrorDominio):
    """CU-01 9a: la web vuelve a la hora con los turnos actualizados, sin borrar nombre ni teléfono."""

    def __init__(self) -> None:
        super().__init__(409, "turno_ocupado", "Ese horario se acaba de ocupar.")


class SeleccionNoDisponible(ErrorDominio):
    def __init__(self) -> None:
        super().__init__(
            409, "seleccion_no_disponible", "Ese servicio o barbero ya no está disponible. Vuelve a elegir."
        )


class MaximoCitas(ErrorDominio):
    """CU-01 9b: dice cuántas tiene, nunca cuáles (cualquiera puede escribir un teléfono ajeno)."""

    def __init__(self, citas: int) -> None:
        mensaje = f"Ya tienes {citas} citas próximas en esta barbería. Revisa tu WhatsApp para gestionarlas."
        super().__init__(409, "maximo_citas", mensaje, {"citas": citas})


async def _barberia_activa(con: Conexion, slug: str) -> asyncpg.Record:
    barberia = await queries.barberia_activa(con, slug)
    if barberia is None:
        raise BarberiaNoDisponible()
    return barberia


async def barberia_publica(con: Conexion, slug: str, servicio_id: UUID | None) -> BarberiaPublica:
    """F1.01 · Página pública: datos, servicios activos y barberos con su próximo turno (RF-01, RF-03, RN-16)."""
    barberia = await _barberia_activa(con, slug)
    barberos = await queries.barberos_con_proximo_turno(con, barberia["id"], servicio_id)
    return BarberiaPublica(
        **barberia,
        servicios=[ServicioPublico(**s) for s in await queries.servicios_activos(con, barberia["id"])],
        barberos=[BarberoPublico(**b) for b in barberos],
    )


async def turnos_publicos(
    con: Conexion, slug: str, servicio_id: UUID, miembro_id: UUID | None, fecha: date
) -> list[TurnoPublico]:
    """F1.04 · Turnos libres de una fecha local; sin `miembro_id`, cada hora con el barbero que asigna RN-05."""
    barberia = await _barberia_activa(con, slug)
    filas = sorted(
        await queries.turnos_libres(con, barberia["id"], servicio_id, miembro_id, fecha), key=itemgetter("inicio")
    )
    return [
        TurnoPublico(inicio=inicio, miembro_id=elegido.miembro_id)
        for inicio, grupo in groupby(filas, key=itemgetter("inicio"))
        if (
            elegido := primero_disponible(
                Candidato(f["miembro_id"], inicio, f["citas_del_dia"], f["orden"]) for f in grupo
            )
        )
    ]


async def crear_cita_publica(con: Conexion, datos: NuevaCitaPublica) -> str:
    """F1.05 · Reserva desde la página pública, en la transacción de quien llama (doc 04 §5.1).

    Devuelve el token del enlace de gestión en claro; en la base solo queda su hash (RNF-10).
    """
    barberia = await _barberia_activa(con, datos.slug)
    servicio = await barberias.servicio_prestado(con, barberia["id"], datos.servicio_id, datos.miembro_id)
    if servicio is None:
        raise SeleccionNoDisponible()
    if not await repo.turno_libre(con, datos.miembro_id, datos.inicio, servicio["duracion_min"], barberia["zona"]):
        raise TurnoOcupado()

    cliente_id = await clientes.registrar(
        con, barberia["id"], datos.nombre, datos.telefono, marketing=datos.acepta_marketing
    )
    # Sin carrera entre dos reservas del mismo cliente: el upsert de `registrar` bloquea su fila hasta el commit.
    citas = await repo.citas_futuras(con, barberia["id"], cliente_id)
    if citas >= barberia["max_citas_futuras_por_cliente"]:
        raise MaximoCitas(citas)

    token = secrets.token_urlsafe(32)
    try:
        cita_id = await repo.insertar_cita(
            con,
            barberia_id=barberia["id"],
            miembro_id=datos.miembro_id,
            cliente_id=cliente_id,
            servicio=servicio,
            inicio=datos.inicio,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
        )
    except asyncpg.ExclusionViolationError as error:
        # Otro cliente lo tomó entre la validación y el insert: `citas_sin_solape` decide (RNF-05).
        raise TurnoOcupado() from error
    await repo.registrar_evento(con, barberia["id"], cita_id, "creada", "cliente")
    await publicar(con, CitaCreada(cita_id, barberia["id"]))
    return token
