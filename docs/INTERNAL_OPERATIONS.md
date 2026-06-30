# Operacion interna diaria

Esta guia describe como usar Agente Activa en operacion interna local. No
implementa roles tecnicos ni permisos en codigo; define responsabilidades
manuales para el MVP.

No usar esta guia como instruccion para exponer el sistema a internet ni para
conectar WhatsApp real.

## Roles operativos manuales

Administrador del sistema:

- enciende el equipo o servidor interno;
- levanta backend, base de datos y panel;
- revisa healthcheck;
- mantiene variables locales y backups;
- apaga el sistema si corresponde.

Persona que toma pedidos:

- busca clientes antes de crear registros;
- actualiza telefonos, alias y direcciones;
- crea pedidos confirmados;
- revisa duplicados antes de guardar informacion nueva.

Persona que revisa dashboard:

- revisa ventas, pedidos del dia y alertas;
- comunica pendientes al equipo operativo;
- valida que los estados esten actualizados.

Encargado de despacho o repartidor:

- revisa pedidos pendientes y asignados;
- actualiza o informa estados operativos;
- confirma entregas o no entregas.

## Inicio del dia

1. Encender la PC o servidor interno.
2. Abrir Docker Desktop o verificar Docker Engine.
3. Desde la raiz del repo, levantar backend y base:

```bash
docker compose up -d
```

4. Verificar contenedores:

```bash
docker compose ps
```

5. Verificar health:

```bash
curl http://localhost:8000/api/v1/health
```

La respuesta esperada es:

```json
{"status":"ok","database":"ok"}
```

6. Levantar el panel admin:

```bash
cd apps/admin
npm run dev
```

7. Abrir:

```text
http://localhost:3000/login
```

8. Iniciar sesion.
9. Revisar el dashboard.

## Revisión inicial del dashboard

Al iniciar el dia, revisar:

- pedidos pendientes;
- pedidos asignados;
- pedidos en camino;
- ultimos pedidos;
- alertas operativas;
- productos activos;
- comportamiento de ventas del dia y del mes.

Si el dashboard muestra datos inesperados, revisar `docs/INCIDENT_RUNBOOK.md`.

## Registrar productos

Registrar productos antes de crear pedidos.

Reglas:

- usar nombres claros;
- definir precio correcto;
- mantener unidad consistente;
- marcar productos inactivos si ya no se venden;
- no inventar productos durante la toma de pedidos;
- no borrar productos sin revisar impacto operativo.

Ejemplo ficticio:

```text
Producto Ejemplo A
Unidad: unidad
Precio: 1.00
```

## Registrar clientes

Antes de crear un cliente:

1. Buscar por telefono.
2. Buscar por nombre.
3. Buscar por alias si aplica.
4. Revisar posibles duplicados.

Crear cliente solo si no existe.

Reglas:

- usar nombre claro;
- registrar telefono principal;
- agregar alias comunes;
- agregar direccion completa;
- agregar referencia si ayuda a despacho;
- no guardar datos incompletos si impiden entregar.

Ejemplo ficticio:

```text
Cliente Ejemplo
Telefono: +593999000000
Alias: Referencia Ejemplo
Direccion: Calle Ficticia 123
Referencia: Porton ficticio
```

## Crear pedidos

Crear pedido solo cuando el cliente ya confirmo.

Antes de crear:

- cliente correcto;
- telefono correcto;
- direccion correcta;
- producto activo;
- cantidad correcta;
- precio correcto desde producto registrado.

El pedido inicia en estado `pendiente`.

## Actualizar estados

Usar estados de forma consistente:

- `pendiente`: pedido creado y aun no tomado por despacho.
- `asignado`: pedido tomado por despacho o repartidor.
- `en_camino`: pedido salio a entrega.
- `entregado`: cliente recibio el pedido.
- `no_entregado`: no se pudo entregar.
- `cancelado`: pedido cancelado por error operativo o solicitud del cliente.

No marcar como `entregado` sin confirmacion real de entrega.

## Revisar pedidos recientes

Durante el dia, revisar:

- pedidos duplicados;
- pedidos pendientes antiguos;
- pedidos sin cambio de estado;
- pedidos cancelados;
- pedidos no entregados.

Si aparece un duplicado, no borrar datos sin revisar. Ver
`docs/ORDER_OPERATIONS.md`.

## Backup diario

Al final del dia, generar backup siguiendo `docs/BACKUP_RESTORE.md`.

Reglas:

- guardar backup fuera del repo;
- confirmar que el archivo existe;
- no subir backup a GitHub;
- guardar copia en carpeta segura o unidad externa;
- probar restauracion periodicamente.

## Fin del dia

1. Revisar pedidos pendientes.
2. Revisar pedidos en camino.
3. Generar backup.
4. Confirmar que el backup existe.
5. Cerrar el panel con `Ctrl + C` si se esta ejecutando localmente.
6. Apagar backend/base si corresponde:

```bash
docker compose down
```

No usar `docker compose down -v` salvo que se quiera borrar la base local.

## Lo que no esta listo para clientes finales

- WhatsApp real.
- Envio automatico de mensajes.
- Exposicion publica.
- Usuarios por empleado.
- Roles tecnicos.
- Permisos granulares.
- Auditoria avanzada por usuario.
- Reportes operativos avanzados.
- Rutas o repartidores avanzados.
