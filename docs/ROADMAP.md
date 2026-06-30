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
11. Nucleo conversacional backend y simulador interno:
   - `POST /api/v1/agent/simulate-message`;
   - deteccion basica de intenciones;
   - extraccion simple de cantidad, producto y direccion;
   - busqueda de cliente por telefono normalizado;
   - consulta de productos activos y pedidos del cliente;
   - proteccion con `AGENT_SIMULATION_TOKEN`;
   - sin WhatsApp real, sin webhook publico y sin crear pedidos.
12. Persistencia conversacional minima del agente:
   - tablas `conversation_sessions` y `conversation_messages`;
   - migracion `0002_conversation_persistence`;
   - `POST /api/v1/agent/simulate-conversation-message`;
   - `GET /api/v1/agent/conversations/{session_id}`;
   - `POST /api/v1/agent/conversations/{session_id}/close`;
   - acumulacion no destructiva de `extracted_data`;
   - mensajes inbound/outbound persistidos;
   - estados `active`, `waiting_for_customer`, `ready_for_confirmation`,
     `closed` y `expired`;
   - sin crear pedidos reales.
13. Webhook WhatsApp/Meta seguro en modo preparacion:
   - `GET /api/v1/whatsapp/webhook`;
   - `POST /api/v1/whatsapp/webhook`;
   - verificacion con `WHATSAPP_WEBHOOK_VERIFY_TOKEN`;
   - validacion `X-Hub-Signature-256` con HMAC-SHA256;
   - parseo defensivo de mensajes entrantes;
   - integracion con persistencia conversacional 9B;
   - tipos no soportados registrados sin romper el endpoint;
   - sin envio real a Meta y sin crear pedidos reales.
14. Confirmacion conversacional y creacion segura de pedidos reales:
   - `POST /api/v1/agent/conversations/{session_id}/confirm-order`;
   - confirmacion explicita requerida;
   - `confirmation_summary` pendiente en `extracted_data`;
   - validacion de cliente, telefono, producto, cantidad y direccion;
   - reutilizacion de `app.services.orders.create_order()`;
   - pedidos creados en estado `pendiente`;
   - auditoria `order_created_by_agent`;
   - bloqueo de duplicados recientes similares;
   - webhook WhatsApp sigue sin crear pedidos automaticamente.
15. Preparacion local escalable y checklist de despliegue:
   - `docs/LOCAL_DEPLOYMENT.md`;
   - `docs/BACKUP_RESTORE.md`;
   - `docs/DEPLOYMENT_CHECKLIST.md`;
   - `docs/PRODUCTION_READINESS.md`;
   - ejemplos seguros en `docs/env/`;
   - sin scripts operativos;
   - sin `docker-compose.prod.example.yml`;
   - sin cambios de logica backend/frontend.
16. Preparacion de operacion interna local:
   - `docs/INTERNAL_OPERATIONS.md`;
   - `docs/INITIAL_DATA_LOAD.md`;
   - `docs/ORDER_OPERATIONS.md`;
   - `docs/DAILY_OPERATIONS_CHECKLIST.md`;
   - `docs/INCIDENT_RUNBOOK.md`;
   - roles operativos manuales sin permisos en codigo;
   - sin datos reales en el repo;
   - sin cambios de logica backend/frontend.
17. Scripts seguros de backup, restore y healthcheck local:
   - `scripts/backup-db.sh`;
   - `scripts/restore-db.sh`;
   - `scripts/check-health.sh`;
   - `scripts/stop-local.sh`;
   - backups guardados en `backups/`;
   - restore con confirmacion exacta `RESTORE`;
   - `backups/`, `*.dump` y `*.backup` ignorados por Git;
   - sin `scripts/start-local.sh`.

## Siguiente bloque recomendado

### Bloque 9E: Simulador visual o confirmacion especial de duplicados

Objetivo recomendado: mejorar la operacion del agente sin exponer todavia envio
real de WhatsApp. Hay dos rutas razonables: un simulador visual interno en el
panel o una confirmacion especial controlada para pedidos duplicados recientes.

Alcance sugerido:

- revisar conversaciones y resultados desde una interfaz protegida; o
- permitir confirmacion especial para crear un pedido adicional similar;
- mantener `AGENT_SIMULATION_TOKEN` o autenticacion administrativa;
- no enviar WhatsApp real todavia.

## Temas pendientes

- Roles futuros.
- Seguridad API.
- Auditoria basica.
- Envio futuro de respuestas reales por WhatsApp.
- Confirmacion especial para duplicados recientes.
- Reportes avanzados.
- Gestion avanzada de rutas y repartidores.
- Docker Compose de produccion, reverse proxy y HTTPS.
- `scripts/start-local.sh` cuando se valide una convencion diaria.
- Preparacion de servidor local.
- WhatsApp saliente controlado.
- Piloto con clientes reales.
- Roles y permisos reales.

## Orden recomendado

1. Bloque 9E: simulador visual interno o confirmacion especial de duplicados.
2. Bloque 8C: roles o permisos basicos si el negocio lo requiere.
3. Seguridad API antes de exponer webhooks publicos.
4. Bloque 10D: preparacion de servidor local.
5. Bloque 11A: WhatsApp saliente controlado.
6. Bloque 11B: piloto con clientes reales.
7. Reportes operativos mas detallados.

## Que no hacer todavia

- No pagos.
- No inventario avanzado.
- No rutas avanzadas.
- No repartidores.
- No exportacion PDF/Excel.
- No WhatsApp real antes de confirmar seguridad, firmas, rate limiting y manejo
  de secretos.
- No crear integraciones externas sin aislar credenciales.
- No crear pedidos automaticamente desde el agente sin confirmacion explicita.
- No agregar dependencias grandes sin justificar.

## Criterios para aceptar nuevos bloques

Cada bloque deberia cumplir:

- Alcance pequeno y validable.
- Sin datos reales en pruebas ni documentacion.
- Pruebas automatizadas cuando toque reglas o endpoints.
- `python -m pytest` y Ruff limpios para backend.
- `npm run lint`, `npm run typecheck` y `npm run build` limpios para frontend.
- Documentacion actualizada cuando cambie comportamiento, setup o contratos.
