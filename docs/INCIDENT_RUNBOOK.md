# Runbook de incidentes

Esta guia contiene pasos simples y seguros para fallas comunes en operacion
local. No reemplaza backups ni soporte tecnico.

Si hay riesgo de perdida de datos, detenerse y crear backup antes de hacer
cambios.

## Comandos basicos

Ver contenedores:

```bash
docker compose ps
```

Ver logs de API:

```bash
docker compose logs api
```

Ver logs de PostgreSQL:

```bash
docker compose logs db
```

Healthcheck:

```bash
./scripts/check-health.sh
```

Healthcheck manual de backend:

```bash
curl http://localhost:8000/api/v1/health
```

Revisar puertos:

```bash
lsof -i :3000
lsof -i :8000
```

## Backend no responde

1. Ejecutar `docker compose ps`.
2. Si `api` no esta arriba, intentar:

```bash
docker compose up -d
```

3. Revisar logs:

```bash
docker compose logs api
```

4. Validar health:

```bash
./scripts/check-health.sh
```

Si la base no responde, revisar la seccion PostgreSQL.

## Frontend no abre

1. Verificar que el admin este corriendo en `apps/admin`.
2. Revisar puerto:

```bash
lsof -i :3000
```

3. Iniciar si no esta corriendo:

```bash
cd apps/admin
npm run dev
```

4. Revisar que `API_BASE_URL` exista en `.env.local` sin mostrar secretos en
   chats, capturas ni logs compartidos.

## Login falla

1. Confirmar usuario correcto con la persona responsable.
2. Revisar que `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` y `AUTH_SECRET` existan
   en `apps/admin/.env.local`.
3. No pegar valores reales en chats ni documentos.
4. Si se cambio `AUTH_SECRET`, sesiones anteriores pueden quedar invalidas.
5. Reiniciar el dev server del admin si se actualizaron variables.

## Docker no levanta

1. Abrir Docker Desktop o revisar Docker Engine.
2. Ejecutar:

```bash
docker compose ps
```

3. Revisar logs si los contenedores arrancan y caen:

```bash
docker compose logs api
docker compose logs db
```

4. Revisar puertos ocupados:

```bash
lsof -i :8000
lsof -i :5432
```

No usar `docker compose down -v` salvo que se quiera borrar la base local.

## PostgreSQL no levanta

1. Revisar estado:

```bash
docker compose ps
```

2. Revisar logs:

```bash
docker compose logs db
```

3. Revisar espacio en disco de la maquina.
4. No borrar volumenes sin backup.
5. Si se requiere restaurar, seguir `docs/BACKUP_RESTORE.md`.

## Dashboard muestra datos inesperados

1. Verificar health.
2. Revisar filtros de fecha si aplica.
3. Revisar pedidos recientes.
4. Confirmar estados de pedidos.
5. Revisar si hubo restauracion de backup o carga manual reciente.

El dashboard depende de datos registrados; si estados estan mal, corregir el
flujo operativo de pedidos.

## Pedido duplicado

1. Revisar ambos pedidos.
2. Confirmar si el cliente queria dos pedidos o fue error.
3. Si fue error, cancelar el duplicado.
4. No borrar registros directamente.
5. Revisar `docs/ORDER_OPERATIONS.md`.

## Cliente mal ingresado

1. Buscar si existe cliente correcto.
2. Agregar telefono, alias o direccion al cliente correcto si corresponde.
3. Evitar crear otro duplicado.
4. Si un pedido quedo asociado al cliente incorrecto, revisar impacto operativo
   antes de cancelar o recrear.

## Restaurar backup

Restaurar backup puede ser destructivo. `pg_restore --clean --if-exists` puede
borrar o reemplazar objetos existentes.

Antes de restaurar:

1. Crear backup del estado actual si es posible.
2. Confirmar que se esta usando el archivo correcto.
3. Probar en entorno de prueba si hay datos importantes.
4. Seguir `docs/BACKUP_RESTORE.md`.

Comando local:

```bash
./scripts/restore-db.sh backups/archivo.dump
```

No restaurar sobre produccion sin backup previo y aprobacion del responsable.

## PC apagada por error

1. Encender la PC.
2. Abrir Docker.
3. Ejecutar:

```bash
docker compose up -d
docker compose ps
./scripts/check-health.sh
```

4. Levantar admin si corresponde.
5. Revisar pedidos recientes y ultimo backup.

## Corte de luz

1. Esperar que la energia sea estable.
2. Encender equipo o servidor.
3. Levantar Docker y servicios.
4. Verificar health.
5. Revisar dashboard y pedidos pendientes.
6. Crear backup cuando el sistema este estable.

Si la base no levanta despues del corte, no borrar volumenes. Revisar logs y
considerar restauracion desde backup probado.
