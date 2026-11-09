# ADR-0007 · Stack: Next.js, FastAPI y Railway

- **Estado:** Propuesta (al aceptarla se cierran P-02 y P-03 del doc 00)
- **Fecha:** 2026-11-07
- **Relacionado con:** RNF-15, RNF-16

## Contexto

Hay que elegir lenguajes, frameworks y hosting. Condiciones: un solo desarrollador, poco presupuesto, un worker que corre permanentemente y un webhook que debe responder siempre. El desarrollador ya tiene experiencia en un proyecto con FastAPI, Next.js, PostgreSQL y despliegue en Railway con Docker.

## Decisión

- **Web:** Next.js con TypeScript (reserva pública y panel PWA).
- **API, webhook y worker:** FastAPI en Python; el worker es otro proceso del mismo código.
- **Base, auth y tiempo real:** Supabase (ADR-0005).
- **Hosting:** Railway para los tres servicios.
- **Tipos compartidos:** los tipos de TypeScript de la web se generan desde el OpenAPI de FastAPI (por ejemplo, con `openapi-typescript`), para que el frontend y la API no se desincronicen.

## Consecuencias

- (+) Máxima productividad: tecnologías que ya se dominan.
- (+) Railway permite uso comercial y procesos permanentes, lo que el worker necesita.
- (−) Dos lenguajes y tres servicios que desplegar.
- (−) El costo mensual exacto de Railway y Supabase se confirma al definir P-06.

## Alternativas descartadas

- **Todo en Next.js** (rutas de API, tareas programadas de la plataforma): un solo lenguaje, pero el worker y el webhook quedan más frágiles en entornos *serverless*, y el plan gratuito de Vercel no permite uso comercial.
- **Supabase Edge Functions con `pg_cron`:** menos piezas, pero en el plan gratuito un proyecto pausado detiene el cron sin avisar, y la lógica queda repartida entre SQL y funciones.
- **Otro framework de backend** (Django, Laravel, NestJS): no aporta ventajas que compensen perder la experiencia previa.
