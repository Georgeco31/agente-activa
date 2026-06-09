# Agente Activa

Agente Activa es un backend MVP para gestionar clientes, productos y pedidos de
una empresa de venta y reparto de agua. El nucleo esta preparado para una futura
integracion con un agente de WhatsApp que reutilice las mismas reglas de negocio.

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

El backend MVP se encuentra funcional y validado. Los bloques completados son:

- Bloque 1: FastAPI, Docker Compose, PostgreSQL y healthcheck.
- Bloque 2: modelos ORM, Alembic, migracion inicial y seed de estados.
- Bloque 3A: normalizacion de telefonos ecuatorianos y texto.
- Bloque 3B: busqueda avanzada de clientes y deteccion de duplicados.
- Bloque 3C: registro seguro de clientes e historial de acciones.
- Bloque 4A: endpoints administrativos de clientes.
- Bloque 4B: endpoints administrativos de productos.
- Bloque 4C: endpoints administrativos de pedidos.
- Bloque 5A: documentacion base, validacion integral, Ruff y pruebas completas.

Validacion actual:

- `docker compose exec api python -m pytest`: 82 pruebas aprobadas.
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
- Pruebas automatizadas y validacion de calidad con Ruff.

## Estructura del proyecto

```text
.
|-- apps/
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
|   |-- DATA_MODEL.md
|   `-- PRD.md
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
- `docs/API_USAGE.md`: guia de uso de la API, pendiente de creacion.
- `docs/TESTING.md`: guia detallada de pruebas, pendiente de creacion.
- OpenAPI interactivo disponible en `http://localhost:8000/docs`.

## Roadmap pendiente

- Bloque 5B: endurecimiento de API, errores y respuestas uniformes.
- Panel administrativo con Next.js.
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

El agente de WhatsApp, el panel administrativo, la autenticacion, los reportes y
la gestion avanzada de rutas o repartidores todavia no forman parte del backend
actual.
