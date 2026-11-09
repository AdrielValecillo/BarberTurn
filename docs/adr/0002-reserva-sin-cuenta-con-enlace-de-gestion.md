# ADR-0002 · Reserva sin cuenta, con enlace de gestión por cita

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RF-05, RF-09, RF-10, RNF-01, RNF-10, D-02

## Contexto

Un cliente de barbería reserva una o dos veces al mes. Pedirle crear una cuenta con contraseña agrega fricción y olvidos, y la prioridad del producto es que reservar sea muy fácil.

## Decisión

- El cliente reserva solo con **nombre y número de WhatsApp**.
- Cada cita tiene un **enlace de gestión** con un token aleatorio de 32 bytes; en la base solo se guarda su hash.
- El atajo "Repetir mi último corte" se basa en datos guardados **en el propio dispositivo**, nunca en el teléfono que alguien escriba.

## Consecuencias

- (+) Reserva en menos de un minuto, sin contraseñas.
- (+) Si el cliente pierde el enlace, basta con que escriba al número central: la respuesta automática se lo reenvía, y WhatsApp ya garantiza que es el dueño de ese número.
- (−) El teléfono no se verifica al reservar: alguien podría reservar con un número ajeno. Ese número recibiría la confirmación y podría cancelar. Se mitiga con los límites de RN-11.
- (−) Quien tenga el enlace puede gestionar la cita, por eso el token es largo y no adivinable.

## Alternativas descartadas

- **Cuenta con contraseña:** demasiada fricción para el uso esperado.
- **Código de verificación por WhatsApp al reservar:** agrega un paso y cuesta un mensaje de autenticación por reserva. Se reconsidera si aparece abuso.
