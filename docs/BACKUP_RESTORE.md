# Backups y restauracion

Esta guia documenta backups locales de PostgreSQL para Agente Activa usando los
contenedores de Docker Compose.

Los backups pueden contener datos reales de clientes, telefonos, direcciones,
pedidos y conversaciones. No subir backups a GitHub ni guardarlos en carpetas
trackeadas.

## Convencion de nombres

Usar nombres con fecha y hora:

```text
agua_sales_YYYYMMDD_HHMM.dump
```

Ejemplo ficticio:

```text
agua_sales_20260630_0930.dump
```

Guardar backups locales en una carpeta no versionada, por ejemplo:

```bash
mkdir -p backups
```

## Crear backup

Crear el dump dentro del contenedor `db`:

```bash
docker compose exec db pg_dump -U agua_user -d agua_sales -Fc -f /tmp/agua_sales_YYYYMMDD_HHMM.dump
```

Copiarlo a la maquina local:

```bash
docker compose cp db:/tmp/agua_sales_YYYYMMDD_HHMM.dump backups/agua_sales_YYYYMMDD_HHMM.dump
```

Verificar que existe:

```bash
ls -lh backups/
```

## Cuando hacer backup

- Antes de aplicar migraciones.
- Antes de cambios grandes de version.
- Antes de restaurar otro backup.
- Diario si hay datos reales.
- Antes de mover datos entre maquinas.

## Restaurar backup

Copiar el backup al contenedor:

```bash
docker compose cp backups/agua_sales_YYYYMMDD_HHMM.dump db:/tmp/restore.dump
```

Restaurar:

```bash
docker compose exec db pg_restore -U agua_user -d agua_sales --clean --if-exists /tmp/restore.dump
```

Despues de restaurar, aplicar migraciones y seed:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python -m app.seeds.order_statuses
```

Validar:

```bash
curl http://localhost:8000/api/v1/health
docker compose exec api python -m pytest
```

## Advertencias de restore

`pg_restore --clean --if-exists` puede borrar o reemplazar objetos existentes en
la base de datos destino.

No ejecutar restore sobre una base de produccion sin backup previo y sin saber
exactamente que se esta haciendo.

Para produccion, restaurar primero en un entorno de prueba y validar datos,
migraciones y healthcheck antes de tocar la base principal.

## Probar una restauracion

Una prueba minima:

1. Crear backup.
2. Levantar un entorno local o base de prueba.
3. Restaurar el backup en esa base.
4. Ejecutar migraciones.
5. Ejecutar seed.
6. Validar healthcheck.
7. Revisar manualmente clientes, productos, pedidos y dashboard.

No considerar confiable un proceso de backup hasta haber probado una
restauracion.

## Que no subir

- `backups/`
- archivos `.dump`;
- archivos `.sql`;
- dumps comprimidos;
- datos reales de clientes;
- telefonos reales;
- direcciones reales.

Si se necesita compartir un backup operativo, hacerlo por un canal seguro y
fuera del repositorio.
