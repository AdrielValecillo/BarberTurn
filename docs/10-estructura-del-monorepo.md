# 10 · Estructura del monorepo

| | |
|---|---|
| **Versión del documento** | 0.1 (borrador) |
| **Fecha** | 7 de noviembre de 2026 |
| **Documentos relacionados** | [03 · Arquitectura](03-arquitectura.md), [04 · Modelo de datos](04-modelo-de-datos.md), [11 · Dominios](11-dominios.md), [ADR-0007](adr/0007-stack-nextjs-fastapi-railway.md) |

---

## 1. Principios

1. **Un solo repositorio** para la web, la API, el worker, la base de datos y la documentación. Un cambio que toca la base, la API y la pantalla va en un mismo *pull request*.
2. **Las apps no comparten código, comparten contratos.** La web nunca importa código de la API: habla con ella por HTTP, con tipos generados desde el OpenAPI.
3. **La base de datos solo cambia por migraciones** en `supabase/migrations/`.
4. **La documentación vive junto al código** en `docs/` y se actualiza en el mismo *pull request* que el cambio.
5. **El código se organiza por dominios** (agenda, barberias, clientes, notificaciones, mensajeria), no por capas técnicas. Ver el [doc 11](11-dominios.md).
6. **Cada cosa tiene un solo lugar.** Si dudas dónde va algo, consulta la sección 7.

## 2. Herramientas

| Necesidad | Herramienta | Alcance |
|---|---|---|
| Paquetes de JavaScript y espacio de trabajo | **pnpm** (workspaces) | `apps/web` y `packages/*` |
| Paquetes y entorno de Python | **uv** | `apps/api` |
| Base de datos local, migraciones y pruebas de RLS | **Supabase CLI** | `supabase/` |
| Comandos comunes para ambos lenguajes | **Makefile** en la raíz | Todo el repo |

Con una sola app de JavaScript no hace falta Turborepo ni Nx; si el repo crece, se puede agregar después sin mover carpetas.

---

## 3. Vista general

```text
turnero/
├── apps/
│   ├── web/                  # Next.js: reserva pública y panel (PWA)
│   └── api/                  # FastAPI: API, webhook de WhatsApp y worker
├── packages/
│   └── api-types/            # Tipos de TypeScript generados desde el OpenAPI de la API
├── supabase/                 # Configuración, migraciones, datos de prueba y pruebas de RLS
├── docs/                     # Documentación del proyecto y decisiones (ADR)
├── .github/                  # CI y plantilla de pull request
├── .editorconfig
├── .gitignore
├── CLAUDE.md                 # Contexto para asistentes de IA
├── Makefile                  # make dev, make test, make db-reset…
├── README.md                 # Cómo levantar el proyecto en 5 minutos
├── package.json              # Scripts de la raíz
└── pnpm-workspace.yaml
```

### Reglas de dependencia

```mermaid
flowchart LR
    web["apps/web"] -->|importa tipos| types["packages/api-types"]
    web -->|HTTP| api["apps/api"]
    api -->|genera openapi.json| types
    api -->|SQL| db["supabase/migrations"]
    web -->|Auth y Realtime| supa["Supabase"]
```

- `apps/web` **nunca** importa nada de `apps/api`.
- `packages/api-types` solo contiene archivos generados: no se editan a mano.
- Las migraciones son la única forma de cambiar el esquema.

---

## 4. `apps/web` (Next.js)

`app/` solo define rutas; los componentes, hooks y llamadas a la API viven en `domains/`, con los mismos dominios que la API ([doc 11](11-dominios.md)).

