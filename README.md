# Agente Activa

Agente Activa es un MVP para gestionar clientes, productos y pedidos de una
empresa de venta y reparto de agua. Incluye un backend operativo y la base
inicial de un panel administrativo, preparados para una futura integracion con
un agente de WhatsApp que reutilice las mismas reglas de negocio.

## Problema que resuelve

El sistema centraliza la informacion operativa que normalmente queda dispersa
entre conversaciones, asesores y registros manuales:

- Clientes con multiples telefonos, alias y direcciones.
- Productos disponibles y sus precios.
- Pedidos confirmados con uno o varios productos.
- Estados e historial de acciones.
- Busqueda avanzada y deteccion de posibles clientes duplicados.

El objetivo es evitar duplicados, impedir pedidos incompletos y mantener
trazabilidad sobre las acciones importantes del negocio.

## Estado actual

El backend MVP se encuentra funcional y validado. El panel administrativo ya
cuenta con su base tecnica y visual. Los bloques completados son:

- Bloque 1: FastAPI, Docker Compose, PostgreSQL y healthcheck.
- Bloque 2: modelos ORM, Alembic, migracion inicial y seed de estados.
- Bloque 3A: normalizacion de telefonos ecuatorianos y texto.
- Bloque 3B: busqueda avanzada de clientes y deteccion de duplicados.
- Bloque 3C: registro seguro de clientes e historial de acciones.
- Bloque 4A: endpoints administrativos de clientes.
- Bloque 4B: endpoints administrativos de productos.
- Bloque 4C: endpoints administrativos de pedidos.
- Bloque 5A: documentacion base, validacion integral, Ruff y pruebas completas.
- Bloque 5B: respuestas de error uniformes y manejo seguro de errores inesperados.
- Bloque 6A: guias de uso de API y pruebas.
- Bloque 6B: base del panel administrativo con Next.js y conexion server-side a FastAPI.
- Bloque 6C: modulo administrativo funcional de clientes.
- Bloque 6D: modulo administrativo funcional de productos.
- Bloque 6E-A: respuestas de pedidos enriquecidas para despacho sin N+1.
- Bloque 6E-B: modulo administrativo funcional de pedidos.
- Bloque 7A: dashboard operativo optimizado.
- Bloque 8A: seguridad y autenticacion basica del panel administrativo.
- Bloque 8B: endurecimiento de configuracion y headers de seguridad.
- Bloque 9A: nucleo conversacional backend y simulador interno.
- Bloque 9B: persistencia conversacional minima del agente.
- Bloque 9C: webhook WhatsApp/Meta seguro en modo preparacion.
- Bloque 9D: confirmacion conversacional y creacion segura de pedidos reales.
- Bloque 10A: preparacion local escalable, backups y checklist de despliegue.
- Bloque 10B: preparacion de operacion interna local.

Validacion actual:

- `docker compose exec api python -m pytest`: 178 pruebas aprobadas.
- `docker compose exec api python -m ruff check app tests`: todos los chequeos aprobados.
- `GET /api/v1/health`: responde `status: ok` y `database: ok`.

## Stack tecnico

- Python 3.12.
- FastAPI.
- PostgreSQL 16.
- SQLAlchemy 2.0.
- Alembic.
- Pydantic.
- Pytest.
- Ruff.
- Docker Compose.
- Node.js y npm para desarrollo local del panel.
- Next.js con App Router.
- React.
- TypeScript.
- ESLint.

## Funcionalidades implementadas

- Healthcheck con verificacion de conexion a PostgreSQL.
- Modelos ORM para clientes, telefonos, alias, direcciones, productos, pedidos,
  detalles de pedido, estados, rutas de reparto e historial.
