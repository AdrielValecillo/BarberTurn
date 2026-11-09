# 06 · Plan de implementación

| | |
|---|---|
| **Versión del documento** | 0.1 (borrador) |
| **Fecha** | 9 de noviembre de 2026 |
| **Documentos relacionados** | [00 · Visión y alcance](00-vision-y-alcance.md) (fases), [01 · Requerimientos](01-requerimientos.md), [02 · Casos de uso](02-casos-de-uso.md), [03 · Arquitectura](03-arquitectura.md), [04 · Modelo de datos](04-modelo-de-datos.md), [10 · Estructura del monorepo](10-estructura-del-monorepo.md), [11 · Dominios](11-dominios.md) |

---

## Cómo usar este documento

- Marca `- [x]` cuando el paso cumpla su **Listo cuando**, no antes. Un paso a medias sigue sin marcar.
- Cada paso tiene un ID (`F1.05`) para citarlo en ramas y PRs (`feat/f1-05-crear-cita`), una descripción, los IDs de requerimientos que cubre (RF, RN, CU, RNF) y su criterio de terminado.
- Los pasos están en el **orden sugerido**. Las pruebas se escriben junto al código que prueban (RNF-16), no al final de la fase.
- No hay fechas: es un solo desarrollador y las estimaciones se hacen al abrir cada fase.
- Al terminar un paso, anota una línea en la [bitácora](#bitácora) del final.

### Reglas para dar un paso por terminado

1. Cumple su **Listo cuando**.
2. `make lint` y `make test` pasan.
3. La documentación afectada se actualizó en el mismo cambio (ver "Dónde va cada cosa" en el [doc 10](10-estructura-del-monorepo.md#7-dónde-va-cada-cosa)).
4. Si cambió la API: `make gen-types` y los tipos subidos. Si cambió la base: una migración **nueva**.
5. El PR cita los IDs que cubre.

---

## Resumen de fases

| Fase | Contenido | Listo cuando (doc 00 §10) | Estado |
|---|---|---|---|
| **F0 · Base** | Repo, entornos, esquema de base de datos, autenticación del personal, trámite con Meta iniciado. | Migración aplicada; un dueño puede iniciar sesión. | En curso |
| **F1 · Reservas** | Página pública, cálculo de disponibilidad, creación de citas, enlace de gestión. | Un cliente reserva, reagenda y cancela sin errores; no hay doble reserva posible. | Pendiente |
| **F2 · Panel** | Agenda, detalle de cita, acciones, citas manuales, bloqueos, configuración. | Un barbero maneja un día completo solo desde el panel. | Pendiente |
| **F3 · WhatsApp** | Plantillas, envío programado, webhook, avisos al barbero. | Ciclo completo de recordatorios con el número real. | Pendiente |
| **F4 · Piloto** | 2–3 barberías en vivo, monitoreo y ajustes. | 4 semanas de uso continuo. | Pendiente |

### Dependencias entre fases

```text
F0 ──► F1 ──► F2 ──┐
 │      │           ├──► F4
 │      └──► F3 ────┘
 └── trámite con Meta (F0.11): corre en paralelo desde el día 1 y es el camino crítico de F3
```

- **F1 no necesita WhatsApp.** Desde F1 la agenda publica `CitaCreada`, `CitaReagendada` y `CitaCancelada`, pero nadie las escucha hasta F3.
- **F2 necesita F0** (inicio de sesión) **y F1** (citas que mostrar).
- **F3 necesita F1.** Puede avanzar en paralelo con F2 hasta el paso F3.07, porque todo se desarrolla con `ConsolaProvider` (ADR-0006).
- El trámite con Meta (aprobación de plantillas, verificación) tarda más que el desarrollo: se inicia en F0.

---

## F0 · Base

**Objetivo:** un esqueleto que corre, una base de datos con el esquema aplicado y el acceso del personal funcionando.
**Listo cuando:** la migración está aplicada y un dueño puede iniciar sesión.

### Repositorio y herramientas

- [x] **F0.01 · Monorepo y herramientas** — pnpm workspace, uv, Supabase CLI como dependencia del repo, `Makefile`, `.editorconfig`, `.gitattributes` y `README`.
  *Cubre:* RNF-16 · *Listo cuando:* los comandos del README corren (en Windows hace falta instalar `make`).
- [x] **F0.02 · Primer commit y repositorio remoto** — revisar `git status`, hacer el primer commit (Conventional Commits) y subir `main` a GitHub.
  *Listo cuando:* el repo está en GitHub con el estado actual.
- [ ] **F0.03 · Primera ejecución de la CI** — abrir un PR de prueba y corregir los workflows (`ci-api`, `ci-web`; nunca se han ejecutado, incluido el job que levanta `supabase start`).
  *Cubre:* RNF-16 · *Listo cuando:* `ci-api` y `ci-web` pasan en verde.

### Base de datos

- [x] **F0.04 · Migración inicial, seed y pruebas de base** — `20261107000000_esquema_inicial.sql` (doc 04 §4), `seed.sql` (una barbería, dos barberos, servicios y horarios) y pruebas pgTAP de RLS de citas y del anti-solape. Verificado en PostgreSQL 16 con un shim de pgTAP.
  *Cubre:* RNF-05, RNF-08, DM-01 a DM-11 · *Listo cuando:* aplica sin errores y las pruebas pasan (cumplido en una base de prueba; falta Supabase real, F0.05).
- [ ] **F0.05 · Verificar contra Supabase local** — `make dev-db`, `make db-reset` y `pnpm exec supabase test db`. Confirma que la migración aplica en el Postgres de Supabase (esquema `auth`, roles, publicación `supabase_realtime`) y que las pruebas pasan con pgTAP real.
  *Listo cuando:* los tres comandos terminan sin errores. **Este paso cierra el "migración aplicada" de la fase.**

### API

- [x] **F0.06 · Esqueleto de la API** — configuración, pool de asyncpg, contexto RLS por petición (`transaccion_panel`, ADR-0008), bus de eventos, `/health`, worker vacío, contratos de import-linter y `Dockerfile`.
  *Cubre:* ADR-0008, ADR-0009 · *Listo cuando:* ruff, mypy, import-linter y pytest pasan.
- [ ] **F0.07 · Errores, logs y base de pruebas** — `core/errores.py` (errores de dominio con su respuesta HTTP: 404, 409 "turno ocupado"…), `core/logs.py` (JSON con ID de petición y teléfonos enmascarados `+57300***4567`) y `tests/conftest.py` con una base de prueba que tiene las migraciones aplicadas. Sentry puede quedar para F4.
  *Cubre:* RNF-16, RNF-17, doc 03 §7.2 y §11 · *Listo cuando:* una prueba de integración corre contra la base local con las migraciones.
- [ ] **F0.08 · Verificación del JWT y miembro actual** — `core/auth.py` verifica el JWT de Supabase (según cómo firme el proyecto: secreto o JWKS; agrega `pyjwt`). `barberias/acceso.py` expone `miembro_actual`, la dependencia que abre `transaccion_panel` y resuelve miembro y rol. Primer endpoint protegido: `GET /panel/barberia`.
  *Cubre:* RF-22, RNF-08, ADR-0008 · *Listo cuando:* el endpoint responde 401 sin JWT, devuelve la barbería con uno válido y una prueba confirma que un usuario de otra barbería no ve nada.

### Web

- [x] **F0.09 · Esqueleto de la web** — Next.js, manifest de la PWA, cliente HTTP tipado (`openapi-fetch` + `@turnero/api-types`), Vitest y la regla de ESLint que impide que un dominio importe a otro.
  *Cubre:* RF-31 (base), doc 11 §8 · *Listo cuando:* `pnpm --filter web lint`, `test` y `build` pasan.
- [ ] **F0.10 · Inicio de sesión del panel** — cliente de Supabase (`lib/supabase/cliente.ts` y `servidor.ts`; `@supabase/supabase-js` y `@supabase/ssr`), `/panel/login` (correo → enlace o código), layout protegido que verifica la sesión y cierre de sesión. El mensaje es siempre "Si el correo está registrado, te llegará un enlace". Hay que decidir cómo evitar que el login cree usuarios nuevos sin revelar qué correos existen.
  *Cubre:* RF-22, CU-06 · *Listo cuando:* el enlace llega al servidor de correo de prueba (`http://127.0.0.1:54324`) y abre una sesión.

### Trámite con Meta, decisiones y entornos

- [ ] **F0.11 · Iniciar el trámite con Meta** — cuenta de negocio y app de WhatsApp Cloud API, número de prueba y registro del número real (el nombre visible debe coincidir con la web, por eso depende de P-01). Las plantillas se redactan en F3.01 y se envían a aprobación como categoría *utilidad*, sin lenguaje promocional.
  *Cubre:* ADR-0001, riesgos del doc 00 §9 · *Listo cuando:* el trámite está iniciado y el número de prueba envía un mensaje a mano. No hace falta que esté aprobado.
- [ ] **F0.12 · Cerrar decisiones pendientes** — P-01 (nombre comercial y dominio) y P-02 (aceptar el ADR-0007, que pasa de *Propuesta* a *Aceptada*). Registrarlo en el doc 00 §7 y en el índice de ADR del doc 03.
  *Listo cuando:* ambas decisiones están escritas en los docs.
- [ ] **F0.13 · Entornos en la nube** — proyecto de Supabase (el gratuito sirve para desarrollo, pero se pausa) y proyecto de Railway con los servicios `web`, `api` y `worker`. Resolver antes el problema del servicio `web`: con carpeta raíz `apps/web` no ve `packages/api-types` (dependencia `workspace:*`), así que hay que usar la raíz del repo con comandos propios o un Dockerfile. Meta necesita una URL pública para el webhook, por lo que esto debe estar antes de F3.09.
  *Cubre:* doc 10 §11, RNF-14 · *Listo cuando:* web y API están desplegadas y `/health` responde contra la base en la nube.
- [ ] **F0.14 · Alta del primer dueño y vinculación** — una forma manual de crear una barbería y su primer dueño por correo (script o SQL; el endpoint de administración llega en F2.10). Al primer ingreso, la API vincula `miembros.user_id` con el usuario autenticado usando el correo del JWT y la conexión de servicio, porque antes de vincular la RLS no reconoce al miembro.
  *Cubre:* CU-06 paso 4, CU-15 · *Listo cuando:* un dueño recibe el enlace, entra y la API lo reconoce como dueño. **Este paso cierra el "un dueño puede iniciar sesión" de la fase.**

---

## F1 · Reservas

**Objetivo:** que un cliente reserve, reagende y cancele desde un enlace, sin cuenta.
**Listo cuando:** un cliente reserva, reagenda y cancela sin errores y no hay doble reserva posible.
**Casos de uso:** CU-01 a CU-04. **Necesita:** F0.05, F0.07.

### API

- [ ] **F1.01 · Datos públicos de la barbería** — `GET /public/barberias/{slug}`: nombre, dirección, servicios activos con duración y precio, y barberos que atienden con su próximo turno. Una barbería inexistente o suspendida responde "no disponible". Ojo con las capas: `barberias` no puede depender de `agenda`, así que el cálculo del "próximo turno" hace que este endpoint viva en `agenda/routes/public.py`.
  *Cubre:* RF-01, RF-03, RN-16, CU-01 · *Listo cuando:* devuelve los datos del seed y una prueba confirma que un slug nunca devuelve datos de otra barbería.
- [ ] **F1.02 · Teléfono, clientes y consentimientos** — `shared/telefono.py` (normalizar a E.164, +57 por defecto), `clientes.registrar` (alta o actualización por `(barberia, teléfono)`, el nombre queda con el último usado) y registro de consentimientos con la versión del texto aceptado.
  *Cubre:* RF-06, RF-07, RN-10 · *Listo cuando:* pruebas de tabla con varios formatos de teléfono; el mismo número en dos barberías crea dos clientes.
- [ ] **F1.03 · Reglas puras de la agenda** — `agenda/rules.py`: transiciones de estado (RN-08), elección del "primero disponible" (RN-05) y límite de cancelación (RN-06). Sin base ni red.
  *Cubre:* RN-05, RN-06, RN-08 · *Listo cuando:* pruebas de tabla que recorren cada flecha del diagrama de estados y los desempates de RN-05.
- [ ] **F1.04 · Turnos disponibles** — `GET /public/barberias/{slug}/turnos?servicio&miembro&fecha` sobre `turnos_disponibles()`; sin `miembro` aplica "el primero disponible".
  *Cubre:* RF-03, RF-04, RN-02 a RN-05, RNF-04 · *Listo cuando:* el ejemplo del doc 01 §4 (14:00, 14:15 y de 15:45 a 18:15) pasa como prueba de integración y la respuesta tarda menos de 500 ms.
- [ ] **F1.05 · Crear cita** — `POST /public/citas`, en una sola transacción (doc 04 §5.1): validar barbería, servicio y que el barbero lo preste; validar el turno; registrar al cliente; máximo de citas futuras (RN-11); generar el token (32 bytes) y guardar solo su hash; insertar la cita con la copia del servicio; consentimientos; evento `creada`; publicar `CitaCreada`. El token en claro se devuelve una sola vez. Un `23P01` responde 409.
  *Cubre:* RF-05, RF-06, RN-01, RN-02, RN-10, RN-11, RN-13, RNF-05, RNF-10 · *Listo cuando:* una prueba lanza dos reservas simultáneas al mismo turno y exactamente una responde 201 y la otra 409.
- [ ] **F1.06 · Límite de reservas por IP** — `core/limites.py` aplicado a `POST /public/citas`: máximo 5 por hora por IP. Con una sola instancia basta un contador en memoria; si la API se escala a varias, moverlo a la base.
  *Cubre:* RN-11 · *Listo cuando:* la sexta reserva de una misma IP en una hora responde 429.
- [ ] **F1.07 · Gestión con token** — `GET /public/citas/{token}` (busca por hash; un token inválido responde un mensaje genérico), turnos para reagendar sin contar la propia cita, `reagendar` (misma cita, vuelve a `pendiente`, evento `reagendada` con la hora anterior y la nueva, publica `CitaReagendada`) y `cancelar` (respeta RN-06, publica `CitaCancelada`).
  *Cubre:* RF-10 a RF-12, RF-20 (parte de agenda), RN-06, RN-08, CU-02 a CU-04 · *Listo cuando:* reagendar conserva ID y enlace; cancelar fuera del límite responde error; ambos liberan el turno.
- [ ] **F1.08 · Archivo de calendario (.ics)** — `GET /public/citas/{token}/calendario.ics`.
  *Cubre:* RF-08 · *Listo cuando:* el archivo se importa en un calendario con la hora correcta en `America/Bogota`.
- [ ] **F1.09 · Aislamiento de los endpoints públicos** — pruebas que recorren todos los `/public/*` y comprueban que ninguno devuelve datos de otra barbería (la conexión de servicio salta la RLS).
  *Cubre:* RNF-08, ADR-0008 · *Listo cuando:* hay una prueba por endpoint con dos barberías en la base.

### Web

- [ ] **F1.10 · Utilidades** — `lib/fechas.ts` (formato `es-CO` en la zona de la barbería: "5:15 p. m.", "sábado 7 de noviembre", "$35.000"), `lib/telefono.ts` y `lib/dispositivo.ts` (nombre, teléfono y último servicio, solo en el dispositivo).
  *Cubre:* RF-09, RNF-12, RNF-13 · *Listo cuando:* pruebas de Vitest con los ejemplos de formato del doc 01.
- [ ] **F1.11 · Componentes base** — `components/ui/`: botón, campo con etiqueta, chip de estado y barra de pasos. Móvil primero desde 360 px, objetivos táctiles de 44 px, contraste 4.5:1.
  *Cubre:* RNF-02, RNF-03 · *Listo cuando:* se usan en la reserva y se pueden operar con teclado.
- [ ] **F1.12 · Reserva en 4 pasos** — rutas `/b/[slug]` → `barbero` → `hora` → `datos`, con el estado en la URL (`?servicio=…&barbero=…&fecha=…`) para que "atrás" y recargar funcionen. Incluye "Repetir mi último corte", los errores de teléfono inválido, de máximo de citas y de límite por IP, el aviso "Ese horario se acaba de ocupar" (vuelve a la hora sin borrar nombre ni teléfono) y la página "no disponible".
  *Cubre:* RF-01 a RF-09, CU-01, RNF-01 · *Listo cuando:* se completa una reserva real contra la API local.
- [ ] **F1.13 · Confirmación** — `/b/[slug]/listo`: resumen, "Agregar a mi calendario" (.ics), "Cómo llegar" (enlace de mapa) y guardado de los datos en el dispositivo.
  *Cubre:* RF-08, CU-01 paso 10 · *Listo cuando:* ambos botones funcionan en un celular.
- [ ] **F1.14 · Gestión de la cita** — `/c/[token]` (ver) y `/c/[token]/cambiar` (reagendar), cancelar con confirmación, modo solo lectura para citas canceladas o pasadas y, pasado el límite, el contacto de la barbería (wa.me) en lugar de los botones.
  *Cubre:* RF-10 a RF-12, CU-02 a CU-04 · *Listo cuando:* los tres flujos funcionan con la cita creada en F1.12.

### Pruebas y medición

- [ ] **F1.15 · E2E con Playwright** — instalar Playwright y cubrir CU-01 (incluido el choque de turno), CU-03 y CU-04.
  *Cubre:* casos críticos ★ del doc 02 · *Listo cuando:* corren en `make test` y en la CI.
- [ ] **F1.16 · Medir rendimiento y usabilidad** — carga de la página pública menor a 3 s en 4G simulado, disponibilidad menor a 500 ms, reserva en menos de 60 s probada a mano en un celular, y revisión básica de accesibilidad (teclado y contraste).
  *Cubre:* RNF-01, RNF-03, RNF-04 · *Listo cuando:* las mediciones están anotadas en la bitácora.

---

## F2 · Panel

**Objetivo:** que el barbero y el dueño manejen la agenda desde el celular.
**Listo cuando:** un barbero maneja un día completo solo desde el panel.
**Casos de uso:** CU-06 a CU-12 y CU-15. **Necesita:** F0.08, F0.10 y F1.05.

### API

- [ ] **F2.01 · Agenda del día** — `GET /panel/agenda?fecha&miembro`: citas del día con su cliente (`agenda/queries.py`), huecos libres según horario y bloqueos, y el resumen (citas, confirmadas, sin confirmar). El barbero solo ve las suyas por RLS; el dueño filtra por barbero. Un día sin horario responde "No tienes horario este día".
  *Cubre:* RF-23, RF-24, RF-37, CU-07 · *Listo cuando:* una prueba con barbero y dueño confirma qué ve cada uno.
- [ ] **F2.02 · Detalle de la cita** — `GET /panel/citas/{id}`: estado, servicio, datos del cliente, número de visitas y fecha del último corte (`v_clientes_resumen`) e historial de eventos. El historial de avisos lo da `notificaciones` (F3.11), no la agenda, que no puede leer hacia arriba.
  *Cubre:* RF-26, CU-08 · *Listo cuando:* devuelve el detalle con el historial de eventos.
- [ ] **F2.03 · Acciones sobre la cita** — `POST /panel/citas/{id}/acciones`: atendida, no vino (solo después de la hora de inicio), cancelar con motivo opcional, reagendar sin límite de tiempo, reasignar a otro barbero (solo el dueño, validando su disponibilidad) y corrección de un estado final por el dueño dentro de las 24 h. Cada acción registra el evento con su actor y publica el evento de dominio que corresponda.
  *Cubre:* RF-20, RF-27, RN-08, RN-18, CU-08 · *Listo cuando:* pruebas para cada transición permitida y cada una rechazada.
- [ ] **F2.04 · Cita manual** — `POST /panel/citas`: teléfono opcional; si hay teléfono, la casilla de autorización guarda un consentimiento con origen `manual`. Fuera del horario del barbero advierte pero permite guardar; un cruce con otra cita lo impide.
  *Cubre:* RF-28, RN-02, RN-17, CU-09 · *Listo cuando:* una cita sin teléfono o sin autorización queda marcada para no recibir WhatsApp.
- [ ] **F2.05 · Bloqueos** — `POST /panel/bloqueos` (y listar y borrar): rango de horas o días completos con motivo. Solo el dueño bloquea la barbería entera. Si hay citas dentro del rango, las lista y ofrece cancelarlas avisando a los clientes o volver atrás.
  *Cubre:* RF-29, RF-40, RN-02, CU-10 · *Listo cuando:* los turnos bloqueados dejan de aparecer en la reserva pública.
- [ ] **F2.06 · Datos de la barbería y servicios** — `GET, PATCH /panel/barberia` y CRUD de `/panel/servicios`. Cambiar el slug avisa que el enlace anterior deja de funcionar; desactivar un servicio no cambia las citas existentes.
  *Cubre:* RF-32, RF-33, RN-13, CU-11 · *Listo cuando:* los cambios se reflejan de inmediato en la página pública.
- [ ] **F2.07 · Equipo** — `/panel/miembros`: registrar con nombre, correo, WhatsApp y rol; elegir qué servicios presta cada uno; desactivar (sus citas futuras quedan señaladas para el dueño).
  *Cubre:* RF-34, RN-14, CU-11 · *Listo cuando:* un barbero desactivado desaparece de la reserva y sus citas aparecen señaladas.
- [ ] **F2.08 · Horarios y reglas de reserva** — `/panel/horarios` (varias franjas por día; las que se cruzan se rechazan con un error legible a partir de `horarios_sin_solape`) y las reglas de reserva dentro de `/panel/barberia`.
  *Cubre:* RF-35, RF-36, CU-11 · *Listo cuando:* cambiar el intervalo de la grilla cambia los turnos que ofrece la reserva.
- [ ] **F2.09 · Clientes y reportes** — `GET /panel/clientes` (lista, búsqueda e historial) y `GET /panel/reportes` (citas, cancelaciones e inasistencias por barbero en un periodo). Los reportes son prioridad C: pueden esperar.
  *Cubre:* RF-38, RF-39, CU-12 · *Listo cuando:* la lista coincide con `v_clientes_resumen`.
- [ ] **F2.10 · Administración de la plataforma** — `/admin/*`: crear, activar y suspender barberías y registrar a su primer dueño. Verifica que el usuario esté en `admins_plataforma` y usa la conexión de servicio. Reemplaza el alta manual de F0.14.
  *Cubre:* RF-41, RN-16, CU-15 · *Listo cuando:* una barbería suspendida deja de mostrar su página pública y no acepta reservas, pero conserva sus citas.

### Web

- [ ] **F2.11 · Estructura del panel y PWA** — layout protegido con navegación, íconos reales de la PWA, oferta de instalación en el celular y selector de barbero para el dueño.
  *Cubre:* RF-31, CU-06 paso 5 · *Listo cuando:* el panel se instala como aplicación en un celular.
- [ ] **F2.12 · Agenda** — `/panel/agenda`: resumen, citas en orden con su estado, huecos libres, línea de la hora actual, flechas de día anterior y siguiente y vista semanal (prioridad S).
  *Cubre:* RF-23 a RF-25, CU-07 · *Listo cuando:* se ve un día del seed con huecos y citas.
- [ ] **F2.13 · Detalle de cita y acciones** — `/panel/citas/[id]`: datos, historial, botones de atendida, no vino, reagendar, cancelar, y de WhatsApp y llamar (wa.me y `tel:`, que no aparecen si no hay teléfono). El historial de avisos se conecta en F3.11.
  *Cubre:* RF-26, RF-27, CU-08 · *Listo cuando:* cada acción cambia el estado y la agenda lo refleja.
- [ ] **F2.14 · Cita manual y bloqueos** — `/panel/citas/nueva` (desde el "+" o desde un hueco libre) y `/panel/bloqueos`.
  *Cubre:* RF-28, RF-29, RF-40, CU-09, CU-10 · *Listo cuando:* tocar un hueco prellena la hora.
- [ ] **F2.15 · Ajustes y clientes** — `/panel/ajustes` (datos, servicios, equipo, horarios y reglas) y `/panel/clientes`.
  *Cubre:* RF-32 a RF-36, RF-38, CU-11, CU-12 · *Listo cuando:* un dueño configura una barbería nueva sin tocar la base.
- [ ] **F2.16 · Agenda en vivo** — `use-agenda-en-vivo`: suscripción de Realtime a `citas` que vuelve a pedir la agenda cuando llega un cambio. La RLS aplica también a Realtime.
  *Cubre:* RF-30 · *Listo cuando:* con el panel abierto, una reserva hecha desde la página pública aparece sin recargar, y un barbero no recibe cambios de las citas de otro.

### Pruebas

- [ ] **F2.17 · Pruebas de permisos** — pgTAP para las demás políticas RLS (un barbero no administra servicios ni miembros; los bloqueos de toda la barbería solo los crea el dueño) y pruebas de API de barbero frente a dueño.
  *Cubre:* RNF-08 · *Listo cuando:* cada fila de la tabla de permisos del doc 04 §4.5 tiene una prueba.
- [ ] **F2.18 · Jornada completa** — recorrer un día entero desde el celular: iniciar sesión, ver la agenda, atender, marcar "No vino", crear una cita manual, bloquear el almuerzo y reagendar. Agregar el E2E de Playwright del panel.
  *Cubre:* CU-06 a CU-10 · *Listo cuando:* se completa sin recurrir a la base ni a la API a mano. **Cierra la fase.**

---

## F3 · WhatsApp

**Objetivo:** recordatorios y avisos que salen a tiempo, sin duplicados, y respuestas que actualizan la cita.
**Listo cuando:** el ciclo completo de recordatorios funciona con el número real.
**Casos de uso:** CU-05, CU-13, CU-14. **Necesita:** F1 y avance del trámite con Meta (F0.11).

### Preparación

- [ ] **F3.01 · Escribir el doc 05 y enviar las plantillas** — nombre, idioma, variables y botones de cada plantilla, el formato del *payload* de los botones (por ejemplo `CANCELAR:<cita_id>`) y la forma de los eventos del webhook. Todas de categoría *utilidad*, sin lenguaje promocional. Se envían a aprobación de Meta.
  *Cubre:* ADR-0001, RF-13 a RF-15 · *Listo cuando:* el doc está escrito y las plantillas están enviadas.

### Dominio `notificaciones`

- [ ] **F3.02 · Puerto y proveedor de consola** — `ports.py` con `ProveedorNotificaciones` y `ResultadoEnvio`, y `proveedores/consola.py`, que imprime el mensaje y un enlace wa.me.
  *Cubre:* ADR-0006 · *Listo cuando:* se puede enviar una plantilla de prueba en local sin Meta.
- [ ] **F3.03 · Programador (función pura)** — `programador.py`: `programar(cita, ahora) -> list[NotificacionNueva]`. Confirmación inmediata, recordatorio de 24 h (solo si faltan más de 26 h), recordatorio de 2 h (solo si faltan más de 3 h, y con botones si no hubo el de 24 h), horario silencioso de 9:00 p. m. a 7:00 a. m., aviso de cambio al reagendar y aviso al barbero de "sin confirmar" 60 minutos antes (RN-09).
  *Cubre:* RF-13 a RF-15, RF-18, RN-07, RN-09 · *Listo cuando:* pruebas de tabla con los ejemplos del doc 01 §4 (cita del jueves 6:40 p. m. y cita de hoy a la 1:00 p. m.).
- [ ] **F3.04 · Manejadores de eventos** — `handlers.py` escucha `CitaCreada` (programa las notificaciones), `CitaReagendada` (anula las pendientes y reprograma) y `CitaCancelada` (anula y avisa al barbero o al cliente), todo en la transacción de la agenda. No se programan mensajes para clientes sin teléfono o sin autorización (RN-17). `main.py` y `worker.py` importan los manejadores al arrancar.
  *Cubre:* RF-18, RF-20, RN-17 · *Listo cuando:* crear una cita deja filas en `notificaciones`, reagendar deja las anteriores en `anulada` y repetir el evento no duplica filas.
- [ ] **F3.05 · Worker de envío** — `envio.py`: toma un lote vencido con `FOR UPDATE SKIP LOCKED`, comprueba que siga aplicando (la cita activa; "sin confirmar" solo si sigue `pendiente`), arma la plantilla, la envía, guarda el `wamid` y pasa a `enviada`. Error temporal: vuelve a `pendiente` unos minutos después, hasta 3 intentos. Error permanente: `fallida` con su código. Límite diario de Meta: reprograma y avisa al administrador. `worker.py` elige el proveedor según `NOTIFICACIONES_PROVEEDOR`. Hay que fijar el ritmo de ejecución: los docs dicen "cada minuto" y "cada 5 minutos".
  *Cubre:* RNF-06, RNF-07, RNF-17, CU-13 · *Listo cuando:* con `ConsolaProvider`, dos workers a la vez no envían nunca el mismo mensaje y una notificación sale dentro de los 5 minutos de su hora.
- [ ] **F3.06 · Resumen diario del barbero** — a la hora configurada por cada barbero, el worker programa su resumen del día.
  *Cubre:* RF-19 (prioridad S) · *Listo cuando:* un barbero con `recibe_avisos` recibe su resumen a la hora que eligió.
- [ ] **F3.07 · Salud del worker** — `GET /health/notificaciones` responde 503 si hay notificaciones pendientes con más de 10 minutos de atraso.
  *Cubre:* doc 03 §11 · *Listo cuando:* la prueba fuerza un atraso y recibe el 503.

### Dominio `mensajeria`

- [ ] **F3.08 · Cliente y proveedor de WhatsApp** — `whatsapp/cliente.py` (HTTP a la Cloud API), `plantillas.py` (nombres y variables del doc 05) y `proveedor.py` (`WhatsAppCloudProvider`, que implementa el puerto). Probar con el número de prueba de Meta y un túnel (ngrok) o la API desplegada.
  *Cubre:* ADR-0001, ADR-0006 · *Listo cuando:* un recordatorio real llega a un celular de prueba.
- [ ] **F3.09 · Webhook** — `GET /webhooks/whatsapp` (verificación) y `POST`: valida la firma `X-Hub-Signature-256` (si no es válida, 401 y no se guarda nada), inserta el evento crudo con su clave de deduplicación, responde 200 de inmediato, procesa después y marca `procesado_at` o `error`.
  *Cubre:* RNF-07, RNF-09, CU-14 · *Listo cuando:* una firma inválida da 401 y el mismo evento enviado dos veces se procesa una sola.
- [ ] **F3.10 · Traductor y respuestas automáticas** — `traductor.py` (capa anticorrupción): los estados enviado, entregado, leído y fallido actualizan la notificación; "Confirmo" confirma la cita; "Cancelar" la cancela dentro del límite o responde con el contacto de la barbería fuera de él; "Reagendar" responde con el enlace de gestión; una respuesta a una cita ya cancelada, atendida o pasada no la modifica (RN-15); un mensaje libre recibe el enlace de gestión y el contacto de la barbería.
  *Cubre:* RF-16, RF-17, RF-21, RN-06, RN-15, CU-05 · *Listo cuando:* se cumplen los criterios de aceptación de RF-16 del doc 01 §4.

### Panel y privacidad

- [ ] **F3.11 · Historial de avisos** — endpoint en `notificaciones` con los avisos de una cita y su estado de entrega (los fallidos con su código de error) y el componente en la web (`domains/notificaciones`) dentro del detalle de la cita. Vista de administración de notificaciones y errores por barbería.
  *Cubre:* RF-42, RNF-17 · *Listo cuando:* el barbero ve en el detalle si el recordatorio llegó, se leyó o falló.
- [ ] **F3.12 · Supresión de datos y retención** — endpoint de administración que llama a `anonimizar_cliente` y publica `ClienteAnonimizado`; el manejador de `notificaciones` borra el teléfono y las variables de sus filas y anula las pendientes. Tarea diaria que borra `whatsapp_eventos` con más de 90 días.
  *Cubre:* RF-43, RNF-11, CU-16 · *Listo cuando:* tras anonimizar a un cliente no queda su teléfono en ninguna tabla.

### Pruebas con el número real

- [ ] **F3.13 · Pruebas de integración** — `tests/integration/` para CU-05, CU-13 y CU-14 con `ConsolaProvider` y con eventos de Meta simulados.
  *Cubre:* casos críticos ★ del doc 02 · *Listo cuando:* corren en la CI.
- [ ] **F3.14 · Ciclo completo con el número real** — plantillas aprobadas, número registrado y token permanente. Recorrido: reservar → confirmación → recordatorio con botones → tocar "Confirmo" → cita confirmada → aviso al barbero.
  *Cubre:* todos los RF de la sección C del doc 01 · *Listo cuando:* el recorrido funciona de punta a punta en producción o con el número real. **Cierra la fase.**

---

## F4 · Piloto

**Objetivo:** probar el producto con barberías reales y medir si resuelve el problema.
**Listo cuando:** 2–3 barberías lo usan durante 4 semanas seguidas.
**Necesita:** F2 y F3.

- [ ] **F4.01 · Documentos 07, 08 y 09** — pruebas, seguridad y privacidad, y despliegue y operación.
  *Listo cuando:* los tres docs existen y los enlaces de los demás docs apuntan a ellos.
- [ ] **F4.02 · Cerrar las decisiones pendientes** — P-03 (hosting de producción), P-04 (precios para las barberías), P-05 (valores por defecto de las reglas, validados con las barberías) y P-06 (presupuesto mensual). Cada una queda escrita en el doc 00 §7 y, si corresponde, en un ADR.
  *Listo cuando:* no queda ninguna decisión pendiente que bloquee el piloto.
- [ ] **F4.03 · Producción** — Supabase en plan pago (los gratuitos se pausan), servicios `web`, `api` y `worker` en Railway con las rutas de despliegue por carpeta, variables de entorno, SMTP propio en Supabase Auth, dominio y el environment `produccion` del workflow de migraciones con revisores.
  *Cubre:* RNF-14, RNF-15 · *Listo cuando:* un cambio en `main` se despliega y las migraciones se aplican con aprobación manual.
- [ ] **F4.04 · Cumplimiento legal** — política de tratamiento de datos publicada y enlazada en la reserva, versión del texto registrada en cada consentimiento y procedimiento de supresión dentro de los 15 días hábiles.
  *Cubre:* RF-06, RNF-11, Ley 1581 · *Listo cuando:* la política está publicada y un simulacro de supresión funciona.
- [ ] **F4.05 · Observabilidad** — Sentry en los tres servicios, logs JSON y un monitor externo que consulta `/health/notificaciones` cada 5 minutos y avisa.
  *Cubre:* RNF-14, RNF-17, doc 03 §11 · *Listo cuando:* un fallo provocado a propósito genera una alerta.
- [ ] **F4.06 · Revisión de seguridad** — secretos fuera del repositorio, CORS limitado a la web, firma del webhook, RLS activada en todas las tablas, toda consulta con la llave de servicio filtrada por `barberia_id` (con pruebas) y límites contra abuso.
  *Cubre:* RNF-08 a RNF-10, RN-11 · *Listo cuando:* la lista está revisada y anotada en el doc 08.
- [ ] **F4.07 · Preparar las barberías piloto** — alta de cada barbería, carga de servicios, equipo y horarios, enlace público, capacitación a los barberos y comprobación del límite de 250 clientes distintos cada 24 horas del número sin verificar.
  *Cubre:* RF-41, CU-15 · *Listo cuando:* cada barbería recibe su primera reserva real.
- [ ] **F4.08 · Medición** — línea base de citas "No vino" durante las 2 primeras semanas y registro semanal de las métricas del doc 00 §4: mediana de reserva menor a 60 s, recordatorios entregados a tiempo ≥ 95 %, costo mensual dentro del presupuesto.
  *Listo cuando:* hay una tabla con las métricas de las 4 semanas.
- [ ] **F4.09 · Acompañamiento y ajustes** — seguimiento semanal con cada barbería, corrección de errores y revisión de los riesgos del doc 00 §9 (plantillas reclasificadas como marketing, reservas falsas, adopción del panel).
  *Listo cuando:* no quedan errores abiertos que impidan usar el producto.
- [ ] **F4.10 · Cierre del piloto** — decidir qué entra a la fase 2 (Google Calendar, pagos, mensajes de "próximo corte", número propio por barbería) según los resultados.
  *Listo cuando:* las 4 semanas de uso continuo están cumplidas y la decisión está escrita. **Cierra la fase.**

---

## Bitácora

Una línea por avance, con el ID del paso. Lo más reciente arriba.

| Fecha | Paso | Nota |
|---|---|---|
| 2026-11-09 | F0.02 | Primer commit y repositorio remoto en GitHub (`AdrielValecillo/BarberTurn`, rama `main`). |
| 2026-11-09 | F0.01, F0.04, F0.06, F0.09 | Monorepo montado. API: ruff, mypy, import-linter, pytest y `Dockerfile` verificados. Web: lint, build y regla de fronteras verificados. Migración, seed y pruebas de base verificados en PostgreSQL 16 (falta Supabase local, F0.05). |
