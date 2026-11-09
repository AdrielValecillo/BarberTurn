.PHONY: install dev-db dev-api dev-worker dev-web db-reset gen-types test lint

SUPABASE = pnpm exec supabase

install:       ## Instala dependencias de JavaScript y Python
	pnpm install
	cd apps/api && uv sync

dev-db:        ## Levanta PostgreSQL, Auth y Realtime locales (requiere Docker)
	$(SUPABASE) start

dev-api:       ## API con recarga automática en :8000
	cd apps/api && uv run fastapi dev app/main.py

dev-worker:    ## Worker de notificaciones
	cd apps/api && uv run python -m app.worker

dev-web:       ## Web en :3000
	pnpm --filter web dev

db-reset:      ## Recrea la base local con migraciones y seed
	$(SUPABASE) db reset

gen-types:     ## Regenera los tipos de la web desde la API
	cd apps/api && uv run python -m app.export_openapi ../../packages/api-types/openapi.json
	pnpm --filter @turnero/api-types run generate

test:          ## Todas las pruebas
	$(SUPABASE) test db
	cd apps/api && uv run pytest
	pnpm --filter web test

lint:
	cd apps/api && uv run ruff check . && uv run mypy app && uv run lint-imports
	pnpm --filter web lint