- Migraciones de base de datos con Alembic.
- Seed idempotente de estados base del pedido.
- Normalizacion de telefonos de Ecuador a formato E.164.
- Normalizacion de nombres, alias, direcciones y referencias.
- Busqueda avanzada de clientes.
- Deteccion de posibles clientes duplicados con razones y score.
- Registro seguro de clientes.
- Asociacion de telefonos, alias y direcciones.
- Historial de acciones relevantes.
- Gestion administrativa de clientes, productos y pedidos mediante API.
- Respuestas de error uniformes para reglas de negocio, validacion y errores inesperados.
- Pruebas automatizadas y validacion de calidad con Ruff.
- Base responsive del panel administrativo.
- Cliente HTTP centralizado y server-only para FastAPI.
- Vista de health del backend desde el panel.
- Busqueda, creacion y detalle de clientes desde el panel.
- Deteccion de duplicados y asociacion de telefonos, alias y direcciones.
- Listado, busqueda, creacion, detalle, actualizacion y desactivacion de productos.
- Listado, filtros, creacion, detalle, cambio de estado y cancelacion de pedidos.
- Datos enriquecidos de cliente y direccion para despacho sin consultas N+1.
- Dashboard operativo con metricas agregadas, ventas entregadas, alertas y
  ultimos pedidos mediante una sola llamada server-side.
- Login administrativo con usuario unico configurado por variables de entorno.
- Sesion firmada en cookie HttpOnly.
- Proteccion de rutas del panel con `src/proxy.ts`.
- Logout server-side que elimina la cookie de sesion.
- Guardas de sesion en Server Actions mutantes del panel.
- Validacion estricta de variables del panel administrativo.
- Headers defensivos de seguridad en Next.js.
- Nucleo conversacional backend para simulacion interna.
- Endpoint interno que interpreta mensajes simulados, busca cliente por telefono,
  consulta productos/pedidos y responde sin crear pedidos reales.
- Persistencia conversacional interna con sesiones, mensajes inbound/outbound,
  acumulacion no destructiva de datos extraidos y cierre manual de sesiones.
- Webhook entrante compatible con Meta/WhatsApp Cloud API en modo preparacion:
  verificacion GET, validacion HMAC-SHA256 de POST y procesamiento interno sin
  envio real de mensajes.
- Confirmacion conversacional protegida para crear pedidos reales solo con
  cliente, producto, cantidad, direccion, resumen pendiente y confirmacion
  explicita.

## Estructura del proyecto

```text
.
|-- apps/
|   |-- admin/
|   |   |-- src/
|   |   |   |-- app/
|   |   |   |-- components/
|   |   |   `-- lib/
|   |   `-- package.json
|   `-- api/
|       |-- alembic/
|       |-- app/
|       |   |-- api/
|       |   |-- core/
|       |   |-- db/
|       |   |-- models/
|       |   |-- repositories/
|       |   |-- schemas/
|       |   |-- seeds/
|       |   `-- services/
|       |-- tests/
|       |-- Dockerfile
|       `-- pyproject.toml
|-- docs/
|   |-- ADMIN_PANEL.md
|   |-- AGENT.md
|   |-- API_USAGE.md
|   |-- BACKUP_RESTORE.md
|   |-- CODEX_HANDOFF.md
|   |-- DATA_MODEL.md
|   |-- DAILY_OPERATIONS_CHECKLIST.md
|   |-- DEPLOYMENT_CHECKLIST.md
|   |-- INCIDENT_RUNBOOK.md
|   |-- INITIAL_DATA_LOAD.md
|   |-- INTERNAL_OPERATIONS.md
|   |-- LOCAL_DEPLOYMENT.md
|   |-- MAC_SETUP.md
|   |-- ORDER_OPERATIONS.md
|   |-- PRD.md
|   |-- PRODUCTION_READINESS.md
|   |-- PROJECT_RULES.md
|   |-- ROADMAP.md
|   |-- SECURITY.md
|   |-- env/
|   `-- TESTING.md
|-- docker-compose.yml
`-- README.md
```

## Ejecutar el proyecto

Desde la raiz del repositorio:

```powershell
docker compose up -d --build
```

Servicios disponibles:

- API: `http://localhost:8000`
- Documentacion OpenAPI: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

