# ADR-0003 · Sin API de Google Calendar en el MVP

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RF-08, D-03

## Contexto

La idea inicial incluía conectar Google Calendar. Hacerlo por API implica OAuth para cada barbero, manejo y renovación de tokens, verificación de la app ante Google por usar permisos sensibles de calendario, y resolver conflictos de sincronización en ambos sentidos.

## Decisión

- La **base de datos es la fuente de verdad** de la agenda.
- Al cliente se le ofrece "Agregar a mi calendario" con un archivo `.ics` y un enlace para Google Calendar que no requiere API.
- El barbero ve su agenda en el panel.

## Consecuencias

- (+) Ahorra semanas de trabajo y el trámite de verificación con Google.
- (+) No hay conflictos de sincronización.
- (−) Los barberos que ya viven en Google Calendar tienen que usar el panel.

## Revisión

En fase 2, si los barberos lo piden: sincronización **en un solo sentido** (de la plataforma hacia su calendario), opcional por barbero.
