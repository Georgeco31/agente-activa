# Guia de pruebas

Esta guia explica como levantar y validar el backend MVP de Agente Activa desde
la raiz del repositorio.

## Requisitos previos

- Docker Desktop abierto y funcionando.
- Repositorio clonado localmente.
- Una terminal PowerShell ubicada en la raiz del repositorio.
- `apps/api/.env` basado en `apps/api/.env.example` cuando se ejecute la API
  fuera de Docker Compose.

No se deben subir archivos `.env`, credenciales ni datos reales al repositorio.

## Levantar servicios

```powershell
docker compose up -d --build
```

El comando construye la imagen de la API y levanta:

- `api`: FastAPI en `http://localhost:8000`.
- `db`: PostgreSQL.

## Verificar servicios

Consultar el estado de los contenedores:

```powershell
docker compose ps
```

Verificar la API y su conexión a PostgreSQL:

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

Aplicar las migraciones:

```powershell
docker compose exec api alembic upgrade head
```

Ejecutar el seed idempotente de estados:

```powershell
docker compose exec api python -m app.seeds.order_statuses
```

El seed puede ejecutarse varias veces sin duplicar registros.

## Verificar tablas y estados

Listar tablas de PostgreSQL:

```powershell
docker compose exec db psql -U agua_user -d agua_sales -c "\dt"
```

Consultar estados de pedido:

```powershell
docker compose exec db psql -U agua_user -d agua_sales -c "SELECT * FROM order_statuses;"
```

Estados esperados:

- `pendiente`
- `asignado`
- `en_camino`
- `entregado`
- `no_entregado`
- `cancelado`

## Ejecutar todas las pruebas

```powershell
docker compose exec api python -m pytest
```

Resultado esperado actual:

```text
125 passed, 1 warning
```

El warning actual de Starlette TestClient relacionado con `httpx` es una
advertencia de deprecación externa y no bloquea las pruebas.

## Ejecutar pruebas por módulo

### Agente conversacional interno

```powershell
docker compose exec api python -m pytest tests/test_agent_service.py tests/test_agent_endpoint.py
```

### Normalización de teléfonos y texto

```powershell
docker compose exec api python -m pytest tests/test_normalization.py
```

### Búsqueda avanzada de clientes

```powershell
docker compose exec api python -m pytest tests/test_customer_search.py
```

### Detección de duplicados

```powershell
docker compose exec api python -m pytest tests/test_duplicate_detection.py
```

### Registro seguro de clientes

```powershell
docker compose exec api python -m pytest tests/test_customer_registration.py
```

### Endpoints de clientes

```powershell
docker compose exec api python -m pytest tests/test_customer_endpoints.py
```

### Endpoints de productos

```powershell
docker compose exec api python -m pytest tests/test_product_endpoints.py
```

### Endpoints de pedidos

```powershell
docker compose exec api python -m pytest tests/test_order_endpoints.py
```

### Manejo uniforme de errores

```powershell
docker compose exec api python -m pytest tests/test_api_error_handling.py
```

## Ejecutar Ruff

```powershell
docker compose exec api python -m ruff check app tests
```

Resultado esperado:

```text
All checks passed!
```

## Validacion frontend

Desde `apps/admin`:

```bash
npm run lint
npm run typecheck
npm run build
npm run dev
```

`npm run dev` ejecuta `next dev --webpack` para validar localmente el panel en
Mac con respuestas HTTP estables.

Para el panel protegido, validar manualmente:

- `/customers`, `/products`, `/orders` y `/health` sin sesion redirigen a
  `/login`.
- `/login` con credenciales incorrectas muestra un error generico.
- `/login` con credenciales correctas redirige a `/`.
- `/login?next=/orders` redirige a `/orders` despues de login correcto.
- Un usuario autenticado que entra a `/login` redirige a `/`.
- Logout elimina la cookie y redirige a `/login`.
- Despues de logout, `/` vuelve a redirigir a `/login`.
- Las Server Actions de clientes, productos y pedidos no ejecutan mutaciones
  sin sesion valida.

## Pruebas de regresión

Una prueba de regresión consiste en volver a ejecutar las pruebas de
funcionalidades existentes después de introducir un cambio. Su objetivo es
confirmar que lo nuevo funciona sin romper clientes, productos, pedidos,
normalización, búsquedas, duplicados u otros comportamientos previamente
validados.

Antes de aprobar un bloque se recomienda ejecutar:

```powershell
docker compose exec api python -m pytest
docker compose exec api python -m ruff check app tests
Invoke-RestMethod http://localhost:8000/api/v1/health
```

## Apagar servicios

```powershell
docker compose down
```

No usar `docker compose down -v` salvo que se quiera eliminar deliberadamente
los volúmenes y datos locales de PostgreSQL.

## Errores comunes

### Docker Desktop no está funcionando

Síntomas comunes:

- No se puede conectar con Docker Engine.
- `docker compose` no puede crear o iniciar contenedores.

Solución: abrir Docker Desktop, esperar a que termine de iniciar y repetir el
comando.

### Pytest no encuentra un archivo

Verificar que el comando se ejecute desde la raiz del repositorio y que la ruta
del archivo sea relativa a `apps/api`, porque el comando corre dentro del
contenedor:

```powershell
docker compose exec api ls tests
```

### Archivo `.env`

`apps/api/.env` puede usarse para ejecución local, pero nunca debe subirse al
repositorio. Utilizar `apps/api/.env.example` como referencia.

### Puerto ocupado

Si los puertos `8000` o `5432` ya están en uso, detener el proceso o contenedor
que los ocupa antes de levantar Docker Compose.

```powershell
docker compose ps
docker ps
```

### Base de datos sin migraciones

Si faltan tablas o aparecen errores de relación inexistente:

```powershell
docker compose exec api alembic upgrade head
```

### Seed no ejecutado

Los pedidos requieren los estados base. Si falta `pendiente` u otro estado:

```powershell
docker compose exec api python -m app.seeds.order_statuses
```

### Warning de Starlette TestClient

La suite puede mostrar una advertencia de deprecación sobre Starlette TestClient
y `httpx`. Actualmente es no bloqueante: las pruebas deben seguir terminando con
estado exitoso.
