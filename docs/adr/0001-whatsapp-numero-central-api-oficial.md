# ADR-0001 · WhatsApp con la API oficial y un número central

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RF-13 a RF-21, D-01

## Contexto

Los recordatorios por WhatsApp son el núcleo del producto: es el canal que usan los clientes de las barberías. Hay cuatro formas de enviarlos:

1. Librerías no oficiales que imitan WhatsApp Web (Baileys, whatsapp-web.js).
2. La API oficial de Meta (WhatsApp Cloud API) con **un número central** de la plataforma.
3. La API oficial con **un número por barbería**, conectado con Embedded Signup, lo que exige ser Tech Provider de Meta.
4. Un intermediario (BSP) como Twilio o 360dialog sobre la API oficial.

## Decisión

Usar la **API oficial con un número central** de la plataforma. Los mensajes van con el nombre de la plataforma y el texto menciona la barbería y el barbero. Todas las plantillas son de categoría *utilidad*.

## Consecuencias

- (+) Sin riesgo de bloqueo del número ni de incumplir los términos de WhatsApp.
- (+) Una sola integración y un solo trámite para todas las barberías.
- (+) Costo bajo en Colombia (del orden de 0,001 USD por mensaje de utilidad).
- (−) El cliente ve el nombre de la plataforma, no el de la barbería.
- (−) Las respuestas libres del cliente llegan a la plataforma: se responden automáticamente con el enlace de gestión y el contacto de la barbería (RF-21).
- (−) Sin verificación del negocio, el límite es de 250 clientes distintos cada 24 horas.
- (−) Desde el 1 de octubre de 2026 también se cobran las respuestas dentro de la ventana de 24 horas (con 1.000 gratis al mes por número).

## Alternativas descartadas

- **No oficial:** gratis, pero arriesga el bloqueo del número (si es el del barbero, pierde su canal con los clientes), incumple los términos y necesita un proceso permanente con sesión.
- **Número por barbería:** más trabajo y trámite de Tech Provider. Queda como posible plan premium.
- **BSP:** simplifica el trámite, pero cobra una comisión sobre cada mensaje.
