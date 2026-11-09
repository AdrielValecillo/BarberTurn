# ADR-0009 · Monolito modular organizado por dominios

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RNF-16, doc 11

## Contexto

La API tiene partes con reglas y ritmos de cambio muy distintos: la agenda (núcleo del producto), la configuración de la barbería, los clientes, la programación de notificaciones y la integración con WhatsApp. Organizado por capas técnicas (todos los routers juntos, todos los servicios juntos), un cambio en las citas obliga a tocar muchas carpetas, y nada impide que la agenda termine dependiendo de detalles de WhatsApp.

Al mismo tiempo, hay un solo desarrollador y un piloto pequeño: separar en microservicios multiplicaría despliegues, redes y fallos parciales sin beneficio.

## Decisión

- La API y el worker son **un solo despliegue** con cinco dominios en `app/domains/`: `barberias`, `clientes`, `agenda`, `notificaciones` y `mensajeria`.
- Los dominios forman **capas**: cada uno solo importa la API pública de los que tiene debajo (`mensajeria → notificaciones → agenda → clientes → barberias`).
- **Solo el dominio dueño escribe sus tablas.** Las lecturas cruzadas para pantallas viven en `queries.py`.
- Los efectos hacia un dominio de arriba se comunican con **eventos de dominio en proceso**, ejecutados en la misma transacción.
- `core/` y `shared/` no conocen ningún dominio.
- Las reglas de dependencia se verifican en la CI con **import-linter**.

## Consecuencias

- (+) Todo lo de un dominio está junto; la agenda, que es el núcleo, no depende de la mensajería.
- (+) Agregar un comportamiento nuevo ante un evento (por ejemplo, fidelización) no obliga a tocar la agenda.
- (+) Si algún día hiciera falta separar un dominio en otro servicio, sus límites ya están definidos.
- (−) Más disciplina: hay que decidir el dominio dueño de cada cosa nueva.
- (−) Algunas pantallas necesitan datos de varios dominios y se arman con consultas de solo lectura en `queries.py`.

## Alternativas descartadas

- **Organización por capas técnicas:** fácil al principio, pero mezcla dominios y no protege el núcleo.
- **Microservicios:** demasiada operación para un desarrollador y un piloto.
- **Un esquema de PostgreSQL por dominio:** aislaría más, pero complica Supabase (esquemas expuestos, RLS y funciones de apoyo). La pertenencia de cada tabla queda documentada en el doc 04.
