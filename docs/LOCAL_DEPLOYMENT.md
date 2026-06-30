# Operacion local

Esta guia describe como levantar Agente Activa en una MacBook, una maquina
Linux local o un servidor interno no expuesto publicamente.

El objetivo de este bloque es operacion local escalable. No habilita
produccion publica, WhatsApp real ni exposicion directa de FastAPI a internet.

## Requisitos

- Git.
- Docker Desktop en macOS o Docker Engine con Docker Compose en Linux.
- Node.js y npm para ejecutar el panel administrativo fuera de contenedor.
- Acceso al repositorio.
- Terminal ubicada en la raiz del repo.

Verificaciones utiles:

```bash
git --version
docker --version
docker compose version
node -v
npm -v
```

## Rutas del proyecto

En esta MacBook el repo esta en:

```text
/Users/georgemac/Desktop/agente/agente-activa
```

En Linux o en otro equipo puede vivir en cualquier carpeta. En todos los casos,
ejecutar los comandos desde la raiz del repositorio clonado.

## Puertos locales

- API FastAPI: `http://localhost:8000`.
- PostgreSQL: `localhost:5432`, solo para uso local o red interna controlada.
- Admin Next.js: `http://localhost:3000`.

No exponer estos puertos a internet sin reverse proxy, HTTPS, firewall y
controles adicionales.

## Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd agente-activa
```

Si el directorio local tiene otro nombre, usar ese directorio como raiz.

## Variables de entorno locales

No versionar archivos `.env` reales.

Backend:

```bash
cp apps/api/.env.example apps/api/.env
```

Admin:

```bash
cp apps/admin/.env.example apps/admin/.env.local
```

Reemplazar placeholders antes de ejecutar el panel. En particular:

- `ADMIN_PASSWORD_HASH`;
- `AUTH_SECRET`;
- `AGENT_SIMULATION_TOKEN` si se prueba el agente;
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN` y `WHATSAPP_APP_SECRET` solo si se prueba el
  webhook localmente.

No usar variables `NEXT_PUBLIC_*` para credenciales.

## Levantar backend y base de datos

Desde la raiz:

```bash
docker compose up -d --build
```

Ver contenedores:

```bash
docker compose ps
```

## Migraciones y seed

Aplicar migraciones:

```bash
docker compose exec api alembic upgrade head
```

Ejecutar seed idempotente de estados de pedido:

```bash
docker compose exec api python -m app.seeds.order_statuses
```

## Verificar backend

Healthcheck:

```bash
curl http://localhost:8000/api/v1/health
```

Healthcheck operativo:

```bash
./scripts/check-health.sh
```

Respuesta esperada:

```json
{"status":"ok","database":"ok"}
```

Dashboard:

```bash
curl http://localhost:8000/api/v1/dashboard/overview
```

OpenAPI local:

```text
http://localhost:8000/docs
```

## Levantar frontend admin

En otra terminal:

```bash
cd apps/admin
npm install
npm run dev
```

El script usa `next dev --webpack`. Abrir:

```text
http://localhost:3000/login
```

Validar login con `ADMIN_USERNAME` y la contrasena usada para generar
`ADMIN_PASSWORD_HASH`. Luego abrir el dashboard en `/`.

## Validacion manual minima

- `/login` carga correctamente.
- Login correcto redirige a `/`.
- Dashboard carga metricas.
- `/customers`, `/products`, `/orders` y `/health` cargan autenticado.
- Logout elimina la sesion.
- Despues de logout, `/` redirige a `/login`.

## Apagar correctamente

Detener el admin con `Ctrl + C` en la terminal de Next.js.

Apagar backend y base de datos:

```bash
./scripts/stop-local.sh
```

Comando manual equivalente:

```bash
docker compose down
```

No usar este comando salvo que se quiera borrar deliberadamente la base local:

```bash
docker compose down -v
```

`down -v` elimina el volumen de PostgreSQL y borra los datos locales.

## Seguridad local

- No subir `.env`.
- No subir `.env.local`.
- No subir backups.
- No subir datos reales.
- No dejar placeholders en entornos reales.
- No usar contrasenas debiles.
- No habilitar `WHATSAPP_WEBHOOK_ENABLED` en una URL publica sin entender los
  riesgos.
- No exponer FastAPI directamente a internet.

## Scripts locales

- Backup local: `./scripts/backup-db.sh`
- Restore local con confirmacion: `./scripts/restore-db.sh backups/archivo.dump`
- Healthcheck local: `./scripts/check-health.sh`
- Parada segura: `./scripts/stop-local.sh`

No existe `scripts/start-local.sh` todavia. Queda para futuro cuando la
operacion diaria este estabilizada.

## Documentacion relacionada

- `docs/BACKUP_RESTORE.md`
- `docs/DEPLOYMENT_CHECKLIST.md`
- `docs/INTERNAL_OPERATIONS.md`
- `docs/DAILY_OPERATIONS_CHECKLIST.md`
- `docs/INCIDENT_RUNBOOK.md`
- `docs/PRODUCTION_READINESS.md`
- `docs/SECURITY.md`
