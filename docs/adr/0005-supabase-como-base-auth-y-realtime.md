# ADR-0005 · Supabase para base de datos, autenticación y tiempo real

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RNF-05, RNF-08, RF-22, RF-30, D-05

## Contexto

El sistema necesita PostgreSQL con restricciones de exclusión y RLS, acceso sin contraseñas para el personal y una agenda que se actualice sola. El equipo es una sola persona.

## Decisión

Usar **Supabase**: PostgreSQL administrado, Supabase Auth (enlace o código por correo, con SMTP propio en producción) y Supabase Realtime. Las migraciones se manejan con la CLI de Supabase.

## Consecuencias

- (+) Auth y tiempo real sin construirlos; Realtime respeta la RLS.
- (+) Entorno local completo con `supabase start`.
- (−) El esquema usa piezas propias de Supabase (`auth.users`, `auth.uid()`, roles `anon` y `authenticated`).
- (−) Los proyectos gratuitos se pausan con poca actividad: **producción va en plan pago antes del piloto**.

## Alternativas descartadas

- **PostgreSQL en Railway con autenticación propia** y tiempo real con SSE: más código que mantener sin ganar nada importante en el MVP. Sigue siendo la ruta de salida si Supabase deja de convenir, porque la base es PostgreSQL estándar.
