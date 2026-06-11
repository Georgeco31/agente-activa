# Panel administrativo

## Estado actual

Los Bloques 6B, 6C, 6D, 6E-B y 7A establecen la base tecnica y visual del panel
administrativo de Agente Activa e implementan los modulos funcionales de
clientes, productos, pedidos y el dashboard operativo.

Incluye:

- Next.js con App Router y TypeScript.
- Navegacion responsive para resumen, clientes, productos, pedidos y health.
- Rutas preparadas para los modulos administrativos.
- Cliente HTTP centralizado para FastAPI.
- Consulta real del endpoint `/api/v1/health`.
- Manejo visual de disponibilidad y errores de API.
- Busqueda explicita de clientes sin llamadas por cada tecla.
- Registro seguro de clientes mediante Server Actions.
- Deteccion y presentacion de posibles duplicados.
- Vista de detalle de cliente.
- Asociacion de telefonos, alias y direcciones.
- Listado y filtro de productos activos.
- Busqueda explicita de productos por nombre o SKU.
- Registro, detalle, actualizacion y desactivacion de productos.
- Listado de pedidos con informacion humana para despacho.
- Filtros explicitos de pedidos por cliente y estado.
- Creacion de pedidos conectando clientes, direcciones y productos activos.
- Detalle, cambio de estado y cancelacion de pedidos.
- Dashboard operativo obtenido mediante una sola consulta server-side.
- Metricas diarias, ventas entregadas, alertas y ultimos pedidos.

## Requisitos locales

- Node.js y npm instalados en Windows.
- Backend disponible en `http://localhost:8000`.

## Configuracion

La variable `API_BASE_URL` se usa exclusivamente del lado servidor:

```text
API_BASE_URL=http://localhost:8000
```

El ejemplo se encuentra en `apps/admin/.env.example`. No se usa
`NEXT_PUBLIC_API_BASE_URL`, porque el navegador no debe comunicarse directamente
con FastAPI en este bloque.

Si en el futuro Next.js se ejecuta dentro de un contenedor, podria requerirse:

```text
API_BASE_URL=http://host.docker.internal:8000
```

## Arquitectura de comunicacion

```text
Navegador
  -> Next.js App Router
    -> Server Component
      -> cliente HTTP centralizado
        -> FastAPI
```

La consulta de health se ejecuta en el servidor de Next.js. El boton Actualizar
solicita una nueva renderizacion del Server Component y no llama FastAPI desde
el navegador. Por esta razon, el Bloque 6B no necesita modificar CORS.

Archivos principales:

- `src/lib/config.ts`: configuracion privada de `API_BASE_URL`.
- `src/lib/api/http.ts`: cliente HTTP centralizado y server-only.
- `src/lib/api/errors.ts`: interpretacion del contrato uniforme de errores.
- `src/lib/api/health.ts`: acceso tipado al healthcheck.
- `src/app/health/page.tsx`: vista server-side del estado de la API.
- `src/lib/api/customers.ts`: acceso centralizado a endpoints de clientes.
- `src/lib/api/customer-types.ts`: contratos TypeScript del modulo.
- `src/app/customers/actions.ts`: mutaciones server-side.
- `src/app/customers/page.tsx`: busqueda, creacion y deteccion de duplicados.
- `src/app/customers/[customerId]/page.tsx`: detalle y asociacion de datos.
- `src/lib/api/products.ts`: acceso centralizado a endpoints de productos.
- `src/lib/api/product-types.ts`: contratos TypeScript del modulo.
- `src/app/products/actions.ts`: mutaciones server-side de productos.
- `src/app/products/page.tsx`: listado, busqueda y creacion.
- `src/app/products/[productId]/page.tsx`: detalle, edicion y desactivacion.
- `src/lib/api/orders.ts`: acceso centralizado a endpoints de pedidos.
- `src/lib/api/order-types.ts`: contratos TypeScript del modulo.
- `src/app/orders/actions.ts`: mutaciones server-side de pedidos.
- `src/app/orders/page.tsx`: listado operativo y filtros.
- `src/app/orders/new/page.tsx`: seleccion de cliente y creacion.
- `src/app/orders/[orderId]/page.tsx`: detalle, estado y cancelacion.
- `src/lib/api/dashboard.ts`: acceso server-only al resumen operativo.
- `src/lib/api/dashboard-types.ts`: contrato TypeScript del dashboard.
- `src/app/page.tsx`: dashboard operativo server-side.
- `src/components/dashboard/`: componentes visuales del resumen.

