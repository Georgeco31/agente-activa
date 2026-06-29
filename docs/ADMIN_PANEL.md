# Panel administrativo

## Estado actual

Los Bloques 6B, 6C, 6D, 6E-B, 7A, 8A y 8B establecen la base tecnica y visual
del panel administrativo de Agente Activa, implementan los modulos funcionales
de clientes, productos, pedidos y dashboard operativo, protegen el panel con
autenticacion basica de MVP y endurecen configuracion y headers.

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
- Pantalla publica de login.
- Proteccion de rutas administrativas con `src/proxy.ts`.
- Sesion firmada en cookie HttpOnly.
- Logout server-side que elimina la cookie.
- Guardas de sesion en Server Actions mutantes.
- Validacion obligatoria de variables de entorno del panel.
- Headers defensivos de seguridad desde Next.js.

## Requisitos locales

- Node.js y npm instalados.
- Backend disponible en `http://localhost:8000`.

## Configuracion

La variable `API_BASE_URL` se usa exclusivamente del lado servidor. Las
credenciales del administrador y el secreto de sesion tambien viven solo en el
servidor:

```text
API_BASE_URL=http://localhost:8000
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=replace-with-scrypt-password-hash
AUTH_SECRET=replace-with-random-32-byte-secret
```

El ejemplo se encuentra en `apps/admin/.env.example`. No se usa
`NEXT_PUBLIC_API_BASE_URL`, porque el navegador no debe comunicarse directamente
con FastAPI en este bloque. Tampoco se usan variables `NEXT_PUBLIC_*` para
credenciales. `API_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y
`AUTH_SECRET` son obligatorias y no aceptan placeholders.

`ADMIN_PASSWORD_HASH` usa `scrypt` nativo de Node.js con este formato:

```text
scrypt$16384$8$1$<salt-base64url>$<hash-base64url>
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

Si en el futuro Next.js se ejecuta dentro de un contenedor, podria requerirse:

```text
API_BASE_URL=http://host.docker.internal:8000
```

## Arquitectura de comunicacion

```text
Navegador
  -> Next.js proxy.ts valida sesion
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
- `src/lib/admin-env.ts`: validacion centralizada de variables del panel.
- `src/proxy.ts`: proteccion de rutas y redireccion a `/login`.
- `src/lib/auth/session-token.ts`: firma y verificacion HMAC SHA-256 de sesion.
- `src/lib/auth/session.ts`: lectura, creacion y eliminacion de cookie.
- `src/lib/auth/credentials.ts`: verificacion server-side de usuario y hash.
- `src/lib/auth/password.ts`: verificacion `scrypt` con `timingSafeEqual`.
- `src/lib/auth/action-guard.ts`: guarda de sesion para Server Actions.
- `src/app/login/page.tsx`: pantalla publica de login.
- `src/app/login/actions.ts`: Server Action de autenticacion.
- `src/app/logout/route.ts`: logout por `POST`.
- `src/app/(protected)/layout.tsx`: shell administrativo protegido.
- `next.config.ts`: headers de seguridad y CSP por ambiente.
- `src/lib/api/http.ts`: cliente HTTP centralizado y server-only.
- `src/lib/api/errors.ts`: interpretacion del contrato uniforme de errores.
- `src/lib/api/health.ts`: acceso tipado al healthcheck.
- `src/app/(protected)/health/page.tsx`: vista server-side del estado de la API.
- `src/lib/api/customers.ts`: acceso centralizado a endpoints de clientes.
- `src/lib/api/customer-types.ts`: contratos TypeScript del modulo.
- `src/app/customers/actions.ts`: mutaciones server-side.
- `src/app/(protected)/customers/page.tsx`: busqueda, creacion y deteccion de duplicados.
- `src/app/(protected)/customers/[customerId]/page.tsx`: detalle y asociacion de datos.
- `src/lib/api/products.ts`: acceso centralizado a endpoints de productos.
- `src/lib/api/product-types.ts`: contratos TypeScript del modulo.
- `src/app/products/actions.ts`: mutaciones server-side de productos.
- `src/app/(protected)/products/page.tsx`: listado, busqueda y creacion.
- `src/app/(protected)/products/[productId]/page.tsx`: detalle, edicion y desactivacion.
- `src/lib/api/orders.ts`: acceso centralizado a endpoints de pedidos.
- `src/lib/api/order-types.ts`: contratos TypeScript del modulo.
- `src/app/orders/actions.ts`: mutaciones server-side de pedidos.
- `src/app/(protected)/orders/page.tsx`: listado operativo y filtros.
- `src/app/(protected)/orders/new/page.tsx`: seleccion de cliente y creacion.
- `src/app/(protected)/orders/[orderId]/page.tsx`: detalle, estado y cancelacion.
- `src/lib/api/dashboard.ts`: acceso server-only al resumen operativo.
- `src/lib/api/dashboard-types.ts`: contrato TypeScript del dashboard.
- `src/app/(protected)/page.tsx`: dashboard operativo server-side.
- `src/components/dashboard/`: componentes visuales del resumen.

## Autenticacion y sesiones

`/login` es la unica pantalla publica del panel. Si el usuario ya tiene una
sesion valida e intenta abrir `/login`, `src/proxy.ts` redirige a `/`.

Las rutas administrativas `/`, `/customers`, `/products`, `/orders`, `/health`
y sus rutas internas requieren la cookie `agente_activa_session`. Si no existe
o no valida, `src/proxy.ts` redirige a `/login?next=<ruta>`.

La cookie:

- es `HttpOnly`;
- usa `sameSite: "lax"`;
- usa `secure` solo en `production`;
- tiene `path: "/"`;
- dura 8 horas;
- contiene solo `username`, rol fijo `admin`, `iat` y `exp`;
- se firma con HMAC SHA-256 usando `AUTH_SECRET`.

El logout se ejecuta con `POST /logout`, elimina la cookie desde el servidor y
redirige a `/login`. No se usa `localStorage`, `sessionStorage` ni credenciales
en el navegador.

Las Server Actions de clientes, productos y pedidos verifican sesion antes de
llamar a FastAPI. Esto evita confiar solo en `proxy.ts`, porque las Server
Actions pueden invocarse por `POST` directo.

## Headers de seguridad

Next.js envia headers defensivos para todas las rutas:

- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options: DENY`;
- `Referrer-Policy: strict-origin-when-cross-origin`;
- `Permissions-Policy` restrictiva;
- `Content-Security-Policy` prudente;
- `Strict-Transport-Security` solo en `production`.

La CSP de desarrollo permite `unsafe-eval` y conexiones locales necesarias para
Next dev y HMR. La CSP de produccion evita `unsafe-eval`, conserva
compatibilidad con scripts y estilos necesarios de Next.js, y no habilita
conexiones al backend desde el navegador.

Mas detalles estan en `docs/SECURITY.md`.

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

`npm run dev` usa `next dev --webpack` para mantener estable la validacion local
en Mac.

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
- No integra WhatsApp.
- No expone variables privadas al navegador.
- No implementa roles reales.
- No implementa recuperacion de contrasena.
- No implementa OAuth.
- No implementa rate limiting avanzado.
