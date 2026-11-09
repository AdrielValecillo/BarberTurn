# ADR-0008 · RLS aplicada en cada petición del panel

- **Estado:** Aceptada
- **Fecha:** 2026-11-07
- **Relacionado con:** RNF-08, DM-11

## Contexto

La API se conecta a la base con un usuario que salta la RLS. Si un endpoint del panel olvida filtrar por barbería, un barbero podría ver datos de otro negocio. Con varias barberías en la misma base, ese error sería grave.

## Decisión

- **Panel:** cada petición verifica el JWT de Supabase y abre una transacción con `set local role authenticated` y los *claims* del usuario en `request.jwt.claims`. Así la RLS de la base aplica además de los filtros del código.
- **Público:** usa la conexión de servicio y **siempre** acota por la barbería del slug o del token. Las pruebas cubren que ningún endpoint público devuelva datos de otra barbería.
- **Administración:** verifica que el usuario esté en `admins_plataforma` y luego usa la conexión de servicio, porque necesita ver todas las barberías.

## Consecuencias

- (+) Defensa en profundidad: un error en el código no basta para filtrar datos.
- (+) Las mismas políticas protegen la API y la suscripción de Realtime.
- (−) Una pequeña sobrecarga por petición (dos instrucciones al abrir la transacción).
- (−) El usuario de conexión debe poder cambiar al rol `authenticated` (en Supabase, el usuario `postgres` puede).

## Alternativas descartadas

- **Solo filtros en el código:** un olvido expone datos de otra barbería.
- **Que el panel consulte la base directamente desde el navegador:** obligaría a mover las reglas de negocio a funciones SQL, más difíciles de probar y mantener.