## Dashboard operativo

La pagina principal consume exclusivamente `GET /api/v1/dashboard/overview`.
FastAPI calcula conteos, sumas y agrupaciones mediante consultas SQL agregadas.
Next.js recibe un contrato listo para presentar y no consulta por separado
clientes, productos ni pedidos.

El dashboard permite seleccionar una fecha diaria y un mes de ventas mediante
un formulario GET. Cada envio produce una nueva renderizacion server-side; no
existe polling, carga mediante `useEffect` ni comunicacion directa desde el
navegador hacia FastAPI.

Incluye:

- Pedidos del dia y distribucion por estado.
- Ventas del dia y del mes.
- Grafico CSS de ventas entregadas por dia.
- Conteo de productos activos y clientes.
- Alertas operativas simples.
- Ultimos pedidos con informacion util para despacho.

Una venta realizada corresponde exclusivamente a un pedido cuyo estado actual
es `entregado`. Como el modelo todavia no contiene `delivered_at`, las ventas
del dia y del mes se agrupan usando `created_at`.

## Modulo de clientes

La busqueda se ejecuta unicamente cuando el usuario envia el formulario. La
pagina usa sus query params para solicitar resultados desde un Server Component,
por lo que no hay polling, llamadas por tecla ni solicitudes directas del
navegador hacia FastAPI.

Las operaciones de creacion y asociacion de datos se ejecutan mediante Server
Actions. Estas acciones realizan validaciones basicas para experiencia de
usuario, pero FastAPI conserva la validacion y decision final.

Operaciones disponibles:

- Buscar por telefono, nombre, alias, direccion o referencia.
- Crear un cliente con nombre y datos asociados opcionales.
- Detectar posibles duplicados y mostrar razones, score y confianza.
- Consultar detalle, telefonos, alias y direcciones.
- Agregar telefonos, alias y direcciones a un cliente existente.
- Mostrar errores uniformes enviados por FastAPI.

## Modulo de pedidos

El listado usa una unica consulta server-side por render y aprovecha la
respuesta enriquecida de FastAPI. Presenta numero de pedido, cliente, telefono
principal, direccion, referencia, estado, total y fecha sin realizar consultas
adicionales por pedido.

Los filtros por `customer_id` y `status_code` se ejecutan unicamente al enviar
el formulario. La creacion usa una busqueda explicita de cliente, carga
controlada de su detalle y productos activos, y un editor local para agregar o
quitar items sin llamadas HTTP desde el navegador.

Operaciones disponibles:

- Listar pedidos con informacion util para despacho.
- Filtrar por cliente y estado.
- Buscar y seleccionar clientes de forma explicita.
- Seleccionar una direccion real del cliente.
- Crear pedidos con uno o varios productos activos.
- Consultar detalle, items, importes y datos tecnicos.
- Cambiar estado de pedidos no finalizados.
- Cancelar pedidos mediante la accion especifica.
- Mostrar errores uniformes enviados por FastAPI.

## Modulo de productos

El listado y la busqueda se cargan desde Server Components. El listado puede
filtrar solo productos activos y la busqueda se ejecuta unicamente cuando el
usuario envia el formulario por nombre o SKU.

Las operaciones de creacion, actualizacion y desactivacion usan Server Actions.
El panel envia exclusivamente los campos aceptados por FastAPI y conserva
`price` como string en el contrato TypeScript.

Operaciones disponibles:

- Listar todos los productos o solo los activos.
- Buscar por nombre o SKU.
- Crear productos con SKU, nombre, unidad, precio, descripcion y estado.
- Consultar el detalle real del producto.
- Actualizar los campos permitidos por FastAPI.
- Desactivar productos sin borrado fisico.
- Mostrar errores uniformes enviados por FastAPI.

## Ejecutar localmente

Primero levantar el backend desde la raiz:

```powershell
docker compose up -d --build
```

Luego iniciar el panel:

```powershell
cd apps/admin
npm run dev
```

Abrir `http://localhost:3000`.

## Validar

Desde `apps/admin`:

```powershell
npm run lint
npm run typecheck
npm run build
```

Desde la raiz del repositorio:

```powershell
docker compose exec api python -m pytest
docker compose exec api python -m ruff check app tests
Invoke-RestMethod http://localhost:8000/api/v1/health
```

## Limites actuales

- No modifica el backend ni Docker Compose.
- No agrega autenticacion.
- No integra WhatsApp.
- No expone variables privadas al navegador.