```text
apps/web/
├── app/                                # Solo rutas: cada página arma piezas de los dominios
│   ├── layout.tsx                      # Layout raíz, fuentes, idioma es-CO
│   ├── manifest.ts                     # Manifiesto de la PWA
│   ├── (publico)/
│   │   ├── b/[slug]/                   # CU-01 · Reserva en 4 pasos
│   │   │   ├── page.tsx                # Paso 1: servicio
│   │   │   ├── barbero/page.tsx        # Paso 2: barbero
│   │   │   ├── hora/page.tsx           # Paso 3: día y hora
│   │   │   ├── datos/page.tsx          # Paso 4: nombre y WhatsApp
│   │   │   └── listo/page.tsx          # Confirmación
│   │   └── c/[token]/
│   │       ├── page.tsx                # CU-02 · Ver la cita
│   │       └── cambiar/page.tsx        # CU-03 · Reagendar
│   └── panel/
│       ├── login/page.tsx              # CU-06
│       └── (protegido)/
│           ├── layout.tsx              # Verifica la sesión, barra de navegación
│           ├── agenda/page.tsx         # CU-07
│           ├── citas/
│           │   ├── nueva/page.tsx      # CU-09
│           │   └── [id]/page.tsx       # CU-08
│           ├── bloqueos/page.tsx       # CU-10
│           ├── clientes/page.tsx       # CU-12
│           └── ajustes/                # CU-11
│               ├── page.tsx
│               ├── servicios/page.tsx
│               ├── equipo/page.tsx
│               ├── horarios/page.tsx
│               └── reglas/page.tsx
├── domains/
│   ├── agenda/
│   │   ├── reserva/                    # Lista de servicios, selector de barbero, grilla de turnos, resumen
│   │   ├── gestion/                    # Ver, reagendar y cancelar con el token
│   │   ├── panel/                      # Agenda del día, fila de cita, línea de "ahora", cita manual, bloqueos
│   │   ├── horarios/                   # Editor de horarios semanales
│   │   ├── hooks/
│   │   │   └── use-agenda-en-vivo.ts   # Suscripción de Realtime a citas
│   │   └── api.ts                      # Llamadas a los endpoints de agenda
│   ├── barberias/                      # Inicio de sesión, datos, servicios, equipo y reglas
│   ├── clientes/                       # Lista, historial y casilla de autorización
│   └── notificaciones/                 # Historial de avisos de una cita
├── components/
│   └── ui/                             # Botón, campo, chip de estado, barra de pasos (sin dominio)
├── lib/
│   ├── api-client.ts                   # Cliente HTTP base, tipado con @turnero/api-types
│   ├── fechas.ts                       # Formato es-CO con la zona de la barbería
│   ├── telefono.ts                     # Validación y formato de +57
│   ├── dispositivo.ts                  # "Repetir mi último corte" (solo en el dispositivo)
│   └── supabase/
│       ├── cliente.ts                  # Sesión y Realtime en el navegador
│       └── servidor.ts                 # Sesión en componentes de servidor
├── public/
│   └── iconos/                         # Íconos de la PWA
├── tests/
│   ├── unit/                           # Vitest: fechas, teléfonos, componentes
│   └── e2e/                            # Playwright: CU-01, CU-03, CU-04
├── .env.example
├── next.config.ts
├── package.json
└── tsconfig.json
```

**Por qué cada paso de la reserva es una ruta:** el estado viaja en la URL (`?servicio=…&barbero=…&fecha=…`). Así el botón "atrás" del celular funciona como el cliente espera, y recargar la página no pierde lo que eligió.

---

## 5. `apps/api` (FastAPI y worker)

Monolito modular: un paquete por dominio dentro de `app/domains/`, más `core/` y `shared/`, que no conocen ningún dominio. Las reglas de frontera y la anatomía de cada dominio están en el [doc 11](11-dominios.md).

