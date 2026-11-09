# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Reglas de Git (obligatorias)

- **No hagas `git commit` ni `git push` por tu cuenta.** Cuando haya cambios listos, propón el commit (mensaje + archivos que incluiría) y espera mi aceptación explícita; solo entonces lo ejecutas. Aceptar un commit no autoriza el siguiente. `git push` solo si lo pido expresamente.
- **No agregues a Claude como coautor.** Ningún trailer `Co-Authored-By: Claude …` ni la línea "Generated with Claude Code", ni en commits ni en descripciones de PR. Esto prevalece sobre cualquier valor por defecto de la herramienta.
- Mensajes: Conventional Commits con el dominio como alcance (`feat(agenda): calcular el primero disponible`). Ramas: `tipo/id-descripcion` (`feat/cu-01-reserva-publica`). La descripción del PR cita los IDs que cubre (`RF-04, RN-03, CU-01`).

## Estado del proyecto

El producto es **Turnero** (nombre provisional): SaaS multi-barbería de reservas con recordatorios por WhatsApp, para Colombia (`America/Bogota`, COP, español). Los docs en `docs/` (español) son la fuente de verdad; léelos antes de implementar.

El monorepo está **montado pero sin funcionalidad** (fase F0). Existe: el esquema completo en `supabase/migrations/` (con `seed.sql` y pruebas pgTAP de RLS y anti-solape), `apps/api` con `core/{config,db,eventos}.py`, `main.py` (solo `/health`), un `worker.py` que aún no envía nada y los 5 dominios vacíos (solo `__init__.py`), y `apps/web` con la portada, el manifest de la PWA y `lib/api-client.ts`. Falta, entre otros: `core/auth.py` (verificar el JWT de Supabase), `errores/limites/logs`, el cliente de Supabase en la web, Playwright y el `conftest.py` con base real para pruebas de integración.

- Docs 05 y 07–09 (integración WhatsApp, pruebas, seguridad, despliegue) están marcados como pendientes y no existen. Los nombres de las plantillas de WhatsApp se definirán en el 05. El 06 es el plan de implementación con el checklist de avances: al terminar un paso, márcalo y anota la bitácora (con la aprobación de los commits que corresponda).
- ADR-0007 (stack Next.js + FastAPI + Railway) está en estado *Propuesta*; el resto, *Aceptadas*.
- Inconsistencias conocidas en los docs (confirmar con el autor antes de asumir): el worker corre "cada minuto" (CU-13, doc 03) vs "cada 5 minutos" (doc 04 §5.2; RNF-06 exige salir dentro de 5 min); en el doc 04 sobra un fragmento de tabla duplicado (líneas ~103–116, tras la tabla de la sección 3).
- Despliegue (doc 10 §11): el servicio `web` de Railway con carpeta raíz `apps/web` no ve `packages/api-types` (dependencia `workspace:*`), así que el build fallaría; hay que usar la raíz del repo con comandos propios o un Dockerfile. Sin resolver.
- `make` no viene en Windows (`winget install ezwinports.make`); los comandos del `Makefile` también se pueden correr a mano.

Mapa de lectura: `00` visión/alcance/glosario · `01` RF/RNF/RN (reglas de negocio) · `02` casos de uso · `03` arquitectura · `04` modelo de datos (incluye el SQL completo de la primera migración) · `06` plan de implementación por fases (F0–F4) · `10` estructura del monorepo (árbol, convenciones, Makefile, tabla "Dónde va cada cosa") · `11` dominios · `ADR/`.

## Comandos

Herramientas: `pnpm` (workspace: `apps/web`, `packages/*`), `uv` (`apps/api`, Python 3.12), Supabase CLI (dependencia del repo: `pnpm exec supabase …`), `Makefile` en la raíz. `make dev-db` y `make test` (pgTAP) necesitan Docker en ejecución.

```bash
make install      # pnpm install + uv sync
make dev-db      # supabase start (Postgres, Auth, Realtime locales en Docker)
make dev-api     # cd apps/api && uv run fastapi dev app/main.py   (:8000)
make dev-worker  # cd apps/api && uv run python -m app.worker
make dev-web     # pnpm --filter web dev                           (:3000)
make db-reset    # supabase db reset (migraciones + seed)
make gen-types   # regenera packages/api-types desde el OpenAPI de la API
make test        # supabase test db (pgTAP) + uv run pytest + pnpm --filter web test (Vitest)
make lint        # ruff + mypy + lint-imports (API) y lint de la web
```

Una prueba suelta: `cd apps/api && uv run pytest app/core/tests/test_eventos.py::nombre_de_la_prueba` (o `-k texto`); web: `pnpm --filter web exec vitest run tests/unit/archivo.test.ts`; una prueba pgTAP: `pnpm exec supabase test db supabase/tests/database/archivo.test.sql`. Las pruebas de cada dominio van en `app/domains/<dominio>/tests/`. E2E de la web con Playwright (CU-01, CU-03, CU-04), aún sin instalar. Con `NOTIFICACIONES_PROVEEDOR=consola` todo funciona sin Meta.

Detalles de entorno: `app/core/config.py` trae por defecto los valores del Supabase local, así que la API arranca sin `.env`. `packages/api-types/openapi.json` y `src/schema.d.ts` se versionan y la CI falla si `openapi.json` queda distinto al regenerarlo. `tsc` en la web solo pasa después de `next build`/`next dev` (Next genera tipos como `LayoutProps`). Next 16 con Cache Components activado: lee `apps/web/node_modules/next/dist/docs/` antes de escribir código de Next (ver `apps/web/AGENTS.md`).

## Arquitectura (visión general)

