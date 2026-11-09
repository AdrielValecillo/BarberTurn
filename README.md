# Turnero

Reservas y recordatorios por WhatsApp para barberías (nombre provisional). Monorepo con la web (Next.js), la API y el worker (FastAPI) y la base de datos (Supabase). El diseño completo está en [`docs/`](docs/); empieza por [`docs/00-vision-y-alcance.md`](docs/00-vision-y-alcance.md) y [`docs/10-estructura-del-monorepo.md`](docs/10-estructura-del-monorepo.md).

## Requisitos

- [Node.js](https://nodejs.org) 22+ y [pnpm](https://pnpm.io) (la versión exacta está en `package.json`)
- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 solo)
- [Docker](https://www.docker.com/products/docker-desktop/) en ejecución (lo usa la base de datos local)
- `make` — en Windows: `winget install ezwinports.make` (o corre los comandos del [`Makefile`](Makefile) a mano)

La CLI de Supabase no se instala aparte: viene como dependencia del repo (`pnpm exec supabase`).

## Levantarlo en 5 minutos

```bash
make install        # pnpm install + uv sync
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local

make dev-db         # PostgreSQL, Auth y Realtime locales (la primera vez descarga imágenes)
make db-reset       # aplica las migraciones y el seed (barbería de ejemplo)

make dev-api        # API en http://localhost:8000  (docs en /docs, salud en /health)
make dev-web        # Web en http://localhost:3000
make dev-worker     # Worker de notificaciones (opcional por ahora)
```

Al correr `make dev-db`, la CLI imprime las URLs y llaves locales (copia la llave pública en `NEXT_PUBLIC_SUPABASE_KEY`). Los correos de acceso del panel no se envían: se leen en el servidor de correo de prueba (http://127.0.0.1:54324).

## Comandos

| Comando | Qué hace |
|---|---|
| `make test` | Pruebas de la base (pgTAP), de la API (pytest) y de la web (Vitest) |
| `make lint` | ruff, mypy, import-linter (límites entre dominios) y ESLint |
| `make gen-types` | Regenera `packages/api-types` desde el OpenAPI de la API. Súbelos con el cambio |
| `make db-reset` | Recrea la base local con migraciones y seed |

## Estructura

```text
apps/web/            Next.js: reserva pública y panel (PWA)
apps/api/            FastAPI: API, webhook de WhatsApp y worker (app/domains/ por dominio)
packages/api-types/  Tipos de TypeScript generados desde el OpenAPI (no se editan a mano)
supabase/            Config, migraciones, seed y pruebas de base de datos
docs/                Documentación y decisiones (ADR)
```

Las reglas de dependencia, las convenciones de nombres y la tabla "dónde va cada cosa" están en el [doc 10](docs/10-estructura-del-monorepo.md) y el [doc 11](docs/11-dominios.md).
