# Operacion de pedidos

Esta guia define reglas manuales para crear y actualizar pedidos en el MVP
local. No cambia reglas de negocio en codigo.

## Cuando crear un pedido

Crear un pedido cuando:

- el cliente ya confirmo que desea comprar;
- el cliente existe o fue creado correctamente;
- el telefono esta asociado al cliente correcto;
- la direccion de entrega esta registrada;
- el producto existe y esta activo;
- la cantidad esta clara;
- el precio esta registrado en el producto.

No crear pedidos con datos incompletos.

## Datos minimos

Todo pedido necesita:

- cliente;
- direccion;
- producto activo;
- cantidad;
- estado inicial;
- precio desde producto registrado.

No inventar clientes, productos ni precios durante la operacion.

## Verificacion antes de guardar

Antes de confirmar:

1. Verificar cliente.
2. Verificar telefono principal o telefono usado para pedir.
3. Verificar direccion.
4. Verificar producto.
5. Verificar cantidad.
6. Revisar pedidos recientes para evitar duplicados.

## Estados de pedido

### pendiente

Estado inicial de un pedido nuevo. Usar cuando el pedido fue creado pero aun no
esta tomado por despacho.

### asignado

Usar cuando el pedido ya fue tomado por despacho o asignado a una persona de
entrega.

### en_camino

Usar cuando el pedido salio a entrega.

### entregado

Usar solo cuando la entrega fue confirmada.

### no_entregado

Usar si no se pudo entregar. Ejemplos:

- cliente no estaba;
- direccion incorrecta;
- cliente pidio reprogramar;
- no hubo acceso al lugar.

Agregar nota operativa fuera del repo si el equipo necesita detalle adicional.

### cancelado

Usar si:

- el cliente cancela;
- el pedido fue creado por error;
- el pedido era duplicado y no debe entregarse;
- el producto ya no esta disponible.

No cancelar pedidos sin revisar impacto operativo.

## Pedidos duplicados

Si se detecta un duplicado:

1. Revisar cliente.
2. Revisar direccion.
3. Revisar producto y cantidad.
4. Revisar hora de creacion.
5. Confirmar con el equipo si era un pedido adicional real.

Si fue error, cancelar el duplicado. No borrar datos directamente.

## Cambio de direccion

Si el cliente cambia direccion:

1. Agregar nueva direccion al cliente.
2. Mantener la direccion anterior si sigue siendo util.
3. Crear el pedido con la direccion correcta.
4. Si el pedido ya existia, revisar si debe cancelarse y crearse de nuevo o si
   basta con actualizar segun el flujo disponible.

No escribir una direccion nueva solo en notas si el pedido depende de ella.

## Producto no registrado

Si el cliente pide algo no registrado:

1. No inventar producto.
2. Confirmar si el negocio realmente vende ese producto.
3. Crear el producto con nombre, unidad y precio correcto.
4. Crear el pedido despues.

Si el producto no se vende, informar al cliente fuera del sistema.

## Agente conversacional

El agente solo debe crear pedidos mediante confirmacion explicita y controles
existentes. El webhook WhatsApp no crea pedidos automaticamente.

Para operacion interna, revisar pedidos recientes despues de pruebas del agente
para confirmar que no se haya creado un pedido no deseado.

## Reglas de seguridad operativa

- No usar datos ficticios en operacion real.
- No usar datos reales en documentacion versionada.
- No compartir capturas con datos de clientes en canales publicos.
- No exponer el panel fuera de la red interna.