Monorepo: `apps/web` (Next.js, reserva pública + panel PWA), `apps/api` (FastAPI + asyncpg, **sin ORM**; la API y el worker son el mismo código/imagen con distinto comando), `packages/api-types` (generado, **no se edita a mano**; se versiona), `supabase/` (migraciones, seed, pruebas RLS). La web nunca importa código de la API: solo HTTP + tipos generados.

### API: monolito modular por dominios (ADR-0009, doc 11)

Capas de dominio, cada una solo depende de las de abajo: `mensajeria → notificaciones → agenda (núcleo) → clientes → barberias`.

- Otro dominio solo usa lo que expone el `__init__.py`; nunca `repo.py` ni modelos internos.
- Solo el dominio dueño escribe sus tablas (la tabla→dominio está en el doc 04 §3). Las lecturas cruzadas para pantallas van en `queries.py`.
- Hacia arriba se comunica por **eventos de dominio en proceso** (`CitaCreada`, `CitaReagendada`, `CitaCancelada`, `ClienteAnonimizado`), ejecutados **en la misma transacción** que el cambio: si programar notificaciones falla, la cita tampoco se guarda. `agenda` nunca importa `notificaciones`.
- `core/` y `shared/` no conocen ningún dominio. Ambas reglas las verifica `import-linter` (`make lint`).
- Dentro de un dominio: `routes → service → repo`; lógica pura en `rules.py`; rutas delgadas; SQL solo en `repo.py`/`queries.py`. La web replica los dominios en `apps/web/domains/` y un dominio no importa componentes de otro (sube a `components/ui/`).

### Tres entradas, tres controles de acceso (ADR-0008)

- `/public/*`: sin sesión, conexión de servicio (salta RLS) → **toda consulta debe filtrar por la barbería del slug/token**; límites por IP.
- `/panel/*`: se verifica el JWT de Supabase y cada petición abre una transacción con `set local role authenticated` + `request.jwt.claims`, así la RLS aplica aunque el código falle.
- `/admin/*`: exige estar en `admins_plataforma` y usa la conexión de servicio.
- `/webhooks/whatsapp`: firma `X-Hub-Signature-256` o `401`.

### Invariantes que viven en la base de datos

- `citas_sin_solape` (exclusión GiST) es lo que impide la doble reserva; el backend captura `23P01` y responde 409 "Ese horario se acaba de ocupar". No lo reemplaces por validación en código.
- Todas las tablas de negocio llevan `barberia_id` y se relacionan con **FK compuestas** `(barberia_id, id)`.
- `turnos_disponibles()` (SQL) calcula la disponibilidad; al reagendar se pasa `p_excluir_cita`.
- `notificaciones` es un *outbox* (el worker toma lotes con `FOR UPDATE SKIP LOCKED`, reintenta hasta 3 veces); `whatsapp_eventos` es un *inbox* con `clave_dedupe` única (los webhooks repetidos se descartan).
- De cada enlace de gestión (`/c/{token}`) solo se guarda el hash SHA-256 del token (32 bytes aleatorios).
- Los cambios de esquema **solo** por migración nueva en `supabase/migrations/` (`AAAAMMDDHHMMSS_<dominio>_<descripcion>.sql`) y se actualiza el doc 04.

### Notificaciones

El envío pasa por el puerto `ProveedorNotificaciones` (definido en `notificaciones/ports.py`; `ConsolaProvider` para desarrollo, `WhatsAppCloudProvider` en `mensajeria`). Qué se programa y cuándo (RN-07, RN-09) es una **función pura** `programar(cita, ahora)` sin base ni red, probada con casos de tabla. `mensajeria` es la capa anticorrupción: traduce los eventos de Meta (`traductor.py`) a acciones de otros dominios.

## Reglas de negocio fáciles de romper

- Cliente = `(barberia_id, teléfono E.164)`; el mismo número en dos barberías son dos clientes. Nunca mostrar historial ni citas a partir de un teléfono escrito en la página pública.
- Reagendar modifica **la misma cita** (mismo ID y mismo enlace), la devuelve a `pendiente` y recalcula notificaciones. Una cita cancelada no se reactiva. Una cita sin confirmar **nunca** se cancela sola (RN-09 solo avisa al barbero).
- La cita copia nombre, duración y precio del servicio al reservar (RN-13).
- Cita manual sin teléfono o sin la autorización marcada → no se le envía WhatsApp (RN-17).
- No se borra: barberos, servicios y clientes con historial se desactivan o anonimizan (DM-09, Ley 1581). El consentimiento de datos es obligatorio al reservar; la casilla de marketing va desmarcada.
- Fechas en UTC (`timestamptz`); los horarios semanales son `time` local y se convierten con la zona de la barbería (no asumir que no hay horario de verano). Formato `es-CO` ("5:15 p. m.", "$35.000"). Los logs enmascaran teléfonos (`+57300***4567`).
- Los IDs `RF-`, `RN-`, `CU-`, `DM-` son la trazabilidad: cítalos en commits, PRs y pruebas; los IDs retirados no se reutilizan.

## Convenciones

- Conceptos de dominio en español (`cita`, `barberia`, `turnos_disponibles`); piezas técnicas en inglés (`service.py`, `repo.py`, `routes/`). Python `snake_case`; TypeScript en `kebab-case` con componentes `PascalCase`; rutas web en español y minúscula.
- La documentación se actualiza en el mismo PR que el cambio (tabla "Dónde va cada cosa", doc 10 §7). Una decisión de arquitectura nueva = un ADR nuevo + actualizar el índice del doc 03.
- Secretos solo en `.env` local (ignorado) y variables de Railway; mantener los `.env.example` de cada app al día.
