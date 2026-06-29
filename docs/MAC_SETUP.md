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

El panel usa `API_BASE_URL` solo del lado servidor y credenciales
administrativas locales:

```text
API_BASE_URL=http://localhost:8000
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=replace-with-scrypt-password-hash
AUTH_SECRET=replace-with-random-32-byte-secret
```

No usar `NEXT_PUBLIC_API_BASE_URL` ni variables `NEXT_PUBLIC_*` para
credenciales. `API_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y
`AUTH_SECRET` son obligatorias; los placeholders no permiten ejecutar el panel.

Generar `AUTH_SECRET`:

```bash
openssl rand -base64 32
```

Generar `ADMIN_PASSWORD_HASH`:

```bash
read -s ADMIN_PASSWORD
export ADMIN_PASSWORD
node -e 'const crypto=require("node:crypto"); const password=process.env.ADMIN_PASSWORD; const salt=crypto.randomBytes(16); crypto.scrypt(password,salt,64,{N:16384,r:8,p:1},(error,key)=>{ if(error) throw error; console.log(`scrypt$16384$8$1$${salt.toString("base64url")}$${key.toString("base64url")}`); });'
unset ADMIN_PASSWORD
```

El formato del hash es:

```text
scrypt$16384$8$1$<salt-base64url>$<hash-base64url>
```

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

El script usa `next dev --webpack` para mantener estable el desarrollo local en
Mac.

URL local:

```text
http://localhost:3000
```

Abrir `/login` e ingresar con `ADMIN_USERNAME` y la contrasena usada para
generar `ADMIN_PASSWORD_HASH`.

Mas detalles de seguridad y produccion estan en `docs/SECURITY.md`.

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
125 passed, 1 warning
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
