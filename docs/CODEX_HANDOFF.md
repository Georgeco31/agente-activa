# Codex Handoff

Este documento es el punto de entrada para continuar Agente Activa desde otro
equipo, especialmente una MacBook nueva con Codex. Resume el contexto necesario
sin depender del historial de chat.

## Que es el MVP

Agente Activa / Agua Activa es un MVP para una empresa de venta y reparto de
agua. El sistema centraliza clientes, telefonos, alias, direcciones, productos,
pedidos y un dashboard operativo. El panel administrativo ya esta protegido con
autenticacion basica de MVP y headers defensivos antes de avanzar hacia el
agente de ventas por WhatsApp.

## Problema que resuelve

El negocio recibe pedidos y consultas por canales como WhatsApp. Sin un sistema
central, la informacion queda dispersa y es facil duplicar clientes, perder
referencias de direccion o crear pedidos incompletos.

El MVP resuelve:

- Identificacion de clientes por telefono, nombre, alias, direccion o referencia.
- Evitar duplicados razonables de clientes.
- Gestion administrativa de clientes, productos y pedidos.
- Seguimiento de estados de pedidos.
- Dashboard operativo para despacho y ventas entregadas.
- Base tecnica para que un futuro agente de WhatsApp use los mismos servicios.

## Arquitectura general

```text
apps/admin  -> Next.js App Router, Server Components, Server Actions
apps/api    -> FastAPI, SQLAlchemy 2.0, Pydantic, Alembic
PostgreSQL  -> Base de datos operativa
Docker      -> API y PostgreSQL
```

El frontend no llama directamente a FastAPI desde el navegador. Next.js consume
la API del lado servidor usando `API_BASE_URL`. No se usa CORS ni
`NEXT_PUBLIC_API_BASE_URL`. Las rutas del panel se protegen con
`apps/admin/src/proxy.ts` y una cookie HttpOnly firmada. La configuracion del
panel se valida de forma estricta desde variables de entorno.

## Estructura de carpetas

```text
.
|-- apps/
|   |-- admin/
|   |   |-- src/app/
|   |   |-- src/components/
|   |   `-- src/lib/api/
|   `-- api/
|       |-- alembic/
|       |-- app/api/
|       |-- app/models/
|       |-- app/repositories/
|       |-- app/schemas/
|       |-- app/services/
|       |-- app/seeds/
|       `-- tests/
|-- docs/
|-- docker-compose.yml
`-- README.md
```

## Backend actual

Stack: FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, Pydantic, Pytest, Ruff y
Docker Compose.

El backend contiene modelos ORM, migraciones, seed de estados, normalizacion de
telefonos y texto, busqueda flexible, deteccion de duplicados, registro seguro
de clientes, endpoints de clientes/productos/pedidos/dashboard y contrato
uniforme de errores.

## Frontend actual

Stack: Next.js App Router, React, TypeScript, Server Components, Server Actions
y ESLint.

El panel administrativo tiene dashboard operativo, modulos de clientes,
productos y pedidos, healthcheck visual, capa HTTP centralizada en
`src/lib/api/http.ts`, login administrativo, logout server-side, guardas de
sesion en Server Actions, validacion centralizada de entorno, headers de
seguridad e identidad visual celeste/blanca.

## Bloques completados

1. Backend base: FastAPI, Docker Compose, PostgreSQL y healthcheck.
2. Modelos ORM, Alembic, migracion inicial y seed de estados.
3. Normalizacion, busqueda flexible, duplicados y registro seguro de clientes.
4. Endpoints administrativos de clientes, productos y pedidos.
5. Contrato uniforme de errores.
6. Documentacion de API y pruebas.
7. Panel admin Next.js con clientes, productos, pedidos y dashboard.
8. Dashboard operativo real con una sola llamada server-side.
9. Seguridad basica del panel: login, sesion HttpOnly, proteccion de rutas y logout.
10. Endurecimiento de seguridad: validacion de entorno y headers defensivos.

## Autenticacion del panel

El panel usa un administrador unico definido por variables de entorno:

- `ADMIN_USERNAME`
- `ADMIN_PASSWORD_HASH`
- `AUTH_SECRET`

`ADMIN_PASSWORD_HASH` usa formato `scrypt$16384$8$1$<salt-base64url>$<hash-base64url>`.
`AUTH_SECRET` firma la cookie `agente_activa_session` con HMAC SHA-256.

La cookie es `HttpOnly`, `sameSite: "lax"`, `secure` solo en `production`,
`path: "/"` y expira en 8 horas. El payload contiene solo `username`, rol fijo
`admin`, `iat` y `exp`.

`/login` es publico. `/`, `/customers`, `/products`, `/orders`, `/health` y sus
rutas internas requieren sesion valida. Si falta sesion, `proxy.ts` redirige a
`/login?next=<ruta>`. Si un usuario autenticado abre `/login`, se redirige a
`/`. Las Server Actions de clientes, productos y pedidos tambien verifican
sesion antes de llamar a FastAPI.

## Endurecimiento del panel

