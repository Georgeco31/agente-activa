# PRD - Agente Activa

## Que es Agente Activa

Agente Activa es un sistema para gestionar clientes, pedidos y reparto de una empresa de venta de agua que atiende principalmente por WhatsApp.

El producto tendra dos capacidades principales:

1. Un nucleo administrativo para clientes, telefonos, alias, direcciones, productos, pedidos, rutas e historial.
2. Un agente de WhatsApp que, en una etapa posterior, usara ese mismo nucleo para atender mensajes, clasificar intenciones y ejecutar acciones de negocio.

En el estado actual del proyecto solo se esta construyendo el backend del nucleo del negocio. El agente conversacional queda fuera del alcance inmediato.

## Problema que resuelve

La empresa recibe pedidos, consultas y reclamos por WhatsApp. Sin un sistema centralizado, aparecen problemas frecuentes:

- Clientes duplicados por usar varios numeros de telefono.
- Dificultad para reconocer clientes por alias, direccion o referencia.
- Pedidos incompletos o mal registrados.
- Falta de historial por cliente.
- Estados de pedido inconsistentes.
- Informacion dispersa entre chats, asesores y repartidores.

Agente Activa busca convertir esa operacion en un flujo ordenado, trazable y preparado para automatizacion futura.

## Usuarios principales

- Administrador: configura productos, rutas, clientes y revisa reportes.
- Asesor humano: atiende clientes, corrige datos y resuelve casos escalados.
- Despacho: revisa pedidos pendientes, asigna rutas y coordina entregas.
- Repartidor: consulta pedidos asignados y actualiza estados.
- Cliente final: hace pedidos, consulta estado, reporta problemas o pide informacion.
- Agente de WhatsApp futuro: consumira servicios internos del backend como herramientas de negocio.

## Objetivo del MVP

Construir una base confiable para operar pedidos de agua y preparar el sistema para un agente de WhatsApp posterior.

El MVP debe permitir:

- Registrar clientes con multiples telefonos.
- Registrar alias o nombres alternativos.
- Registrar varias direcciones por cliente.
- Crear productos.
- Crear pedidos confirmados con detalle de productos.
- Manejar estados de pedido controlados.
- Buscar clientes por telefono, nombre, alias, direccion o referencia.
- Detectar posibles duplicados antes de crear clientes nuevos.
- Registrar historial de acciones relevantes.

## Alcance actual

El alcance actual corresponde a la Etapa 1 del MVP: backend del nucleo del negocio.

Incluye:

- Base tecnica con FastAPI.
- Conexion a PostgreSQL con SQLAlchemy 2.0.
- Docker Compose para API y PostgreSQL.
- Endpoint `/api/v1/health`.
- Documentacion inicial del producto y del modelo de datos.
- Proximo bloque: modelos ORM, Alembic y migracion inicial.

## Fuera de alcance por ahora

Por ahora no se implementara:

- Agente conversacional de WhatsApp.
- Integracion con WhatsApp Cloud API.
- Automatizaciones con Make, Zapier o n8n.
- Panel administrativo completo.
- Reportes avanzados.
- Optimizacion de rutas.
- Gestion avanzada de repartidores.
- Cobros en linea.
- Inventario.
- Facturacion electronica.

## Reglas principales del negocio

- Cada cliente tiene un ID unico.
- Un cliente puede tener varios telefonos.
- Un cliente puede tener varios alias.
- Un cliente puede tener varias direcciones.
- Un pedido pertenece a un cliente.
- Un pedido puede tener uno o varios productos.
- No se deben crear clientes duplicados.
- Los telefonos de Ecuador se guardan en formato E.164.
- Ejemplo: `0999627968` debe guardarse como `+593999627968`.
- El sistema debe guardar campos normalizados para busqueda.
- La normalizacion de texto debe convertir a minusculas, eliminar tildes, quitar espacios extra y limpiar signos innecesarios.
- Antes de crear un cliente nuevo, el sistema debe buscar coincidencias por telefono, nombre, alias, direccion o referencia.
- Si un numero nuevo pertenece a un cliente existente, debe asociarse al mismo cliente.
- Si hay coincidencias ambiguas, el sistema debe evitar creacion automatica y pedir revision.
- Un pedido solo se crea cuando tenga cliente, direccion, producto, cantidad y estado inicial.
- No deben existir pedidos confirmados incompletos.
- Si faltan datos, el caso debe manejarse como solicitud pendiente o formulario incompleto, no como pedido.
- Las reglas importantes deben vivir en servicios del backend, no en la UI.

## Estados del pedido

Estados obligatorios:

- `pendiente`: pedido registrado y en espera de gestion.
- `asignado`: pedido asignado a ruta o repartidor.
- `en_camino`: pedido en reparto.
- `entregado`: pedido entregado al cliente.
- `no_entregado`: pedido no pudo entregarse.
- `cancelado`: pedido cancelado.

Reglas de estado:

- Todo pedido confirmado debe iniciar con un estado valido.
- Los estados deben venir de un catalogo controlado.
- `entregado`, `no_entregado` y `cancelado` son estados finales.
- Todo cambio de estado debe registrarse en el historial de acciones.

## Criterios de exito

El MVP sera exitoso si:

- El equipo puede registrar clientes sin depender de WhatsApp.
- Los telefonos quedan normalizados de forma consistente.
- La busqueda encuentra clientes por telefono, nombre, alias, direccion y referencia.
- El sistema detecta posibles duplicados antes de crear clientes.
- Se pueden asociar telefonos nuevos a clientes existentes.
- Se pueden asociar alias nuevos a clientes existentes.
- Los productos se gestionan desde el backend.
- Los pedidos confirmados siempre tienen los datos minimos requeridos.
- Los estados de pedido son consistentes.
- El historial permite auditar acciones relevantes.
- El futuro agente de WhatsApp puede usar los servicios internos sin duplicar reglas.