Comprobar el estado de la API y su conexion a PostgreSQL:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "database": "ok"
}
```

Para usar el simulador interno del agente, configurar `AGENT_SIMULATION_TOKEN`
en el entorno del backend y enviar el header `X-Agent-Simulation-Token`. El
endpoint stateless es `POST /api/v1/agent/simulate-message`; el endpoint con
persistencia conversacional es `POST /api/v1/agent/simulate-conversation-message`.
La creacion real desde agente usa
`POST /api/v1/agent/conversations/{session_id}/confirm-order` y requiere
confirmacion explicita.
Ver `docs/AGENT.md`.

Para probar el webhook WhatsApp/Meta en modo preparacion, configurar
`WHATSAPP_WEBHOOK_ENABLED`, `WHATSAPP_WEBHOOK_VERIFY_TOKEN` y
`WHATSAPP_APP_SECRET` en el entorno local del backend. El webhook valida firma,
procesa mensajes internamente y no envia respuestas reales.

## Ejecutar el panel administrativo

Con el backend disponible, configurar las variables locales del panel:

```bash
cd apps/admin
cp .env.example .env.local
```

Completar en `.env.local`:

```text
API_BASE_URL=http://localhost:8000
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=replace-with-scrypt-password-hash
AUTH_SECRET=replace-with-random-32-byte-secret
```

Generar `AUTH_SECRET` en Mac:

```bash
openssl rand -base64 32
```

Generar `ADMIN_PASSWORD_HASH` en Mac:

```bash
read -s ADMIN_PASSWORD
export ADMIN_PASSWORD
node -e 'const crypto=require("node:crypto"); const password=process.env.ADMIN_PASSWORD; const salt=crypto.randomBytes(16); crypto.scrypt(password,salt,64,{N:16384,r:8,p:1},(error,key)=>{ if(error) throw error; console.log(`scrypt$16384$8$1$${salt.toString("base64url")}$${key.toString("base64url")}`); });'
unset ADMIN_PASSWORD
```

Iniciar Next.js:

```bash
npm install
npm run dev
```

El script `npm run dev` usa el dev server de Next.js con webpack para mantener
la validacion local estable en Mac. El panel queda disponible en
`http://localhost:3000`. Usa
`API_BASE_URL=http://localhost:8000` exclusivamente del lado servidor y no
requiere cambios de CORS. No se usan variables `NEXT_PUBLIC_*` para
credenciales. `API_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y
`AUTH_SECRET` son obligatorias en el entorno del panel.

Validar el frontend:

```powershell
npm run lint
npm run typecheck
npm run build
```

## Migraciones y seed

Aplicar todas las migraciones disponibles:

```powershell
docker compose exec api alembic upgrade head
```

Precargar o actualizar los estados base del pedido:

```powershell
docker compose exec api python -m app.seeds.order_statuses
```

El seed es idempotente y puede ejecutarse varias veces sin duplicar estados.

Estados base:

- `pendiente`
- `asignado`
- `en_camino`
- `entregado`
- `no_entregado`
- `cancelado`

## Pruebas y calidad

Ejecutar todas las pruebas:

```powershell
docker compose exec api python -m pytest
```

Ejecutar Ruff:

```powershell
docker compose exec api python -m ruff check app tests
```

## Operacion local y backups

La guia operativa principal para una maquina local o servidor interno esta en
[`docs/LOCAL_DEPLOYMENT.md`](docs/LOCAL_DEPLOYMENT.md).

Backups y restauracion de PostgreSQL estan documentados en
[`docs/BACKUP_RESTORE.md`](docs/BACKUP_RESTORE.md). Antes de migraciones o
cambios grandes, crear un backup y probar la restauracion en un entorno de
prueba.

El checklist de despliegue local esta en
[`docs/DEPLOYMENT_CHECKLIST.md`](docs/DEPLOYMENT_CHECKLIST.md). La preparacion
para VPS/nube futura esta en
[`docs/PRODUCTION_READINESS.md`](docs/PRODUCTION_READINESS.md).

Los ejemplos adicionales de entorno viven en `docs/env/` y contienen solo
placeholders. No crear ni versionar `.env` reales.

## Operacion interna

Las guias para uso diario interno estan en:

- [`docs/INTERNAL_OPERATIONS.md`](docs/INTERNAL_OPERATIONS.md)
- [`docs/INITIAL_DATA_LOAD.md`](docs/INITIAL_DATA_LOAD.md)
- [`docs/ORDER_OPERATIONS.md`](docs/ORDER_OPERATIONS.md)
- [`docs/DAILY_OPERATIONS_CHECKLIST.md`](docs/DAILY_OPERATIONS_CHECKLIST.md)
- [`docs/INCIDENT_RUNBOOK.md`](docs/INCIDENT_RUNBOOK.md)

Estas guias no implementan roles tecnicos ni permisos en codigo. Definen
responsabilidades manuales para operar el MVP localmente.

## Respuestas de error

Los errores de la API usan una estructura uniforme:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource not found.",
    "details": {}
  }
}
```

