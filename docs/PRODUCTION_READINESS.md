# Preparacion para produccion futura

Agente Activa todavia no esta listo para exposicion publica. Este documento
resume lo que falta antes de migrar a VPS o nube.

## Estado actual

- Backend y PostgreSQL operan localmente con Docker Compose.
- Admin Next.js opera localmente fuera de contenedor.
- Panel administrativo tiene login, cookie HttpOnly y headers defensivos.
- Webhook WhatsApp esta en modo preparacion.
- No hay envio real a WhatsApp.
- No se debe exponer FastAPI directamente a internet.

## Requisitos antes de produccion publica

- Dominio propio.
- HTTPS obligatorio.
- Reverse proxy, por ejemplo Nginx, Caddy o equivalente gestionado.
- Separacion de ambientes: local, staging y production.
- Secretos distintos por ambiente.
- Backups automaticos y probados.
- Logs persistentes y sanitizados.
- Monitoreo de salud y recursos.
- Plan de rollback.
- Firewall con puertos minimos abiertos.
- Proteccion del backend: no publicar FastAPI sin controles.
- Estrategia de despliegue para el admin.
- Estrategia de imagenes o build reproducible.

## Variables de produccion

Las variables reales deben vivir en el proveedor de despliegue, gestor de
secretos o archivos locales fuera de Git.

No usar placeholders en produccion:

- `DATABASE_URL`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD_HASH`
- `AUTH_SECRET`
- `AGENT_SIMULATION_TOKEN`
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN`
- `WHATSAPP_APP_SECRET`

No usar variables `NEXT_PUBLIC_*` para credenciales.

## Reverse proxy y HTTPS

Un despliegue publico deberia enrutar:

- `https://admin.example.com` hacia el admin.
- `https://api.example.com` o una ruta interna hacia FastAPI, solo si hay
  controles suficientes.

El proxy debe:

- terminar TLS;
- redirigir HTTP a HTTPS;
- conservar headers seguros;
- limitar tamanos de request;
- registrar logs sin secretos;
- permitir healthchecks controlados.

## Base de datos

Para produccion, PostgreSQL no deberia exponerse publicamente.

Requisitos minimos:

- volumen persistente;
- backups automaticos;
- restauracion probada;
- credenciales fuertes;
- acceso limitado por red o firewall;
- monitoreo de espacio en disco.

## WhatsApp real

WhatsApp Cloud API necesita una URL publica HTTPS para webhooks. Antes de
habilitarlo:

- validar dominio y certificado;
- validar firma HMAC en todos los `POST`;
- revisar rate limiting;
- revisar logs;
- definir envio saliente real;
- definir manejo de errores y reintentos;
- evitar crear pedidos automaticamente desde webhook.

## Docker Compose de produccion

No existe `docker-compose.prod.example.yml` en este bloque.

Debe quedar para futuro cuando se defina:

- Dockerfile o estrategia del admin;
- reverse proxy;
- HTTPS;
- dominios;
- backups;
- secretos;
- logs;
- separacion staging/production.

## Scripts operativos

No se crean scripts en este bloque.

Scripts futuros utiles:

- backup de base;
- restore controlado;
- healthcheck;
- rotacion de backups;
- verificacion de secretos placeholders.

Antes de agregarlos, validar convenciones operativas en Mac y Linux.

## Rollback basico

Un rollback minimo deberia tener:

1. Backup reciente y probado.
2. Version anterior identificada en Git.
3. Imagen o build anterior disponible.
4. Procedimiento para detener servicios.
5. Procedimiento para restaurar base si hubo migraciones.
6. Healthcheck posterior al rollback.

No aplicar migraciones irreversibles sin backup y plan de vuelta.

## Que no esta listo todavia

- Exposicion publica completa.
- Reverse proxy configurado.
- HTTPS real.
- Admin dockerizado para produccion.
- Backups automaticos.
- Monitoreo y alertas.
- Rate limiting persistente.
- Autenticacion API propia.
- Roles reales.
- Auditoria avanzada.
- WhatsApp saliente real.
- CI/CD de despliegue.
