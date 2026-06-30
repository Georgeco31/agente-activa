# Seguridad

Esta guia resume la seguridad actual del panel administrativo y las reglas para
configurarlo sin exponer secretos.

## Bloque 8A

El Bloque 8A protege el panel administrativo con:

- login publico en `/login`;
- administrador unico configurado por variables de entorno;
- `ADMIN_PASSWORD_HASH` en formato `scrypt`;
- sesion firmada con `AUTH_SECRET`;
- cookie `agente_activa_session` `HttpOnly`;
- `sameSite: "lax"`;
- `secure` solo en `production`;
- `path: "/"`;
- expiracion de 8 horas con `iat`, `exp` y `maxAge`;
- proteccion de rutas con `apps/admin/src/proxy.ts`;
- logout con eliminacion de cookie;
- guardas de sesion en Server Actions mutantes.

No se usa `localStorage`, `sessionStorage` ni variables `NEXT_PUBLIC_*` para
credenciales.

## Bloque 8B

El Bloque 8B endurece configuracion y headers:

- `API_BASE_URL` es obligatorio y debe ser una URL valida `http` o `https`.
- `ADMIN_USERNAME` es obligatorio y no puede ser placeholder.
- `ADMIN_PASSWORD_HASH` es obligatorio, no puede ser placeholder y debe tener
  formato `scrypt$N$r$p$salt-base64url$hash-base64url`.
- `AUTH_SECRET` es obligatorio, no puede ser placeholder y debe tener al menos
  32 caracteres.
- Los errores de configuracion indican que variable esta mal sin imprimir el
  valor recibido.
- Next.js agrega headers defensivos:
  - `X-Content-Type-Options: nosniff`;
  - `X-Frame-Options: DENY`;
  - `Referrer-Policy: strict-origin-when-cross-origin`;
  - `Permissions-Policy` restrictiva;
  - `Content-Security-Policy` prudente;
  - `Strict-Transport-Security` solo en `production`.

La CSP de desarrollo permite lo necesario para Next dev y HMR. La CSP de
produccion es mas estricta, pero conserva compatibilidad con los scripts y
estilos que necesita Next.js.

## Bloque 9C

El Bloque 9C prepara un webhook entrante compatible con Meta/WhatsApp Cloud API
sin enviar mensajes reales:

- `WHATSAPP_WEBHOOK_ENABLED` controla si el webhook acepta verificacion y
  eventos.
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN` se usa solo para la verificacion `GET`.
- `WHATSAPP_APP_SECRET` se usa para validar `X-Hub-Signature-256` en `POST`.
- El `POST` lee el body crudo antes de parsear JSON.
- La firma debe tener formato `sha256=<hmac-hex>`.
- El HMAC se calcula con SHA-256 sobre el body crudo.
- La comparacion usa `compare_digest`.
- Los errores no imprimen verify token, app secret ni firma recibida.
- Los tipos no soportados se registran con metadata minima y no se procesan
  como pedidos.
- `outbound_sent` permanece en `false`; no hay envio saliente a Meta.

No se debe exponer el webhook a internet sin HTTPS, rate limiting, monitoreo,
logs sanitizados y una estrategia clara de manejo de secretos.

## Variables locales

Crear `apps/admin/.env.local` desde `apps/admin/.env.example`:

```bash
cp apps/admin/.env.example apps/admin/.env.local
```

Completar con valores reales locales:

```text
API_BASE_URL=http://localhost:8000
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=replace-with-scrypt-password-hash
AUTH_SECRET=replace-with-random-32-byte-secret
```

No subir `apps/admin/.env.local`.

Para el backend, `apps/api/.env.example` incluye placeholders de 9C:

```text
WHATSAPP_WEBHOOK_ENABLED=false
WHATSAPP_WEBHOOK_VERIFY_TOKEN=replace-with-whatsapp-webhook-verify-token
WHATSAPP_APP_SECRET=replace-with-whatsapp-app-secret
```

Los valores reales deben vivir solo en el entorno local o de despliegue.

## Generar AUTH_SECRET

En Mac:

```bash
openssl rand -base64 32
```

Guardar el resultado en `AUTH_SECRET`.

## Generar ADMIN_PASSWORD_HASH

En Mac:

```bash
read -s ADMIN_PASSWORD
export ADMIN_PASSWORD
node -e 'const crypto=require("node:crypto"); const password=process.env.ADMIN_PASSWORD; const salt=crypto.randomBytes(16); crypto.scrypt(password,salt,64,{N:16384,r:8,p:1},(error,key)=>{ if(error) throw error; console.log(`scrypt$16384$8$1$${salt.toString("base64url")}$${key.toString("base64url")}`); });'
unset ADMIN_PASSWORD
```

Guardar el resultado en `ADMIN_PASSWORD_HASH`. No guardar la contrasena real en
archivos versionados.

## Archivos que no se deben subir

- `.env`
- `.env.local`
- `apps/api/.env`
- `apps/admin/.env.local`
- `node_modules/`
- `.next/`
- archivos con API keys, tokens o credenciales;
- datos reales de clientes;
- telefonos reales;
- direcciones reales;
- dumps de base de datos;
- certificados o llaves privadas.

Los `.env.example` deben contener solo placeholders.

## Recomendaciones para produccion

- Usar HTTPS.
- Usar secretos fuertes y distintos por ambiente.
- Rotar `AUTH_SECRET` y credenciales si se filtran.
- No exponer FastAPI publicamente sin proteccion.
- No usar datos reales en entornos publicos o compartidos.
- Configurar backups y control de acceso fuera del repositorio.
- Validar que el hosting preserve headers de seguridad.
- Revisar logs para evitar que impriman secretos.
- Exponer el webhook de WhatsApp solo mediante HTTPS.
- Validar firma de Meta en todos los `POST`.
- Agregar rate limiting y monitoreo antes de pruebas publicas reales.
- Rotar `WHATSAPP_WEBHOOK_VERIFY_TOKEN` y `WHATSAPP_APP_SECRET` si se filtran.

## Pendientes futuros

Estos puntos no forman parte del MVP actual:

- usuarios en base de datos;
- roles y permisos reales;
- auditoria persistente por usuario;
- rate limiting persistente;
- autenticacion propia de la API;
- envio saliente real a WhatsApp;
- rotacion automatizada de sesiones;
- recuperacion de contrasena;
- OAuth o proveedor externo de identidad.