Las validaciones de entrada responden con estado `422` y codigo
`VALIDATION_ERROR`. Los errores inesperados responden con estado `500` y codigo
`INTERNAL_SERVER_ERROR` sin exponer trazas ni detalles internos.

## Endpoints disponibles

### Health

- `GET /api/v1/health`

### Dashboard

- `GET /api/v1/dashboard/overview`

### Agente interno

- `POST /api/v1/agent/simulate-message`
- `POST /api/v1/agent/simulate-conversation-message`
- `GET /api/v1/agent/conversations/{session_id}`
- `POST /api/v1/agent/conversations/{session_id}/close`
- `POST /api/v1/agent/conversations/{session_id}/confirm-order`

### WhatsApp webhook en preparacion

- `GET /api/v1/whatsapp/webhook`
- `POST /api/v1/whatsapp/webhook`

### Clientes

- `POST /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `GET /api/v1/customers/search`
- `POST /api/v1/customers/detect-duplicates`
- `POST /api/v1/customers/{customer_id}/phones`
- `POST /api/v1/customers/{customer_id}/aliases`
- `POST /api/v1/customers/{customer_id}/addresses`

### Productos

- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `GET /api/v1/products/search`
- `PATCH /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}/deactivate`

### Pedidos

- `POST /api/v1/orders`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{order_id}`
- `PATCH /api/v1/orders/{order_id}/status`
- `PATCH /api/v1/orders/{order_id}/cancel`

## Documentacion adicional

- [Requisitos del producto](docs/PRD.md)
- [Modelo de datos](docs/DATA_MODEL.md)
- [Panel administrativo](docs/ADMIN_PANEL.md)
- [Agente conversacional](docs/AGENT.md)
- [Guía de uso de API](docs/API_USAGE.md)
- [Guía de pruebas](docs/TESTING.md)
- [Operación local](docs/LOCAL_DEPLOYMENT.md)
- [Backups y restauración](docs/BACKUP_RESTORE.md)
- [Checklist de despliegue](docs/DEPLOYMENT_CHECKLIST.md)
- [Operación interna](docs/INTERNAL_OPERATIONS.md)
- [Carga inicial de datos](docs/INITIAL_DATA_LOAD.md)
- [Operación de pedidos](docs/ORDER_OPERATIONS.md)
- [Checklist diario](docs/DAILY_OPERATIONS_CHECKLIST.md)
- [Runbook de incidentes](docs/INCIDENT_RUNBOOK.md)
- [Preparación para producción](docs/PRODUCTION_READINESS.md)
- [Handoff para Codex](docs/CODEX_HANDOFF.md)
- [Setup en Mac](docs/MAC_SETUP.md)
- [Roadmap](docs/ROADMAP.md)
- [Reglas del proyecto](docs/PROJECT_RULES.md)
- [Seguridad](docs/SECURITY.md)
- OpenAPI interactivo disponible en `http://localhost:8000/docs`.

## Roadmap pendiente

- Envio futuro de respuestas reales por WhatsApp.
- Confirmacion especial para pedidos duplicados recientes.
- Autorizacion y roles futuros.
- Reportes operativos.
- Gestion avanzada de rutas y repartidores.
- Docker Compose de produccion, reverse proxy y HTTPS cuando se defina el
  despliegue publico.
- Scripts seguros de backup/restore.
- Preparacion de servidor local.
- WhatsApp saliente controlado.
- Piloto con clientes reales.

## Seguridad

- No subir archivos `.env`.
- No subir API keys, tokens ni credenciales.
- No agregar datos reales de clientes al repositorio.
- Usar exclusivamente datos ficticios en documentacion y pruebas.
- Configurar credenciales seguras por ambiente antes de desplegar.
- Consultar [docs/SECURITY.md](docs/SECURITY.md) para generar `AUTH_SECRET`,
  `ADMIN_PASSWORD_HASH` y revisar recomendaciones de produccion.

## Funcionalidades aun no implementadas

Envio real de mensajes por WhatsApp, exposicion publica sin controles
adicionales, creacion automatica de pedidos desde el agente, roles reales,
recuperacion de contrasena, OAuth, reportes, docker-compose de produccion,
scripts operativos y la gestion avanzada de rutas o repartidores todavia no
forman parte del MVP actual.
