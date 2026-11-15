"""Teléfono en E.164 (RN-10). Debe validar igual que `normalizarTelefono` de apps/web/lib/telefono.ts."""

import re

# shortcut: solo celulares de Colombia (+57 y 10 dígitos que empiezan por 3); ampliar si se abre otro país.
# [0-9] y no \d: en Python \d acepta dígitos Unicode ("３"), en JavaScript no.
_CELULAR = re.compile(r"(?:57)?(3[0-9]{9})")


def normalizar(texto: str) -> str | None:
    """Devuelve el número en E.164 ("+573001234567") o None si no es un celular válido."""
    m = _CELULAR.fullmatch(re.sub(r"[^0-9]", "", texto))
    return f"+57{m[1]}" if m else None
