# Checklist de despliegue local

Usar este checklist para levantar o revisar Agente Activa en una maquina local
o servidor interno.

## Codigo y entorno

- [ ] Repo clonado.
- [ ] Repo limpio o cambios locales entendidos con `git status --short`.
- [ ] Rama correcta seleccionada.
- [ ] Docker Desktop o Docker Engine funcionando.
- [ ] `docker compose version` responde correctamente.
- [ ] Node.js y npm instalados para el admin.
- [ ] Puertos revisados:
  - [ ] API `8000`.
  - [ ] PostgreSQL `5432`.
  - [ ] Admin `3000`.
- [ ] Firewall o red local revisada.
- [ ] Responsable operativo definido.

## Variables y secretos

- [ ] `apps/api/.env` creado desde `apps/api/.env.example` si aplica.
- [ ] `apps/admin/.env.local` creado desde `apps/admin/.env.example`.
- [ ] Placeholders reemplazados en entornos reales.
- [ ] `AUTH_SECRET` fuerte.
- [ ] `ADMIN_PASSWORD_HASH` generado con `scrypt`.
- [ ] `AGENT_SIMULATION_TOKEN` fuerte si se prueba el agente.
- [ ] `WHATSAPP_WEBHOOK_ENABLED=false` salvo prueba controlada.
- [ ] No hay tokens ni secretos en archivos versionados.

## Backend

- [ ] `docker compose up -d --build` ejecutado.
- [ ] Contenedores `api` y `db` arriba.
- [ ] Migraciones aplicadas con `alembic upgrade head`.
- [ ] Seed de estados ejecutado.
- [ ] Healthcheck OK.
- [ ] Dashboard endpoint responde.
- [ ] Pruebas backend ejecutadas si corresponde.
- [ ] Ruff ejecutado si corresponde.

## Frontend admin

- [ ] Dependencias instaladas con `npm install`.
- [ ] `npm run lint` OK.
- [ ] `npm run typecheck` OK.
- [ ] `npm run build` OK.
- [ ] `npm run dev` levanta el panel local.
- [ ] `/login` carga.
- [ ] Login correcto funciona.
- [ ] Dashboard carga autenticado.
- [ ] Clientes, productos, pedidos y health cargan autenticado.
- [ ] Logout funciona.

## Backups

- [ ] Backup creado con `pg_dump`.
- [ ] Backup copiado fuera del contenedor.
- [ ] Backup guardado fuera de carpetas trackeadas.
- [ ] Restauracion probada en entorno local o de prueba.
- [ ] Procedimiento de restore conocido.
- [ ] Procedimiento de rollback basico conocido.

## Seguridad y Git

- [ ] No hay `.env` trackeados.
- [ ] No hay `.env.local` trackeados.
- [ ] No hay backups trackeados.
- [ ] No hay datos reales en Git.
- [ ] No hay `node_modules/` trackeado.
- [ ] No hay `.next/` trackeado.
- [ ] No se exponen puertos publicamente sin proxy/HTTPS.
- [ ] No se habilito WhatsApp real.
- [ ] No se expuso FastAPI directamente a internet.

## Apagado

- [ ] Se conoce el procedimiento de apagado del admin: `Ctrl + C`.
- [ ] Se conoce el procedimiento de apagado de backend/base:

```bash
docker compose down
```

- [ ] Se entiende que `docker compose down -v` borra datos locales.
