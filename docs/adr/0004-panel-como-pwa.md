# ADR-0004 · Panel del barbero como PWA

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RF-31, D-04

## Contexto

Los barberos usan el celular todo el día. Una app nativa exige publicar en dos tiendas, pasar revisiones y mantener otro código.

## Decisión

El panel es parte de la web en Next.js y se puede **instalar como aplicación** (PWA) en la pantalla de inicio. Los avisos al barbero se envían por **WhatsApp**, no por notificaciones push del navegador.

## Consecuencias

- (+) Un solo código para clientes y personal; actualizaciones inmediatas sin pasar por tiendas.
- (+) Los avisos llegan aunque el barbero no tenga el panel abierto ni instalado.
- (−) Sin presencia en tiendas de apps.
- (−) Las notificaciones push web quedan para después: en iPhone solo funcionan si la PWA está instalada.