```text
apps/api/
├── app/
│   ├── main.py                         # Monta las rutas de cada dominio y registra los manejadores de eventos
│   ├── worker.py                       # Elige el proveedor (consola o WhatsApp) y corre los trabajos
│   ├── export_openapi.py               # Escribe openapi.json para generar los tipos de la web
│   ├── core/                           # Infraestructura técnica
│   │   ├── config.py                   # Variables de entorno (pydantic-settings)
│   │   ├── db.py                       # Pool de asyncpg y contexto RLS por petición (ADR-0008)
│   │   ├── auth.py                     # Verificación del JWT de Supabase
│   │   ├── eventos.py                  # Bus de eventos de dominio en proceso
│   │   ├── errores.py                  # Errores de dominio y su respuesta HTTP
│   │   ├── limites.py                  # Límites por IP (RN-11)
│   │   └── logs.py                     # Logs JSON, teléfonos enmascarados
│   ├── shared/
│   │   ├── telefono.py                 # Teléfono en E.164
│   │   └── tiempo.py                   # Zonas horarias
│   └── domains/
│       ├── barberias/                  # Soporte · la base, no depende de nadie
│       │   ├── __init__.py             # API pública del dominio
│       │   ├── acceso.py               # miembro_actual: miembro y rol del usuario con sesión
│       │   ├── models.py
│       │   ├── service.py
│       │   ├── repo.py
│       │   ├── schemas.py
│       │   ├── routes/
│       │   │   ├── public.py           # Datos públicos de la barbería
│       │   │   ├── panel.py            # Ajustes, servicios, equipo, reglas
│       │   │   └── admin.py            # Alta y suspensión de barberías
│       │   └── tests/
│       ├── clientes/                   # Soporte · depende de barberias
│       │   ├── __init__.py
│       │   ├── models.py
│       │   ├── service.py              # registrar, consentimientos, anonimizar
│       │   ├── repo.py
│       │   ├── events.py               # ClienteAnonimizado
│       │   ├── schemas.py
│       │   ├── routes/
│       │   │   ├── panel.py
│       │   │   └── admin.py            # Supresión de datos
│       │   └── tests/
│       ├── agenda/                     # NÚCLEO · depende de barberias y clientes
│       │   ├── __init__.py
│       │   ├── models.py               # Cita, EstadoCita, Turno, Horario, Bloqueo
│       │   ├── rules.py                # Transiciones (RN-08), grilla (RN-03), primero disponible (RN-05)
│       │   ├── service.py              # crear_cita, reagendar, cancelar, confirmar, marcar…
│       │   ├── repo.py
│       │   ├── queries.py              # Agenda del día, detalle, resumen de visitas, reportes
│       │   ├── events.py               # CitaCreada, CitaReagendada, CitaCancelada
│       │   ├── schemas.py
│       │   ├── routes/
│       │   │   ├── public.py           # Turnos, crear cita, gestión con token, .ics
│       │   │   └── panel.py            # Agenda, acciones, citas manuales, bloqueos, horarios
│       │   └── tests/
│       ├── notificaciones/             # Soporte · depende de agenda, clientes y barberias
│       │   ├── __init__.py
│       │   ├── ports.py                # ProveedorNotificaciones (ADR-0006)
│       │   ├── programador.py          # RN-07 y RN-09 como funciones puras
│       │   ├── handlers.py             # Escucha los eventos de agenda y clientes
│       │   ├── envio.py                # Trabajo del worker: envíos, reintentos, resumen diario
│       │   ├── repo.py
│       │   ├── proveedores/
│       │   │   └── consola.py          # Para desarrollo
│       │   ├── routes/
│       │   │   └── admin.py            # Registro de envíos y errores
│       │   └── tests/
│       └── mensajeria/                 # Genérico · depende de todos los de abajo
│           ├── __init__.py
│           ├── whatsapp/
│           │   ├── cliente.py          # Llamadas HTTP a la Cloud API
│           │   ├── firma.py            # X-Hub-Signature-256
│           │   └── plantillas.py       # Nombres y variables de las plantillas (doc 05)
│           ├── proveedor.py            # WhatsAppCloudProvider: implementa el puerto de notificaciones
│           ├── traductor.py            # Eventos de Meta → acciones de los dominios
│           ├── service.py              # Deduplica y despacha cada evento
│           ├── repo.py
│           ├── routes/
│           │   └── webhook.py          # GET y POST /webhooks/whatsapp
│           └── tests/
├── tests/
│   ├── conftest.py                     # Base de prueba con las migraciones aplicadas
│   └── integration/                    # Flujos de punta a punta entre dominios (CU-01, CU-05…)
├── Dockerfile                          # La misma imagen sirve para la API y el worker
├── pyproject.toml                      # Incluye los contratos de import-linter
├── uv.lock
└── .env.example
```

**Capas dentro de cada dominio:** `routes → service → repo`, con la lógica pura en `rules.py` y las lecturas para pantallas en `queries.py`. Otro dominio solo usa lo que este expone en `__init__.py`.

**Pruebas junto a cada dominio:** las unitarias viven en `domains/<dominio>/tests/`; las que cruzan varios dominios, en `tests/integration/`.

**SQL explícito con asyncpg, sin ORM:** las piezas clave del sistema (restricción de exclusión, RLS, `FOR UPDATE SKIP LOCKED`, `turnos_disponibles`) son de PostgreSQL. Escribirlas en SQL directo es más claro que pelear con un ORM.

---

## 6. `packages/`, `supabase/`, `docs/` y `.github/`

