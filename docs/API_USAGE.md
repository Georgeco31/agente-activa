# Guia de uso de la API

Esta guia describe como consumir el backend MVP de Agente Activa en un entorno
local. Todos los nombres, telefonos, direcciones, UUIDs y demas datos utilizados
en los ejemplos son ficticios.

## Acceso local

- URL base: `http://localhost:8000`
- Prefijo de API: `/api/v1`
- OpenAPI interactivo: `http://localhost:8000/docs`

Los ejemplos usan PowerShell e `Invoke-RestMethod`. Para solicitudes con cuerpo,
el objeto se convierte a JSON antes de enviarlo.

## Health

### Consultar estado de la API

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

Respuesta exitosa:

```json
{
  "status": "ok",
  "database": "ok"
}
```

Este endpoint también comprueba que la API puede consultar PostgreSQL.

## Clientes

Los teléfonos móviles ecuatorianos se normalizan al formato E.164. Por ejemplo,
`0999627968` se guarda como `+593999627968`.

Los nombres, alias, direcciones y referencias se normalizan para facilitar
búsquedas y detectar posibles duplicados. Antes de registrar un cliente nuevo,
el sistema compara sus datos con clientes existentes.

### Crear un cliente

`POST /api/v1/customers`

```powershell
$body = @{
  display_name = "Cliente Ejemplo Norte"
  phone = "0999627968"
  alias = "Tienda Azul"
  address = "Av. Ejemplo 123 y Calle Ficticia"
  reference = "Porton azul frente al parque"
  customer_type = "persona"
  notes = "Datos exclusivamente ficticios"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/customers `
  -ContentType "application/json" `
  -Body $body
```

Si existen coincidencias fuertes, la API no crea el cliente y devuelve un error
`CUSTOMER_DUPLICATE_CANDIDATE_FOUND` con candidatos dentro de `details`.

### Obtener un cliente por ID

`GET /api/v1/customers/{customer_id}`

```powershell
$customerId = "11111111-1111-4111-8111-111111111111"
Invoke-RestMethod "http://localhost:8000/api/v1/customers/$customerId"
```

La respuesta incluye los teléfonos, alias y direcciones asociados.

### Buscar clientes

`GET /api/v1/customers/search`

La búsqueda acepta uno o varios parámetros:

- `phone`
- `name`
- `alias`
- `address`
- `reference`

```powershell
Invoke-RestMethod `
  "http://localhost:8000/api/v1/customers/search?phone=0999627968"

Invoke-RestMethod `
  "http://localhost:8000/api/v1/customers/search?alias=Tienda%20Azul"
```

Debe enviarse al menos un criterio.

### Detectar posibles duplicados

`POST /api/v1/customers/detect-duplicates`

```powershell
$body = @{
  phone = "+593999627968"
  name = "Cliente Ejemplo Norte"
  alias = "Tienda Azul"
  address = "Av. Ejemplo 123 y Calle Ficticia"
  reference = "Porton azul frente al parque"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/customers/detect-duplicates `
  -ContentType "application/json" `
  -Body $body
```

Cada coincidencia contiene `customer_id`, nombre visible, razones, score y nivel
de confianza.

### Agregar un teléfono

`POST /api/v1/customers/{customer_id}/phones`

```powershell
$customerId = "11111111-1111-4111-8111-111111111111"
$body = @{
  phone = "0987654321"
  label = "alternativo"
  is_primary = $false
  is_whatsapp = $true
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/customers/$customerId/phones" `
  -ContentType "application/json" `
  -Body $body
```

Un teléfono normalizado no puede pertenecer a más de un cliente.

### Agregar un alias

`POST /api/v1/customers/{customer_id}/aliases`

```powershell
$customerId = "11111111-1111-4111-8111-111111111111"
$body = @{
  alias = "Local Ejemplo"
  source = "manual"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/customers/$customerId/aliases" `
  -ContentType "application/json" `
  -Body $body
```

### Agregar una dirección

`POST /api/v1/customers/{customer_id}/addresses`

```powershell
$customerId = "11111111-1111-4111-8111-111111111111"
$body = @{
  address = "Calle Ficticia 456"
  reference = "Casa blanca junto al parque"
  label = "bodega"
  city = "Ciudad Ejemplo"
  neighborhood = "Barrio Norte"
  is_primary = $false
  notes = "Direccion ficticia"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/customers/$customerId/addresses" `
  -ContentType "application/json" `
  -Body $body
```

## Productos

Cada producto requiere un SKU único. El precio no puede ser negativo. Los
productos desactivados permanecen disponibles para conservar históricos, pero no
pueden utilizarse para crear pedidos nuevos.

### Crear un producto

`POST /api/v1/products`

```powershell
$body = @{
  sku = "AGUA-EJEMPLO-20L"
  name = "Botellon Ejemplo 20 Litros"
  description = "Producto ficticio para documentacion"
  unit = "botellon"
  price = "9.50"
  is_active = $true
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/products `
  -ContentType "application/json" `
  -Body $body
```

### Listar productos

