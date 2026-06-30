# Carga inicial de datos

Esta guia explica como preparar datos reales antes de operar internamente. No
incluye datos reales y no debe usarse para versionar clientes, telefonos,
direcciones ni productos reales.

## Orden recomendado

1. Cargar productos activos.
2. Revisar precios.
3. Cargar clientes frecuentes.
4. Agregar telefonos principales.
5. Agregar alias comunes.
6. Agregar direcciones completas.
7. Agregar referencias utiles de entrega.
8. Revisar duplicados.

## Productos

Cargar primero productos que se venden actualmente.

Reglas:

- usar nombres claros;
- registrar precio correcto;
- revisar unidad;
- mantener productos activos solo si se venden;
- marcar productos inactivos en vez de borrarlos;
- no crear pedidos con productos improvisados.

Ejemplo ficticio:

```text
Nombre: Producto Ejemplo A
SKU: EJEMPLO-A
Unidad: unidad
Precio: 1.00
Estado: activo
```

## Clientes

Antes de crear un cliente:

- buscar por telefono;
- buscar por nombre;
- buscar por alias;
- revisar resultados similares.

Reglas:

- no duplicar clientes;
- usar nombres claros;
- no usar abreviaturas ambiguas;
- registrar notas solo si ayudan a la operacion;
- no agregar datos reales a GitHub.

Ejemplo ficticio:

```text
Nombre: Cliente Ejemplo
Tipo: persona
Notas: Ejemplo ficticio para documentacion
```

## Telefonos

Registrar telefono principal en formato Ecuador.

Reglas:

- revisar telefono antes de crear cliente;
- asociar telefono nuevo a cliente existente si ya esta registrado;
- marcar el telefono principal cuando corresponda;
- identificar si es WhatsApp si ayuda a la operacion;
- no inventar telefonos.

Ejemplo ficticio:

```text
+593999000000
```

## Alias

Los alias ayudan a buscar clientes por nombres comunes o referencias internas.

Reglas:

- usar alias que el equipo realmente reconozca;
- evitar alias ofensivos o ambiguos;
- no crear alias duplicados innecesarios;
- asociar alias al cliente correcto.

Ejemplo ficticio:

```text
Alias: Tienda Ejemplo
```

## Direcciones

Registrar direcciones completas y referencias utiles.

Reglas:

- direccion completa;
- referencia cuando ayude al repartidor;
- ciudad o sector si aplica;
- no dejar direccion solo como "casa" o "de siempre";
- si un cliente tiene varias direcciones, mantenerlas separadas y claras.

Ejemplo ficticio:

```text
Direccion: Calle Ficticia 123
Referencia: Porton ficticio
Etiqueta: casa
```

## Revision de duplicados

Antes y despues de la carga inicial:

- buscar cliente por telefono;
- buscar por nombre;
- revisar aliases;
- revisar direcciones similares;
- unir operativamente la informacion antes de crear nuevos registros.

Si hay duda, no crear duplicado. Revisar con la persona responsable.

## Datos que no deben entrar al repo

- clientes reales;
- telefonos reales;
- direcciones reales;
- productos reales con precios internos si no son publicos;
- backups;
- capturas con datos de clientes;
- archivos `.env` reales.

Los ejemplos en documentacion deben ser ficticios.