`API_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y `AUTH_SECRET` son
obligatorias. `API_BASE_URL` debe ser una URL `http` o `https`; el hash debe
usar formato `scrypt$N$r$p$salt-base64url$hash-base64url`; `AUTH_SECRET` debe
tener al menos 32 caracteres. Los errores de configuracion no imprimen valores
secretos.

`next.config.ts` aplica headers:

- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options: DENY`;
- `Referrer-Policy: strict-origin-when-cross-origin`;
- `Permissions-Policy` restrictiva;
- `Content-Security-Policy`;
- `Strict-Transport-Security` solo en `production`.

La CSP de desarrollo permite lo necesario para Next dev y HMR. La documentacion
principal de seguridad esta en `docs/SECURITY.md`.

## Endpoints principales

Health:

- `GET /api/v1/health`

Dashboard:

- `GET /api/v1/dashboard/overview`

Clientes:

- `POST /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `GET /api/v1/customers/search`
- `POST /api/v1/customers/detect-duplicates`
- `POST /api/v1/customers/{customer_id}/phones`
- `POST /api/v1/customers/{customer_id}/aliases`
- `POST /api/v1/customers/{customer_id}/addresses`

Productos:

- `POST /api/v1/products`
- `GET /api/v1/products`
- `GET /api/v1/products/{product_id}`
- `GET /api/v1/products/search`
- `PATCH /api/v1/products/{product_id}`
- `PATCH /api/v1/products/{product_id}/deactivate`

Pedidos:

- `POST /api/v1/orders`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{order_id}`
- `PATCH /api/v1/orders/{order_id}/status`
- `PATCH /api/v1/orders/{order_id}/cancel`

## Endpoint dashboard

`GET /api/v1/dashboard/overview` devuelve el resumen operativo usado por el
dashboard con una sola llamada desde Next.js.

Parametros opcionales:

- `date=YYYY-MM-DD`
- `year=YYYY`
- `month=1-12`

Incluye pedidos del dia, pedidos por estado, ventas del dia, ventas del mes,
ventas por dia del mes, productos activos, total de clientes, ultimos pedidos y
alertas operativas simples.

Regla de ventas: una venta realizada es un pedido con estado actual
`entregado`. Como no existe `delivered_at`, las ventas se agrupan por
`created_at`.

## Contrato de errores

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": {}
  }
}
```

Reglas:

- Validaciones FastAPI/Pydantic: `422 VALIDATION_ERROR`.
- Reglas de negocio: `400`, `404` o `409`.
- Errores inesperados: `500 INTERNAL_SERVER_ERROR` sin trazas ni datos internos.

## Estado de pruebas

Ultima validacion conocida:

- Backend: `106 passed, 1 warning`.
- Ruff: `All checks passed`.
- Frontend: `npm run lint`, `npm run typecheck` y `npm run build` aprobados.
- Healthcheck: `status ok`, `database ok`.
- Dashboard endpoint funcionando.

## Lectura recomendada para Codex en otro equipo

1. `README.md`
2. `docs/CODEX_HANDOFF.md`
3. `docs/PROJECT_RULES.md`
4. `docs/MAC_SETUP.md`
5. `docs/ROADMAP.md`
6. `docs/DATA_MODEL.md`
7. `docs/API_USAGE.md`
8. `docs/ADMIN_PANEL.md`
9. `docs/SECURITY.md`
10. `docs/TESTING.md`

## Decisiones tecnicas importantes

- Backend y frontend viven en un monorepo.
- La API conserva reglas de negocio; la UI no decide reglas criticas.
- Next.js consume FastAPI del lado servidor.
- No usar `NEXT_PUBLIC_API_BASE_URL`.
- No usar CORS mientras el frontend no llame directo a FastAPI.
- No hacer polling ni llamadas por tecla.
- Dashboard consume un endpoint agregado optimizado.
- El panel se protege con `src/proxy.ts`, no con `middleware.ts` en Next.js 16.
- `API_BASE_URL` no tiene fallback silencioso; debe configurarse.
- Los headers de seguridad viven en `apps/admin/next.config.ts`.
- `npm run dev` del admin usa `next dev --webpack`; no cambiarlo sin
  revalidar login, proxy y CSP en desarrollo local.
- No guardar tokens ni credenciales en `localStorage` o `sessionStorage`.
- No exponer `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` ni `AUTH_SECRET` al cliente.
- Mantener pruebas para nuevas funcionalidades.
- Mantener documentacion actualizada.
- Mantener la identidad visual celeste y blanca.

## No cambiar sin validacion

- Modelos ORM y migraciones.
- Docker Compose.
- Contrato uniforme de errores.
- Comunicacion server-side Next.js -> FastAPI.
- Proteccion de rutas con `apps/admin/src/proxy.ts`.
- Cookie de sesion `agente_activa_session`.
- Regla de ventas basada en estado `entregado`.
- Restriccion de no usar datos reales.
- Colores y estilo base del panel.
- La decision de proteger el panel antes de implementar WhatsApp.
