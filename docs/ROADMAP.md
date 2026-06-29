# Roadmap

Este roadmap resume el estado del MVP y el orden recomendado para continuar.

## Bloques completados

1. Backend base con FastAPI, Docker Compose, PostgreSQL y healthcheck.
2. Modelos ORM, Alembic, migracion inicial y seed de estados.
3. Normalizacion, busqueda flexible, deteccion de duplicados y registro seguro.
4. Endpoints de clientes, productos y pedidos.
5. Contrato uniforme de errores.
6. Documentacion de API y pruebas.
7. Panel administrativo con Next.js:
   - base visual;
   - clientes;
   - productos;
   - pedidos;
   - dashboard operativo.
8. Dashboard operativo real:
   - `GET /api/v1/dashboard/overview`;
   - ventas del dia;
   - ventas del mes;
   - grafico mensual;
   - pedidos por estado;
   - ultimos pedidos;
   - alertas operativas;
   - diseno celeste y blanco;
   - una sola llamada server-side desde el frontend.
9. Seguridad y autenticacion basica del panel:
   - login publico en `/login`;
   - administrador unico por variables de entorno;
   - verificacion de `ADMIN_PASSWORD_HASH` con `scrypt`;
   - sesion firmada en cookie HttpOnly;
   - proteccion de rutas con `src/proxy.ts`;
   - logout con eliminacion de cookie;
   - guardas de sesion en Server Actions mutantes;
   - documentacion de configuracion segura.
10. Endurecimiento de seguridad y configuracion:
   - validacion estricta de `API_BASE_URL`;
   - validacion de `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y `AUTH_SECRET`;
   - eliminacion del fallback silencioso de API;
   - headers defensivos en Next.js;
   - CSP prudente por ambiente;
   - documentacion de seguridad en `docs/SECURITY.md`.

## Siguiente bloque recomendado

### Bloque 8C: Roles o permisos basicos

Objetivo recomendado: evaluar si el negocio necesita permisos basicos antes de
avanzar hacia WhatsApp o exponer mas funciones operativas.

Alcance sugerido:

- Roles simples si existen operadores distintos.
- Politicas basicas de autorizacion por modulo si son necesarias.
- Auditoria basica si el negocio requiere trazabilidad por usuario.
- Pruebas backend y frontend acordes al alcance.
- Documentacion de configuracion segura.

## Temas pendientes

- Roles futuros.
- Seguridad API.
- Auditoria basica.
- Integracion futura con WhatsApp/agente.
- Reportes avanzados.
- Gestion avanzada de rutas y repartidores.

## Orden recomendado

1. Bloque 8C: roles o permisos basicos si el negocio lo requiere.
2. Bloque 9A: preparacion de canal WhatsApp y webhook.
3. Bloque 9B: agente conversacional usando servicios existentes.
4. Bloque 10A: reportes operativos mas detallados.

## Que no hacer todavia

- No pagos.
- No inventario avanzado.
- No rutas avanzadas.
- No repartidores.
- No exportacion PDF/Excel.
- No WhatsApp antes de confirmar seguridad y manejo de secretos.
- No crear integraciones externas sin aislar credenciales.
- No agregar dependencias grandes sin justificar.

## Criterios para aceptar nuevos bloques

Cada bloque deberia cumplir:

- Alcance pequeno y validable.
- Sin datos reales en pruebas ni documentacion.
- Pruebas automatizadas cuando toque reglas o endpoints.
- `python -m pytest` y Ruff limpios para backend.
- `npm run lint`, `npm run typecheck` y `npm run build` limpios para frontend.
- Documentacion actualizada cuando cambie comportamiento, setup o contratos.
