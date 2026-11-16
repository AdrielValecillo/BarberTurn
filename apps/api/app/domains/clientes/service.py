"""Casos de uso de clientes."""

from uuid import UUID

from app.core.db import Conexion
from app.core.errores import ErrorDominio
from app.domains.clientes import repo
from app.shared.telefono import normalizar

# Versión del texto de la política que acepta el cliente (RF-06). La pone la API, nunca la web.
# shortcut: borrador hasta publicar la política en /privacidad (F4.04); entonces se sube la versión.
VERSION_POLITICA = "2026-11-borrador"


class TelefonoInvalido(ErrorDominio):
    def __init__(self) -> None:
        super().__init__(422, "telefono_invalido", "Escribe un celular de 10 dígitos, por ejemplo 300 123 4567.")


async def registrar(con: Conexion, barberia_id: UUID, nombre: str, telefono: str, *, marketing: bool) -> UUID:
    """F1.02 · Registra o actualiza al cliente que reserva en la web y guarda sus autorizaciones con la versión vigente.

    Quien llama ya verificó que aceptó la política (la casilla es obligatoria, RF-06);
    marketing se guarda solo si marcó la casilla (RF-07).
    """
    telefono_e164 = normalizar(telefono)
    if telefono_e164 is None:
        raise TelefonoInvalido()
    cliente_id = await repo.guardar_cliente(con, barberia_id, nombre, telefono_e164, marketing)
    tipos = ["tratamiento_datos", "mensajes_marketing"] if marketing else ["tratamiento_datos"]
    await repo.guardar_consentimientos(con, barberia_id, cliente_id, tipos, VERSION_POLITICA, "web")
    return cliente_id
