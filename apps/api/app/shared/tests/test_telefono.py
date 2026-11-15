"""Teléfono en E.164 (F1.02, RN-10). Mismos casos que la web (tests/unit/telefono.test.ts): validan igual."""

import pytest

from app.shared.telefono import normalizar


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("300 123 4567", "+573001234567"),
        ("3001234567", "+573001234567"),
        ("+57 300-123-4567", "+573001234567"),
        ("573001234567", "+573001234567"),
    ],
)
def test_cu01_celular_valido(texto: str, esperado: str) -> None:
    assert normalizar(texto) == esperado


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "300 123 456",
        "30012345678",
        "601 123 4567",
        "abc",
        "+1 300 123 4567",
        "3００１２３４５６７",  # dígitos no ASCII: la web tampoco los acepta
    ],
)
def test_cu01_8a_no_es_un_celular_valido(texto: str) -> None:
    assert normalizar(texto) is None
