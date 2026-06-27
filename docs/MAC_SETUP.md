# Mac Setup

Guia para levantar Agente Activa desde cero en una MacBook.

## Requisitos

- Git.
- Docker Desktop para macOS.
- Node.js y npm.
- VS Code opcional.
- Acceso al repositorio en GitHub.

Verificaciones utiles:

```bash
git --version
docker --version
docker compose version
node -v
npm -v
```

## Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd "AGENTE VENTAS ACTIVA"
```

Si el nombre local del directorio cambia, ejecuta los comandos desde la raiz
del repositorio clonado.

## Variables de entorno

No versionar archivos `.env` reales.

Si existen archivos de ejemplo, copiarlos antes de iniciar:

```bash
cp apps/api/.env.example apps/api/.env
cp apps/admin/.env.example apps/admin/.env.local
```

El panel usa `API_BASE_URL` solo del lado servidor. En desarrollo local en Mac:

```text
API_BASE_URL=http://localhost:8000
```

No usar `NEXT_PUBLIC_API_BASE_URL`.

## Levantar backend y base de datos

Desde la raiz:

```bash
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.seeds.order_statuses
```

## Verificar backend

Healthcheck:

```bash
curl http://localhost:8000/api/v1/health
```

Respuesta esperada:

```json
{"status":"ok","database":"ok"}
```

Dashboard:

```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

OpenAPI:

```text
http://localhost:8000/docs
```

## Instalar frontend

```bash
cd apps/admin
npm install
```

## Ejecutar frontend

```bash
npm run dev
```

URL local:

```text
http://localhost:3000
```

Detener Next.js con `Ctrl + C`.

## Validacion backend

Desde la raiz:

```bash
docker compose exec api python -m pytest
docker compose exec api python -m ruff check app tests
curl http://localhost:8000/api/v1/health
```

Resultado esperado actual:

```text
106 passed, 1 warning
All checks passed!
```

## Validacion frontend

Desde `apps/admin`:

```bash
npm run lint
npm run typecheck
npm run build
```

## Apagar servicios

Frontend:

```text
Ctrl + C
```

Backend y PostgreSQL:

```bash
docker compose down
```

No usar este comando salvo que quieras borrar la base local:

```bash
docker compose down -v
```

`down -v` elimina volumenes de PostgreSQL y por tanto borra datos locales.
