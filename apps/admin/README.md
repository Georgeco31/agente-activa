# Panel administrativo de Agente Activa

Base inicial del panel administrativo construida con Next.js, App Router y
TypeScript. En el Bloque 8A incluye autenticacion local del panel, sesion con
cookie HttpOnly y proteccion de rutas administrativas. En el Bloque 8B endurece
validacion de entorno y headers de seguridad.

## Variables locales

Copiar `apps/admin/.env.example` a `apps/admin/.env.local` y completar:

```text
API_BASE_URL=http://localhost:8000
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=replace-with-scrypt-password-hash
AUTH_SECRET=replace-with-random-32-byte-secret
```

`ADMIN_PASSWORD_HASH` usa el formato:

```text
scrypt$16384$8$1$<salt-base64url>$<hash-base64url>
```

`API_BASE_URL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y `AUTH_SECRET` son
obligatorias. Los placeholders no son validos para ejecutar el panel.

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

## Ejecutar

Desde `apps/admin`:

```powershell
npm run dev
```

El script usa `next dev --webpack` para mantener estable la validacion local en
Mac. Abrir `http://localhost:3000`.

## Validar

```powershell
npm run lint
npm run typecheck
npm run build
```

La configuracion y las decisiones de arquitectura estan documentadas en
[`docs/ADMIN_PANEL.md`](../../docs/ADMIN_PANEL.md).
Las reglas de seguridad estan documentadas en
[`docs/SECURITY.md`](../../docs/SECURITY.md).
