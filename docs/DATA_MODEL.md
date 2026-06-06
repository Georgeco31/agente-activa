# Modelo de Datos - Agente Activa

## Proposito del modelo

El modelo de datos de Agente Activa esta disenado para representar el nucleo operativo de una empresa de venta y reparto de agua.

La prioridad es mantener una identidad unica de cliente aunque existan multiples telefonos, alias y direcciones. Esta decision prepara el sistema para busqueda avanzada, prevencion de duplicados y automatizacion futura mediante un agente de WhatsApp.

## Entidades principales

### Customer

Representa al cliente como entidad unica.

Responsabilidades:

- Mantener el ID unico del cliente.
- Guardar el nombre principal visible.
- Guardar el nombre normalizado para busqueda.
- Agrupar telefonos, alias, direcciones y pedidos.

Campos esperados:

- `id`
- `display_name`
- `normalized_name`
- `customer_type`
- `status`
- `notes`
- `created_at`
- `updated_at`

### CustomerPhone

Representa un telefono asociado a un cliente.

Responsabilidades:

- Guardar telefonos en formato E.164.
- Permitir varios telefonos por cliente.
- Evitar que el mismo telefono pertenezca a dos clientes.
- Identificar telefonos de WhatsApp o telefonos principales.

Campos esperados:

- `id`
- `customer_id`
- `phone_e164`
- `normalized_phone`
- `raw_phone`
- `label`
- `is_primary`
- `is_whatsapp`
- `verified_at`
- `created_at`

Restriccion principal:

- `normalized_phone` debe ser unico globalmente.

### CustomerAlias

Representa nombres alternativos, apodos o referencias comerciales del cliente.

Responsabilidades:

- Permitir busqueda por nombres no oficiales.
- Registrar alias capturados por asesor, sistema o futura automatizacion.
- Evitar alias duplicados dentro del mismo cliente.

Campos esperados:

- `id`
- `customer_id`
- `alias`
- `normalized_alias`
- `source`
- `created_at`

Restriccion recomendada:

- Combinacion unica `customer_id + normalized_alias`.

### CustomerAddress

Representa una direccion de entrega asociada a un cliente.

Responsabilidades:

- Permitir varias direcciones por cliente.
- Guardar direccion exacta y referencia de ubicacion.
- Asociar una direccion a una zona o ruta de reparto cuando aplique.
- Facilitar busqueda por direccion o referencia.

Campos esperados:

- `id`
- `customer_id`
- `delivery_route_id`
- `label`
- `address_text`
- `normalized_address`
- `reference`
- `normalized_reference`
- `city`
- `neighborhood`
- `latitude`
- `longitude`
- `is_primary`
- `notes`
- `created_at`
- `updated_at`

### Product

Representa un producto vendible.

Responsabilidades:

- Mantener catalogo real de productos.
- Guardar precio actual.
- Permitir activar o desactivar productos.
- Dar informacion confiable al futuro agente.

Campos esperados:

- `id`
- `sku`
- `name`
- `normalized_name`
- `description`
- `unit`
- `price`
- `is_active`
- `created_at`
- `updated_at`

Restriccion principal:

- `sku` debe ser unico.

### Order

Representa un pedido confirmado.

Responsabilidades:

- Asociar cliente, direccion, estado y canal de origen.
- Guardar totales del pedido.
- Guardar la ruta de reparto si aplica.
- Evitar pedidos confirmados incompletos.

Campos esperados:

- `id`
- `order_number`
- `customer_id`
- `customer_phone_id`
- `customer_address_id`
- `order_status_id`
- `delivery_route_id`
- `payment_method`
- `estimated_delivery_time`
- `notes`
- `source_channel`
- `subtotal`
- `delivery_fee`
- `total`
- `confirmed_at`
- `created_at`
- `updated_at`

Regla principal:

- Un pedido solo puede crearse si tiene cliente, direccion, al menos un producto, cantidad y estado inicial.

### OrderItem

Representa el detalle de productos dentro de un pedido.

Responsabilidades:

- Permitir varios productos en un pedido.
- Guardar cantidad y precio unitario.
- Guardar snapshot del nombre y precio para proteger historicos.

Campos esperados:

- `id`
- `order_id`
- `product_id`
- `product_name_snapshot`
- `quantity`
- `unit_price`
- `line_total`
- `created_at`

Decision importante:

- `unit_price` y `product_name_snapshot` se guardan en el detalle para que los pedidos antiguos no cambien si el producto cambia de precio o nombre.

### OrderStatus

Representa el catalogo controlado de estados de pedido.

Estados obligatorios:

- `pendiente`
- `asignado`
- `en_camino`
- `entregado`
- `no_entregado`
- `cancelado`

Campos esperados:

- `id`
- `code`
- `name`
- `sort_order`
- `is_final`

Restriccion principal:

- `code` debe ser unico.

