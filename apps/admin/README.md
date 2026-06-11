# Panel administrativo de Agente Activa

Base inicial del panel administrativo construida con Next.js, App Router y
TypeScript. En el Bloque 6B incluye el shell de navegacion, rutas preparadas para
clientes, productos y pedidos, y una consulta server-side al healthcheck de
FastAPI.

## Ejecutar

Desde `apps/admin`:

```powershell
npm run dev
```

Abrir `http://localhost:3000`.

## Validar

```powershell
npm run lint
npm run typecheck
npm run build
```

La configuracion y las decisiones de arquitectura estan documentadas en
[`docs/ADMIN_PANEL.md`](../../docs/ADMIN_PANEL.md).