`GET /api/v1/products`

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/products
```

Listar únicamente productos activos:

```powershell
Invoke-RestMethod "http://localhost:8000/api/v1/products?active_only=true"
```

### Obtener un producto por ID

`GET /api/v1/products/{product_id}`

```powershell
$productId = "22222222-2222-4222-8222-222222222222"
Invoke-RestMethod "http://localhost:8000/api/v1/products/$productId"
```

### Buscar productos

`GET /api/v1/products/search`

La búsqueda acepta `name` o `sku`.

```powershell
Invoke-RestMethod `
  "http://localhost:8000/api/v1/products/search?sku=AGUA-EJEMPLO-20L"

Invoke-RestMethod `
  "http://localhost:8000/api/v1/products/search?name=Botellon%20Ejemplo%2020%20Litros"
```

### Actualizar un producto

`PATCH /api/v1/products/{product_id}`

```powershell
$productId = "22222222-2222-4222-8222-222222222222"
$body = @{
  name = "Botellon Ejemplo Actualizado"
  price = "10.25"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Patch `
  -Uri "http://localhost:8000/api/v1/products/$productId" `
  -ContentType "application/json" `
  -Body $body
```

### Desactivar un producto

`PATCH /api/v1/products/{product_id}/deactivate`

```powershell
$productId = "22222222-2222-4222-8222-222222222222"
Invoke-RestMethod `
  -Method Patch `
  -Uri "http://localhost:8000/api/v1/products/$productId/deactivate"
```

## Pedidos

Un pedido confirmado requiere:

- Un cliente existente.
- Una dirección existente que pertenezca al cliente.
- Al menos un item.
- Un producto activo por item.
- Una cantidad mayor que cero por item.

El estado inicial siempre es `pendiente`. Si un item no incluye `unit_price`, el
sistema utiliza el precio actual del producto. Los pedidos no pueden utilizar
productos inactivos.

### Crear un pedido

`POST /api/v1/orders`

```powershell
$body = @{
  customer_id = "11111111-1111-4111-8111-111111111111"
  address_id = "33333333-3333-4333-8333-333333333333"
  items = @(
    @{
      product_id = "22222222-2222-4222-8222-222222222222"
      quantity = "2"
    },
    @{
      product_id = "44444444-4444-4444-8444-444444444444"
      quantity = "1"
      unit_price = "4.50"
    }
  )
  notes = "Pedido ficticio para documentacion"
} | ConvertTo-Json -Depth 4

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/orders `
  -ContentType "application/json" `
  -Body $body
```

### Listar pedidos

`GET /api/v1/orders`

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/orders
```

Filtros opcionales:

```powershell
$customerId = "11111111-1111-4111-8111-111111111111"
Invoke-RestMethod `
  "http://localhost:8000/api/v1/orders?customer_id=$customerId"

Invoke-RestMethod `
  "http://localhost:8000/api/v1/orders?status_code=pendiente"
```

### Obtener un pedido por ID

`GET /api/v1/orders/{order_id}`

```powershell
$orderId = "55555555-5555-4555-8555-555555555555"
Invoke-RestMethod "http://localhost:8000/api/v1/orders/$orderId"
```

### Actualizar estado

`PATCH /api/v1/orders/{order_id}/status`

```powershell
$orderId = "55555555-5555-4555-8555-555555555555"
$body = @{ status_code = "asignado" } | ConvertTo-Json

Invoke-RestMethod `
  -Method Patch `
  -Uri "http://localhost:8000/api/v1/orders/$orderId/status" `
  -ContentType "application/json" `
  -Body $body
```

Los estados finales no pueden cambiar nuevamente.

### Cancelar un pedido

`PATCH /api/v1/orders/{order_id}/cancel`

```powershell
$orderId = "55555555-5555-4555-8555-555555555555"
Invoke-RestMethod `
  -Method Patch `
  -Uri "http://localhost:8000/api/v1/orders/$orderId/cancel"
```

La cancelación cambia el estado del pedido a `cancelado`.

## Formato uniforme de errores

Las respuestas de error siguen este contrato:

```json
{
  "error": {
    "code": "CUSTOMER_NOT_FOUND",
    "message": "Customer not found.",
    "details": {}
  }
}
```

Los códigos HTTP usados son:

- `400`: regla de negocio inválida.
- `404`: recurso inexistente.
- `409`: duplicado o conflicto.
- `422`: validación de entrada.
- `500`: error inesperado protegido.

### Cliente inexistente

```json
{
  "error": {
    "code": "CUSTOMER_NOT_FOUND",
    "message": "Customer not found.",
    "details": {}
  }
}
```

### SKU de producto duplicado

```json
{
  "error": {
    "code": "PRODUCT_SKU_ALREADY_EXISTS",
    "message": "Product SKU is already registered.",
    "details": {}
  }
}
```

### Producto inactivo en un pedido

```json
{
  "error": {
    "code": "ORDER_PRODUCT_INACTIVE",
    "message": "Inactive products cannot be ordered.",
    "details": {}
  }
}
```

### Error de validación

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {
      "errors": [
        {
          "field": "body.price",
          "message": "Input should be greater than or equal to 0",
          "type": "greater_than_equal"
        }
      ]
    }
  }
}
```

### Error interno

```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Internal server error.",
    "details": {}
  }
}
```

Los errores internos nunca deben exponer trazas, credenciales ni detalles
sensibles.

## Seguridad

- No utilizar datos reales de clientes en ejemplos, pruebas o documentación.
- No exponer API keys, tokens ni credenciales en solicitudes compartidas.
- No subir archivos `.env` al repositorio.
- Usar variables de entorno y credenciales distintas por ambiente.
