# ADR-0006 · Interfaz propia para enviar notificaciones

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RF-13 a RF-20, RN-07, D-06

## Contexto

El trámite con Meta (plantillas, número, verificación) puede tardar más que el desarrollo, y las reglas de cuándo enviar cada mensaje (RN-07) son la parte con más casos borde.

## Decisión

- El envío pasa por una interfaz propia, `ProveedorNotificaciones`, con dos implementaciones: `ConsolaProvider` (desarrollo) y `WhatsAppCloudProvider`.
- Las reglas de programación viven en una **función pura**, `programar(cita, ahora)`, que devuelve las notificaciones a crear sin tocar la base ni la red.

## Consecuencias

- (+) Se puede construir y probar todo el sistema sin depender de Meta.
- (+) RN-07 se prueba con casos de tabla, rápidos y sin infraestructura.
- (+) Cambiar de proveedor (un BSP, SMS) no obliga a reescribir el resto.
- (−) Una capa más, pequeña, que mantener.