```text
packages/
└── api-types/
    ├── openapi.json                    # Generado por apps/api/app/export_openapi.py
    ├── src/schema.d.ts                 # Generado con openapi-typescript
    └── package.json                    # Nombre: @turnero/api-types

supabase/
├── config.toml                         # Creado por supabase init
├── migrations/
│   └── 20261107000000_esquema_inicial.sql   # El SQL del doc 04
├── seed.sql                            # Barbería de ejemplo, dos barberos, servicios y horarios
└── tests/
    └── database/
        └── rls_citas.test.sql          # pgTAP: un barbero no ve citas ajenas

docs/
├── 00-vision-y-alcance.md
├── 01-requerimientos.md
├── 02-casos-de-uso.md
├── 03-arquitectura.md
├── 04-modelo-de-datos.md
├── 05-integracion-whatsapp.md          # Pendiente
├── 06-plan-de-implementacion.md        # Checklist de avances por fase
├── 07-pruebas.md                       # Pendiente
├── 08-seguridad-y-privacidad.md        # Pendiente
├── 09-despliegue-y-operacion.md        # Pendiente
├── 10-estructura-del-monorepo.md       # Este documento
├── 11-dominios.md
└── adr/
    ├── 0000-plantilla.md
    └── 0001-… a 0009-…

.github/
├── workflows/
│   ├── ci-api.yml                      # Se activa con cambios en apps/api, supabase o packages
│   ├── ci-web.yml                      # Se activa con cambios en apps/web o packages
│   └── migraciones.yml                 # Manual: aplica las migraciones en producción
└── pull_request_template.md            # Pide los IDs (RF, CU) que cubre el cambio
```

**Los tipos generados se suben al repositorio.** Así la web compila sin tener la API corriendo. La CI de la API regenera `openapi.json` y falla si quedó distinto al del repo: obliga a actualizar los tipos en el mismo cambio.

---

## 7. Dónde va cada cosa

| Si vas a… | Va en | Y además actualizas |
|---|---|---|
| Agregar una tabla | Primero decide su dominio dueño. Migración `AAAAMMDDHHMMSS_<dominio>_<descripcion>.sql` | `docs/04` (con su dominio) |
| Cambiar una tabla, columna o política | Una migración nueva en `supabase/migrations/` | `docs/04` |
| Agregar una regla de negocio | `rules.py` del dominio dueño si es pura; si necesita la base, `service.py` | El RN en `docs/01` y su prueba |
| Hacer que otro dominio reaccione a algo | Un evento en `events.py` del que publica y un manejador en `handlers.py` del que reacciona | La tabla de eventos en `docs/11` |
| Usar algo de otro dominio | Su API pública (`__init__.py`), solo si está debajo en el mapa | Si no está debajo, es un evento |
| Agregar un endpoint | `routes/` y `schemas.py` del dominio | Regenerar `packages/api-types` |
| Agregar una pantalla | La ruta en `apps/web/app/…` y sus piezas en `apps/web/domains/<dominio>/` | El CU en `docs/02` si cambia el flujo |
| Cambiar el texto de una plantilla de WhatsApp | Primero en Meta (aprobación), luego `domains/mensajeria/whatsapp/plantillas.py` | `docs/05` |
| Cambiar cuándo sale un recordatorio | `domains/notificaciones/programador.py` | RN-07 en `docs/01` y sus casos de prueba |
| Agregar algo que usan varios dominios y no es de ninguno | `shared/` (o `components/ui/` en la web) | — |
| Tomar una decisión de arquitectura | Un ADR nuevo en `docs/adr/` | El índice de ADR en `docs/03` |
| Agregar una variable de entorno | `core/config.py` o el código de la web | El `.env.example` de la app y las variables de Railway |
| Guardar un secreto | `.env` local y variables de Railway | **Nunca** en el repositorio |

---

## 8. Convenciones

### Nombres

- **Conceptos del dominio en español**, igual que en la base de datos y el glosario: `cita`, `barberia`, `turnos_disponibles`, `programar_notificaciones`.
- **Piezas técnicas en inglés**, como las nombran los frameworks: `router.py`, `schemas.py`, `service.py`, `repo.py`, `components/`, `hooks/`.
- **Python:** archivos y funciones en `snake_case`, clases en `PascalCase`.
- **TypeScript:** archivos en `kebab-case`, componentes de React en `PascalCase`.
- **Rutas web:** en español y en minúscula (`/panel/agenda`, `/b/barberia-norte`).

### Git

- **Ramas:** `tipo/id-descripcion`, por ejemplo `feat/cu-01-reserva-publica` o `fix/rn-07-horario-silencioso`.
- **Commits:** Conventional Commits con el dominio como alcance: `feat(agenda): calcular el primero disponible`.
- **Pull requests:** la plantilla pide los IDs que cubre (`RF-04, RN-03, CU-01`). Así la trazabilidad llega hasta el código sin mantener una matriz aparte.

### Archivos de entorno

`apps/api/.env.example`

```bash
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
SUPABASE_URL=http://127.0.0.1:54321
WEB_ORIGIN=http://localhost:3000

NOTIFICACIONES_PROVEEDOR=consola     # consola | whatsapp
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_APP_SECRET=
WHATSAPP_VERIFY_TOKEN=

SENTRY_DSN=
```

