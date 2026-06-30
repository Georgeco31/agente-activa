# Checklist diario de operacion

Usar este checklist cada dia de operacion interna.

## Inicio del dia

- [ ] PC o servidor interno encendido.
- [ ] Docker Desktop o Docker Engine funcionando.
- [ ] Backend y base levantados.
- [ ] `docker compose ps` muestra servicios esperados.
- [ ] Health OK:

```bash
curl http://localhost:8000/api/v1/health
```

- [ ] Admin abre en `http://localhost:3000/login`.
- [ ] Login funciona.
- [ ] Dashboard revisado.
- [ ] Pedidos pendientes revisados.
- [ ] Productos activos revisados si hubo cambios recientes.

## Durante el dia

- [ ] Pedidos registrados solo con confirmacion del cliente.
- [ ] Cliente verificado antes de crear pedido.
- [ ] Telefono verificado.
- [ ] Direccion verificada.
- [ ] Producto activo verificado.
- [ ] Duplicados revisados antes de crear cliente o pedido.
- [ ] Estados de pedido actualizados.
- [ ] No se borraron datos sin revisar.
- [ ] No se improvisaron productos, precios ni clientes.
- [ ] No se subieron datos reales a Git.

## Fin del dia

- [ ] Pedidos pendientes revisados.
- [ ] Pedidos `en_camino` revisados.
- [ ] Pedidos `no_entregado` revisados.
- [ ] Backup generado siguiendo `docs/BACKUP_RESTORE.md`.
- [ ] Backup verificado con `ls -lh backups/` o ubicacion segura equivalente.
- [ ] Backup guardado fuera del repo.
- [ ] Si aplica, copia guardada en unidad externa o carpeta segura.
- [ ] Panel admin detenido con `Ctrl + C` si corre localmente.
- [ ] Backend/base apagados si corresponde:

```bash
docker compose down
```

- [ ] No se uso `docker compose down -v` salvo decision deliberada.

## Si algo falla

- [ ] Revisar `docs/INCIDENT_RUNBOOK.md`.
- [ ] No borrar volumenes sin backup.
- [ ] No restaurar backup sin confirmar archivo correcto.
- [ ] No compartir secretos en capturas o chats.
