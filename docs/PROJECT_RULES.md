# Project Rules

Reglas de trabajo para mantener Agente Activa ordenado, seguro y facil de
continuar.

## Seguridad y datos

- No subir archivos `.env` reales.
- No subir API keys, tokens ni credenciales.
- No subir datos reales de clientes.
- No subir telefonos reales.
- No subir direcciones reales.
- Usar datos ficticios en documentacion, pruebas y ejemplos.
- Revisar cuidadosamente cualquier archivo generado antes de versionarlo.
- No guardar tokens o credenciales en `localStorage` ni `sessionStorage`.
- No exponer credenciales con variables `NEXT_PUBLIC_*`.

## Backend

- No modificar Docker Compose sin necesidad clara.
- No cambiar modelos ORM sin evaluar si requiere migracion Alembic.
- Si se cambia estructura de datos, crear migracion y prueba correspondiente.
- Mantener reglas de negocio en servicios backend, no en la UI.
- Preferir repositorios y servicios existentes antes de crear rutas directas.
- Toda funcionalidad nueva debe tener pruebas.
- Mantener contrato uniforme de errores.

## Agente conversacional

- Mantener `simulate-message` y `simulate-conversation-message` como flujos de
  simulacion/conversacion; no deben crear pedidos reales.
- El webhook WhatsApp no debe crear pedidos reales automaticamente ni llamar
  APIs externas de Meta mientras siga en modo preparacion.
- La creacion real desde el agente debe pasar por `confirm-order`, con
  `AGENT_SIMULATION_TOKEN`, `confirmation_summary` pendiente, datos completos y
  confirmacion explicita.
- No crear clientes automaticamente desde conversaciones.
- No enviar mensajes reales a WhatsApp sin un bloque especifico de envio
  saliente, seguridad y validacion.

## Frontend

- No romper Server Components.
- No hacer llamadas directas desde navegador a FastAPI.
- No usar `NEXT_PUBLIC_API_BASE_URL`.
- No modificar CORS para resolver problemas que deben ser server-side.
- No usar polling innecesario.
- No hacer llamadas por cada tecla.
- Las mutaciones deben pasar por Server Actions cuando aplique.
- Centralizar llamadas HTTP en `apps/admin/src/lib/api/`.
- Mantener resultados serializables entre Server Actions y cliente.
- Mantener `npm run dev` del admin en una configuracion validada localmente; si
  se cambia el bundler, revalidar login, proxy, CSP y headers.

## Autenticacion del panel

- Usar `apps/admin/src/proxy.ts` para proteccion de rutas en Next.js 16.
- No crear `middleware.ts` para este panel.
- Mantener `/login` como ruta publica.
- Proteger `/`, `/customers`, `/products`, `/orders`, `/health` y rutas internas.
- Mantener la cookie `agente_activa_session` como `HttpOnly`, `sameSite: "lax"`,
  `secure` solo en `production`, `path: "/"` y maxAge de 8 horas.
- Firmar la sesion con HMAC SHA-256 usando `AUTH_SECRET`.
- Mantener `ADMIN_PASSWORD_HASH` en formato `scrypt`.
- No guardar contrasenas ni hashes dentro de la cookie.
- Verificar sesion dentro de Server Actions mutantes; no confiar solo en
  `proxy.ts`.
- Validar `API_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y
  `AUTH_SECRET` desde `apps/admin/src/lib/admin-env.ts`.
- No restaurar fallback silencioso para `API_BASE_URL`; debe estar configurada.
- Mantener headers defensivos del panel en `apps/admin/next.config.ts`.
- Mantener CSP prudente por ambiente: desarrollo debe permitir Next dev/HMR y
  produccion no debe habilitar `unsafe-eval`.
- Activar `Strict-Transport-Security` solo en `production`.
- Documentar cambios de seguridad en `docs/SECURITY.md`.

## Rendimiento

- No calcular metricas pesadas en frontend.
- Preferir backend optimizado con endpoints claros.
- Evitar N+1 en listados y dashboards.
- Usar `selectinload` o agregaciones SQL cuando corresponda.
- El dashboard debe consumir `GET /api/v1/dashboard/overview`, no multiples
  endpoints de pedidos, clientes y productos.

## Dependencias

- No instalar dependencias nuevas sin justificar.
- Antes de agregar una libreria, revisar si el stack actual ya resuelve el caso.
- Si se agrega una dependencia, documentar por que y validar build/pruebas.

## Diseno

- Mantener identidad visual celeste y blanca.
- Colores base:
  - Celeste principal: `#0EA5E9`
  - Celeste suave: `#E0F2FE`
  - Azul agua: `#0284C7`
  - Azul profundo: `#075985`
  - Blanco: `#FFFFFF`
  - Fondo claro: `#F8FCFF`
  - Texto oscuro: `#0F172A`
  - Bordes suaves: `#BAE6FD`
- Mantener contraste legible.
- Evitar saturar la pantalla.
- Validar responsive basico cuando se cambie UI.

## Documentacion

- Mantener README y docs alineados con el estado real.
- Actualizar `docs/API_USAGE.md` si cambia un endpoint.
- Actualizar `docs/DATA_MODEL.md` si cambia estructura de datos.
- Actualizar `docs/ADMIN_PANEL.md` si cambia el panel.
- Actualizar `docs/TESTING.md` si cambia la forma de validar.
- Usar ejemplos ficticios.

## Flujo de validacion recomendado

Backend:

```bash
docker compose exec api python -m pytest
docker compose exec api python -m ruff check app tests
```

Frontend:

```bash
cd apps/admin
npm run lint
npm run typecheck
npm run build
```

Health:

```bash
curl http://localhost:8000/api/v1/health
```

## Antes de implementar WhatsApp

- Confirmar que el panel administrativo sigue protegido.
- Validar seguridad de API.
- Revisar manejo de secretos.
- Confirmar que el agente usara servicios existentes y no duplicara reglas.
