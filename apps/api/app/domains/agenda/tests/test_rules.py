"""Reglas puras de la agenda (F1.03): RN-05, RN-06 y RN-08, con casos de tabla sacados del doc 01."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.domains.agenda.rules import Candidato, primero_disponible, puede_cancelar, puede_pasar

A_LAS_2 = datetime(2026, 11, 20, 19, 0, tzinfo=UTC)  # 2:00 p. m. en Bogotá
A_LAS_3 = datetime(2026, 11, 20, 20, 0, tzinfo=UTC)  # 3:00 p. m. en Bogotá

# RN-08: cada flecha del diagrama de estados. Todo par que no esté aquí está prohibido.
FLECHAS = {
    ("pendiente", "confirmada"),  # el cliente toca Confirmo
    ("confirmada", "pendiente"),  # se reagenda
    ("pendiente", "pendiente"),  # se reagenda
    ("pendiente", "cancelada"),
    ("confirmada", "cancelada"),
    ("pendiente", "atendida"),
    ("confirmada", "atendida"),
    ("pendiente", "no_asistio"),
    ("confirmada", "no_asistio"),
}
ESTADOS = ["pendiente", "confirmada", "atendida", "no_asistio", "cancelada"]


@pytest.mark.parametrize("desde", ESTADOS)
@pytest.mark.parametrize("hacia", ESTADOS)
def test_rn08_solo_se_permiten_las_flechas_del_diagrama(desde: str, hacia: str) -> None:
    # después del inicio, para que "no vino" no dependa de la hora
    assert puede_pasar(desde, hacia, A_LAS_2, ahora=A_LAS_3) == ((desde, hacia) in FLECHAS)


# RN-08: "No vino solo se puede marcar después de la hora de inicio."
@pytest.mark.parametrize(
    ("minutos_desde_inicio", "esperado"),
    [(-1, False), (0, True), (1, True)],
)
def test_rn08_no_vino_solo_desde_la_hora_de_inicio(minutos_desde_inicio: int, esperado: bool) -> None:
    ahora = A_LAS_3 + timedelta(minutes=minutos_desde_inicio)
    assert puede_pasar("confirmada", "no_asistio", A_LAS_3, ahora) is esperado


# RN-06: el cliente cancela hasta 120 min antes (configurable); la barbería, siempre; nunca sola (RN-09).
@pytest.mark.parametrize(
    ("actor", "minutos_antes", "limite_min", "esperado"),
    [
        ("cliente", 121, 120, True),
        ("cliente", 120, 120, True),  # justo en el límite todavía puede
        ("cliente", 119, 120, False),
        ("cliente", 30, 0, True),  # límite configurado en 0
        ("cliente", -10, 0, False),  # la cita ya empezó
        ("miembro", 5, 120, True),
        ("miembro", -60, 120, True),
        ("sistema", 500, 120, False),
        ("Cliente", 500, 120, False),  # un actor desconocido nunca salta el límite
    ],
)
def test_rn06_limite_de_cancelacion(actor: str, minutos_antes: int, limite_min: int, esperado: bool) -> None:
    ahora = A_LAS_3 - timedelta(minutes=minutos_antes)
    assert puede_cancelar(actor, A_LAS_3, ahora, limite_min) is esperado


ANA = UUID(int=1)
BETO = UUID(int=2)
CAMI = UUID(int=3)


# RN-05: el turno libre más cercano; empate → menos citas ese día; empate → menor `orden`.
@pytest.mark.parametrize(
    ("candidatos", "esperado"),
    [
        ([], None),
        ([Candidato(ANA, A_LAS_3, 0, 0), Candidato(BETO, A_LAS_2, 5, 9)], BETO),
        ([Candidato(ANA, A_LAS_2, 4, 0), Candidato(BETO, A_LAS_2, 2, 9)], BETO),
        ([Candidato(ANA, A_LAS_2, 2, 1), Candidato(BETO, A_LAS_2, 2, 0)], BETO),
        ([Candidato(CAMI, A_LAS_3, 0, 0), Candidato(ANA, A_LAS_2, 3, 2), Candidato(BETO, A_LAS_2, 3, 1)], BETO),
        # empate total (mismo `orden` por defecto): el resultado no depende del orden de entrada
        ([Candidato(BETO, A_LAS_2, 1, 0), Candidato(ANA, A_LAS_2, 1, 0)], ANA),
        ([Candidato(ANA, A_LAS_2, 1, 0), Candidato(BETO, A_LAS_2, 1, 0)], ANA),
    ],
)
def test_rn05_primero_disponible(candidatos: list[Candidato], esperado: UUID | None) -> None:
    elegido = primero_disponible(candidatos)
    assert (elegido.miembro_id if elegido else None) == esperado
