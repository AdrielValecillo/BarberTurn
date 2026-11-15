"""Reglas puras de la agenda: sin base ni red (doc 11)."""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID

# RN-08: pendiente → pendiente y confirmada → pendiente son "se reagenda". atendida, no_asistio y cancelada son finales.
_TRANSICIONES: dict[str, frozenset[str]] = {
    "pendiente": frozenset({"pendiente", "confirmada", "cancelada", "atendida", "no_asistio"}),
    "confirmada": frozenset({"pendiente", "cancelada", "atendida", "no_asistio"}),
}


def puede_pasar(desde: str, hacia: str, inicio: datetime, ahora: datetime) -> bool:
    """RN-08: ¿la cita puede pasar de `desde` a `hacia`? "No vino" solo desde la hora de inicio."""
    if hacia == "no_asistio" and ahora < inicio:
        return False
    return hacia in _TRANSICIONES.get(desde, frozenset())


def puede_cancelar(actor: str, inicio: datetime, ahora: datetime, limite_min: int) -> bool:
    """RN-06: el cliente cancela hasta `limite_min` minutos antes del inicio; la barbería (miembro), siempre.

    Cualquier otro actor, incluido "sistema", no cancela: RN-09 dice que la cita nunca se cancela sola.
    """
    if actor == "miembro":
        return True
    return actor == "cliente" and ahora <= inicio - timedelta(minutes=limite_min)


@dataclass(frozen=True)
class Candidato:
    """Un barbero que presta el servicio y tiene libre `inicio`, con sus citas de ese día."""

    miembro_id: UUID
    inicio: datetime
    citas_del_dia: int
    orden: int


def primero_disponible(candidatos: Iterable[Candidato]) -> Candidato | None:
    """RN-05: el turno más cercano; si hay empate, menos citas ese día; si sigue, menor `orden`.

    Sirve también para asignar barbero a un turno concreto: todos los candidatos llevan el mismo `inicio`.
    """
    # miembro_id solo para que el resultado no dependa del orden de entrada
    return min(candidatos, key=lambda c: (c.inicio, c.citas_del_dia, c.orden, c.miembro_id), default=None)
