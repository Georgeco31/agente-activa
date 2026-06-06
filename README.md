# Agente Activa

Agente Activa es un MVP para una empresa de venta y reparto de agua que atiende pedidos por WhatsApp.

El proyecto se esta construyendo por bloques. Primero se desarrolla el backend del nucleo del negocio: clientes, telefonos, alias, direcciones, productos, pedidos, estados, rutas de reparto e historial. Mas adelante, el agente de WhatsApp usara este nucleo mediante servicios internos, sin duplicar reglas de negocio.

## Estado actual

Bloque 1 completado: base tecnica inicial.

Bloque 2 en implementacion: modelos ORM, Alembic, migracion inicial y seed de estados.

Incluye:

- Estructura inicial de `apps/api`.
- FastAPI configurado.
- SQLAlchemy 2.0 configurado.
- Conexion base a PostgreSQL.
- Dockerfile para la API.
- `docker-compose.yml` en la raiz.
- Servicio PostgreSQL en Docker Compose.
- Endpoint `GET /api/v1/health`.
- Documentacion base en `docs/`.

No incluye todavia:

- Servicios de clientes, productos o pedidos.
- Agente de WhatsApp.
- Panel administrativo.

## Stack tecnico

- Backend: FastAPI.
- ORM: SQLAlchemy 2.0.
- Base de datos: PostgreSQL.
- Migraciones: Alembic, desde el Bloque 2.
- Validacion: Pydantic.
- Pruebas: Pytest.
- Contenedores: Docker Compose.
- Frontend admin futuro: Next.js con App Router.

## Estructura actual

```text
.
  apps/
    api/
      app/
        api/
        core/
        db/
        main.py
      Dockerfile
      pyproject.toml
      README.md
  docs/
    PRD.md
    DATA_MODEL.md
  docker-compose.yml
  README.md
```

## Ejecutar con Docker Compose

Desde la raiz del repositorio:

```powershell
cd "C:\Users\Administrator\Documents\AGENTE VENTAS ACTIVA"
docker compose up --build
```

Esto levanta:

- `db`: PostgreSQL.
- `api`: FastAPI en `http://localhost:8000`.

## Probar el endpoint de salud

En otra terminal:

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

El endpoint ejecuta una consulta simple contra PostgreSQL, por lo que valida que la API puede conectarse a la base de datos.

## Verificar PostgreSQL

```powershell
docker compose ps
docker compose exec db pg_isready -U agua_user -d agua_sales
```

## Ejecutar migraciones

Levantar servicios:

```powershell
docker compose up -d --build
```

Aplicar la migracion inicial:

```powershell
docker compose exec api alembic upgrade head
```

Verificar tablas:

```powershell
docker compose exec db psql -U agua_user -d agua_sales -c "\dt"
```

Verificar version de Alembic:

```powershell
docker compose exec db psql -U agua_user -d agua_sales -c "SELECT * FROM alembic_version;"
```

## Ejecutar seed de estados

El seed de estados es idempotente. Puede ejecutarse mas de una vez sin duplicar registros.

```powershell
docker compose exec api python -m app.seeds.order_statuses
```

Verificar estados:

```powershell
docker compose exec db psql -U agua_user -d agua_sales -c "SELECT * FROM order_statuses;"
```

## Variables de entorno

La API incluye un archivo de referencia en:

```text
apps/api/.env.example
```

En Docker Compose, la API usa:

```text
DATABASE_URL=postgresql+psycopg://agua_user:agua_password@db:5432/agua_sales
```

## Documentacion

- `docs/PRD.md`: requisitos del producto y alcance del MVP.
- `docs/DATA_MODEL.md`: entidades, relaciones y decisiones del modelo de datos.

## Proximo paso

Completar validacion del Bloque 2: modelos ORM + Alembic + migracion inicial.

El Bloque 2 debe crear los modelos de negocio, configurar migraciones y precargar los estados base del pedido:

- `pendiente`
- `asignado`
- `en_camino`
- `entregado`
- `no_entregado`
- `cancelado`