### DeliveryRoute

Representa una ruta o zona de reparto.

Se usa el nombre `DeliveryRoute` para evitar confusion con rutas o endpoints de FastAPI.

Responsabilidades:

- Agrupar direcciones y pedidos por zona.
- Permitir asignacion operativa posterior.
- Preparar el sistema para despacho y reparto.

Campos esperados:

- `id`
- `code`
- `name`
- `description`
- `city`
- `is_active`
- `created_at`

Restriccion principal:

- `code` debe ser unico.

### ActionHistory

Representa el historial de acciones relevantes del sistema.

Responsabilidades:

- Auditar creacion y actualizacion de entidades.
- Registrar asociacion de telefonos y alias.
- Registrar cambios de estado de pedido.
- Registrar deteccion de posibles duplicados.
- Preparar trazabilidad para el futuro agente de WhatsApp.

Campos esperados:

- `id`
- `entity_type`
- `entity_id`
- `customer_id`
- `order_id`
- `action_type`
- `description`
- `old_value`
- `new_value`
- `performed_by_type`
- `performed_by_id`
- `created_at`

## Relaciones entre entidades

- `Customer` tiene muchos `CustomerPhone`.
- `Customer` tiene muchos `CustomerAlias`.
- `Customer` tiene muchas `CustomerAddress`.
- `Customer` tiene muchos `Order`.
- `CustomerAddress` puede pertenecer a una `DeliveryRoute`.
- `Order` pertenece a un `Customer`.
- `Order` puede estar asociado al `CustomerPhone` desde donde se hizo el pedido.
- `Order` pertenece a una `CustomerAddress`.
- `Order` pertenece a un `OrderStatus`.
- `Order` puede pertenecer a una `DeliveryRoute`.
- `Order` tiene muchos `OrderItem`.
- `OrderItem` pertenece a un `Product`.
- `ActionHistory` puede estar relacionado con `Customer`, `Order` u otra entidad mediante `entity_type` y `entity_id`.

## Reglas de integridad

- Todo `CustomerPhone` debe pertenecer a un `Customer`.
- Todo `CustomerAlias` debe pertenecer a un `Customer`.
- Todo `CustomerAddress` debe pertenecer a un `Customer`.
- Todo `Order` debe pertenecer a un `Customer`.
- Todo `Order` debe tener una direccion.
- Todo `Order` debe tener un estado valido.
- Todo `OrderItem` debe pertenecer a un `Order`.
- Todo `OrderItem` debe referenciar un `Product`.
- Todo producto vendido en un pedido debe conservar snapshot de nombre y precio.
- Un telefono no puede pertenecer a mas de un cliente.

## Restricciones importantes

- `CustomerPhone.normalized_phone` unico global.
- `Product.sku` unico.
- `OrderStatus.code` unico.
- `DeliveryRoute.code` unico.
- `Order.order_number` unico.
- `CustomerAlias.customer_id + normalized_alias` unico recomendado.
- Los estados de pedido no deben almacenarse como texto libre en `Order`.
- Los pedidos confirmados no deben crearse sin items.
- Las reglas de negocio deben vivir en servicios backend, no en endpoints ni UI.

## Campos normalizados para busqueda

Campos normalizados esperados:

- `Customer.normalized_name`
- `CustomerPhone.normalized_phone`
- `CustomerAlias.normalized_alias`
- `CustomerAddress.normalized_address`
- `CustomerAddress.normalized_reference`
- `Product.normalized_name`

Reglas de normalizacion de texto:

- Convertir a minusculas.
- Eliminar tildes.
- Quitar espacios extra.
- Limpiar signos innecesarios.
- Mantener una forma consistente para comparacion y busqueda.

Regla de normalizacion de telefono:

- Los telefonos de Ecuador deben guardarse en formato E.164.
- Si el numero llega como `0999627968`, debe guardarse como `+593999627968`.
- Si el numero llega como `593999627968`, debe guardarse como `+593999627968`.
- Si el numero llega como `+593999627968`, se conserva normalizado.

## Decisiones de diseno

- El cliente no se identifica por telefono. El cliente tiene ID propio y puede tener multiples telefonos.
- Los alias estan separados del cliente para permitir busqueda flexible y multiples nombres.
- Las direcciones estan separadas del cliente porque un cliente puede pedir para varias ubicaciones.
- Los productos estan separados de los pedidos para mantener catalogo y reportes.
- Los pedidos usan `OrderItem` para soportar multiples productos.
- Los precios historicos se guardan en `OrderItem`.
- Los estados de pedido viven en un catalogo controlado.
- Las rutas de reparto se llaman `DeliveryRoute` para evitar confusion con rutas HTTP.
- El historial de acciones es una tabla transversal para auditoria.
- El futuro agente de WhatsApp debera usar servicios internos del backend y no escribir directamente en la base de datos.