`apps/web/.env.example`

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_KEY=            # llave pública del proyecto (nunca la de servicio)
```

---

## 9. Archivos de la raíz

`pnpm-workspace.yaml`

```yaml
packages:
  - apps/web
  - packages/*
```

`Makefile`

```makefile
.PHONY: dev-db dev-api dev-worker dev-web db-reset gen-types test lint

dev-db:        ## Levanta PostgreSQL, Auth y Realtime locales
	supabase start

dev-api:       ## API con recarga automática en :8000
	cd apps/api && uv run fastapi dev app/main.py

dev-worker:    ## Worker de notificaciones
	cd apps/api && uv run python -m app.worker

dev-web:       ## Web en :3000
	pnpm --filter web dev

db-reset:      ## Recrea la base local con migraciones y seed
	supabase db reset

gen-types:     ## Regenera los tipos de la web desde la API
	cd apps/api && uv run python -m app.export_openapi ../../packages/api-types/openapi.json
	pnpm --filter @turnero/api-types exec openapi-typescript openapi.json -o src/schema.d.ts

test:          ## Todas las pruebas
	supabase test db
	cd apps/api && uv run pytest
	pnpm --filter web test

lint:
	cd apps/api && uv run ruff check . && uv run mypy app && uv run lint-imports
	pnpm --filter web lint
```

`.gitignore` (lo esencial)

```text
.env
.env.local
node_modules/
.next/
.venv/
__pycache__/
.pytest_cache/
coverage/
supabase/.temp/
```

### `CLAUDE.md` (esqueleto)

```markdown
# Turnero

SaaS de reservas para barberías con recordatorios por WhatsApp.

## Stack
- apps/web: Next.js + TypeScript (reserva pública y panel PWA)
- apps/api: FastAPI + asyncpg, sin ORM. El worker es app/worker.py
- Base de datos: Supabase (PostgreSQL con RLS). Esquema en supabase/migrations

## Dominios (docs/11-dominios.md)
mensajeria → notificaciones → agenda → clientes → barberias
- Un dominio solo importa la API pública (__init__.py) de los que tiene debajo.
- Nunca escribe tablas de otro dominio. Para afectar a uno de arriba, publica un evento.
- core/ y shared/ no importan dominios. `make lint` lo verifica con import-linter.

## Reglas
- Lee docs/01-requerimientos.md antes de tocar reglas de negocio. Cita los IDs (RF, RN, CU).
- La base solo cambia con una migración nueva; actualiza docs/04.
- Capas en cada dominio: routes → service → repo. Lógica pura en rules.py. SQL solo en repo.py y queries.py.
- Fechas en UTC; se muestran en la zona de la barbería.
- No edites packages/api-types a mano: usa `make gen-types`.
- Nunca escribas secretos en el código.

## Comandos
make dev-db · make dev-api · make dev-worker · make dev-web · make test
```

---

## 10. Cómo crearlo desde cero

```bash
mkdir turnero && cd turnero && git init

# Espacio de trabajo de JavaScript
pnpm init
printf "packages:\n  - apps/web\n  - packages/*\n" > pnpm-workspace.yaml

# Web
pnpm create next-app@latest apps/web --typescript --app --eslint --use-pnpm

# API (Python con uv)
uv init --app apps/api
cd apps/api
uv add "fastapi[standard]" asyncpg pydantic-settings pyjwt httpx
uv add --dev pytest pytest-asyncio ruff mypy import-linter
cd ../..

# Tipos compartidos
mkdir -p packages/api-types/src
cd packages/api-types && pnpm init && pnpm add -D openapi-typescript && cd ../..

# Base de datos
supabase init
# Copia el SQL del doc 04 en supabase/migrations/20261107000000_esquema_inicial.sql
supabase start
supabase db reset

# Documentación
mkdir -p docs/adr   # y copia aquí los documentos 00 a 10 y los ADR
```

Antes del primer commit, cambia el nombre del paquete de tipos a `@turnero/api-types` en su `package.json` y agrega la dependencia en la web con `pnpm --filter web add @turnero/api-types@workspace:*`.

---

## 11. Despliegue en Railway

| Servicio de Railway | Carpeta raíz | Comando de inicio |
|---|---|---|
| `web` | `apps/web` | `pnpm start` |
| `api` | `apps/api` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| `worker` | `apps/api` | `python -m app.worker` |

La API y el worker usan el mismo `Dockerfile`; solo cambia el comando de inicio. Configura en cada servicio las rutas que deben disparar un despliegue (`apps/web/**` para la web, `apps/api/**` para la API y el worker), así un cambio en la web no redespliega el backend.
