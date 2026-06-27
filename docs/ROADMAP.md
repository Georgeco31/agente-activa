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

## Siguiente bloque recomendado

### Bloque 8A: Seguridad y autenticacion del panel

Objetivo recomendado: proteger el panel administrativo antes de conectar
WhatsApp o exponer mas funciones operativas.

Alcance sugerido:

- Autenticacion basica del panel.
- Proteccion de rutas en Next.js.
- Sesiones.
- Logout.
- Validacion de variables de entorno necesarias.
- Primer modelo de usuario si se decide persistir usuarios.
- Pruebas backend y frontend acordes al alcance.
- Documentacion de configuracion segura.

## Temas pendientes

- Autenticacion.
- Proteccion de rutas.
- Sesiones.
- Roles futuros.
- Seguridad API.
- Validacion de variables de entorno.
- Auditoria basica.
- Integracion futura con WhatsApp/agente.
- Reportes avanzados.
- Gestion avanzada de rutas y repartidores.

## Orden recomendado

1. Bloque 8A: seguridad y autenticacion del panel.
2. Bloque 8B: roles o permisos basicos si el negocio lo requiere.
3. Bloque 9A: preparacion de canal WhatsApp y webhook.
4. Bloque 9B: agente conversacional usando servicios existentes.
5. Bloque 10A: reportes operativos mas detallados.

## Que no hacer todavia

- No pagos.
- No inventario avanzado.
- No rutas avanzadas.
- No repartidores.
- No exportacion PDF/Excel.
- No WhatsApp antes de proteger el panel.
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
