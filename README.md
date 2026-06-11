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

Validacion actual:

- `docker compose exec api python -m pytest`: 97 pruebas aprobadas.
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
|   |-- API_USAGE.md
|   |-- DATA_MODEL.md
|   |-- PRD.md
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

## Ejecutar el panel administrativo

Con el backend disponible, iniciar Next.js localmente en Windows:

```powershell
cd apps/admin
npm install
npm run dev
```

El panel queda disponible en `http://localhost:3000`. Usa
`API_BASE_URL=http://localhost:8000` exclusivamente del lado servidor y no
requiere cambios de CORS.

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
- [Guía de uso de API](docs/API_USAGE.md)
- [Guía de pruebas](docs/TESTING.md)
- OpenAPI interactivo disponible en `http://localhost:8000/docs`.

## Roadmap pendiente

- Implementacion funcional de modulos del panel administrativo.
- Integracion futura con agente de WhatsApp.
- Autenticacion y autorizacion.
- Reportes operativos.
- Gestion avanzada de rutas y repartidores.

## Seguridad

- No subir archivos `.env`.
- No subir API keys, tokens ni credenciales.
- No agregar datos reales de clientes al repositorio.
- Usar exclusivamente datos ficticios en documentacion y pruebas.
- Configurar credenciales seguras por ambiente antes de desplegar.

## Funcionalidades aun no implementadas

El agente de WhatsApp, los flujos completos del panel administrativo, la
autenticacion, los reportes y la gestion avanzada de rutas o repartidores
todavia no forman parte del MVP actual.
