# Agente conversacional

Esta guia documenta los Bloques 9A, 9B, 9C y 9D del agente interno. El objetivo
es preparar el futuro agente de WhatsApp sin enviar mensajes reales y con
creacion de pedidos reales solo bajo confirmacion explicita y controles
backend.

## Que hace 9A

- Recibe un mensaje simulado con telefono y texto.
- Normaliza telefono y texto usando reglas existentes.
- Busca el cliente por telefono normalizado.
- Detecta una intencion operativa basica.
- Extrae cantidad, pista de producto y pista de direccion cuando aparecen.
- Consulta productos activos para resolver una pista de producto.
- Consulta pedidos del cliente solo para responder estado de pedido.
- Devuelve una respuesta simulada para el cliente.

`POST /api/v1/agent/simulate-message` no escribe en la base de datos. Solo
interpreta, consulta y responde.

## Que hace 9B

- Agrega persistencia conversacional minima.
- Crea o reutiliza una sesion abierta por telefono normalizado.
- Guarda cada mensaje inbound del cliente.
- Guarda cada respuesta outbound simulada del agente.
- Acumula `extracted_data` entre mensajes de forma no destructiva.
- Recalcula `missing_fields` usando el estado acumulado.
- Asocia la sesion a un cliente existente si el telefono ya esta registrado.
- Permite consultar una sesion y sus mensajes.
- Permite cerrar una sesion manualmente.

`ready_for_confirmation` significa que el flujo ya tiene datos suficientes para
pedir confirmacion. No significa que exista un pedido real.

## Que hace 9C

- Agrega un webhook entrante compatible con Meta/WhatsApp Cloud API en modo
  preparacion.
- Permite verificacion `GET` con `hub.mode`, `hub.verify_token` y
  `hub.challenge`.
- Recibe eventos `POST` solo si el webhook esta habilitado.
- Valida `X-Hub-Signature-256` con HMAC-SHA256 usando `WHATSAPP_APP_SECRET`.
- Parsea mensajes entrantes de texto.
- Envia mensajes de texto validos al servicio conversacional persistente de 9B.
- Guarda conversaciones y mensajes en la base de datos.
- Registra tipos no soportados como metadata minima sin procesarlos como pedido.

9C no llama APIs externas de Meta y no envia respuestas reales.

## Que hace 9D

- Genera `confirmation_summary` cuando una conversacion llega a
  `ready_for_confirmation`.
- Expone `POST /api/v1/agent/conversations/{session_id}/confirm-order`.
- Crea un pedido real solo si hay datos completos y confirmacion explicita.
- Reutiliza `app.services.orders.create_order()` para conservar reglas de
  pedidos.
- Crea pedidos en estado inicial `pendiente`.
- Cierra la conversacion despues de crear el pedido.
- Guarda `order_id`, `order_number` y `confirmed_at` en `extracted_data`.
- Guarda un mensaje outbound interno con el numero de pedido.
- Registra auditoria adicional `order_created_by_agent`.
- Bloquea duplicados recientes similares.

## Que no hace todavia

- No conecta WhatsApp real.
- No envia mensajes reales.
- No usa OpenAI ni APIs externas.
- No crea pedidos desde el webhook WhatsApp.
- No crea pedidos desde `simulate-conversation-message`.
- No crea pedidos sin resumen pendiente y confirmacion explicita.
- No cancela pedidos.
- No modifica pedidos.
- No modifica clientes.
- No modifica productos.
- No implementa job automatico de expiracion.
- No implementa una pantalla `/agent` en el panel.
- No debe exponerse publicamente sin HTTPS, rate limiting, monitoreo y controles
  adicionales.

## Intenciones soportadas

- `greeting`: saludo simple.
- `create_order`: mensaje que parece pedido.
- `ask_price`: consulta de precio.
- `ask_order_status`: consulta de estado del pedido.
- `cancel_order`: solicitud de cancelacion.
- `provide_address`: mensaje que aporta referencia de direccion.
- `unknown`: mensaje no reconocido.

## Estados conversacionales

- `active`: sesion abierta sin flujo de pedido listo.
- `waiting_for_customer`: falta informacion para continuar.
- `ready_for_confirmation`: los datos acumulados permiten pedir confirmacion
  explicita, pero no se crea un pedido real automaticamente.
- `closed`: sesion cerrada manualmente.
- `expired`: estado reservado para expiracion futura; no hay job automatico.

Una sesion cerrada no se reutiliza. Si llega otro mensaje del mismo telefono,
se crea una nueva sesion abierta.

## Tablas nuevas

### conversation_sessions

- `id`: UUID primario.
- `phone`: telefono recibido.
- `normalized_phone`: telefono normalizado para busqueda y reutilizacion.
- `customer_id`: FK opcional a `customers.id` con `ON DELETE SET NULL`.
- `status`: estado conversacional.
- `current_intent`: intencion activa.
- `extracted_data`: JSONB con datos acumulados.
- `missing_fields`: JSONB con campos faltantes recalculados.
- `last_message_at`: fecha del ultimo mensaje.
- `created_at`: fecha de creacion.
- `updated_at`: fecha de ultima actualizacion.

Indices principales: `normalized_phone`, `status`, `customer_id` y
`normalized_phone + status`.

### conversation_messages

- `id`: UUID primario.
- `session_id`: FK a `conversation_sessions.id` con `ON DELETE CASCADE`.
- `direction`: `inbound`, `outbound` o `system`.
- `phone`: telefono del mensaje.
- `message`: texto del mensaje.
- `intent`: intencion detectada, si aplica.
- `confidence`: confianza del analisis, si aplica.
- `message_metadata`: JSONB opcional con datos de analisis.
- `created_at`: fecha de creacion.

Se usa `message_metadata` para evitar el atributo reservado `metadata` de
SQLAlchemy.

Migracion:

```bash
docker compose exec api alembic upgrade head
```

## Endpoints internos

Todos los endpoints del agente requieren:

```http
X-Agent-Simulation-Token: <AGENT_SIMULATION_TOKEN>
```

### Simulacion stateless

`POST /api/v1/agent/simulate-message`

Este endpoint pertenece al Bloque 9A y se mantiene sin persistencia.

Request:

```json
{
  "phone": "+593999999999",
  "message": "Hola, quiero un bidon de 20 litros"
}
```

Response:

```json
{
  "intent": "create_order",
  "confidence": 0.85,
  "customer": {
    "found": true,
    "id": "11111111-1111-4111-8111-111111111111",
    "display_name": "Cliente Ejemplo"
  },
  "extracted": {
    "quantity": 1,
    "product_hint": "bidon 20 litros",
    "product_id": "22222222-2222-4222-8222-222222222222",
    "product_name": "Bidon 20 Litros",
    "product_price": "3.50",
    "address_hint": null
  },
  "missing_fields": ["address_id"],
  "reply": "Claro. Deseas que lo enviemos a tu direccion registrada?"
}
```

### Simulacion con persistencia

`POST /api/v1/agent/simulate-conversation-message`

Request:

```json
{
  "phone": "+593999999999",
  "message": "Hola, quiero un bidon de 20 litros"
}
```

Response:

```json
{
  "session": {
    "id": "33333333-3333-4333-8333-333333333333",
    "status": "waiting_for_customer",
    "current_intent": "create_order"
  },
  "analysis": {
    "intent": "create_order",
    "confidence": 0.85,
    "customer": {
      "found": true,
      "id": "11111111-1111-4111-8111-111111111111",
      "display_name": "Cliente Ejemplo"
    },
    "extracted": {
      "quantity": 1,
      "product_hint": "bidon 20 litros",
      "product_id": "22222222-2222-4222-8222-222222222222",
      "product_name": "Bidon 20 Litros",
      "product_price": "3.50",
      "address_hint": null
    },
    "missing_fields": ["address_id"],
    "reply": "Claro. Deseas que lo enviemos a tu direccion registrada?"
  }
}
```

Ejemplo:

```bash
curl -X POST http://localhost:8000/api/v1/agent/simulate-conversation-message \
  -H "Content-Type: application/json" \
  -H "X-Agent-Simulation-Token: $AGENT_SIMULATION_TOKEN" \
  -d '{"phone":"+593999999999","message":"Hola, quiero un bidon de 20 litros"}'
```

### Consultar una conversacion

`GET /api/v1/agent/conversations/{session_id}`

Devuelve la sesion, los datos acumulados y los mensajes guardados.

### Cerrar una conversacion

`POST /api/v1/agent/conversations/{session_id}/close`

Marca la sesion como `closed`. No elimina mensajes y no crea pedidos.

### Confirmar y crear pedido

`POST /api/v1/agent/conversations/{session_id}/confirm-order`

Header obligatorio:

```http
X-Agent-Simulation-Token: <AGENT_SIMULATION_TOKEN>
```

Body:

```json
{
  "message": "confirmo"
}
```

El endpoint crea un pedido real solo si se cumple todo:

- la sesion existe y no esta cerrada;
- la sesion esta en `ready_for_confirmation`;
- existe `confirmation_summary` pendiente en `extracted_data`;
- el cliente existe;
- el telefono normalizado de la sesion pertenece al cliente;
- el producto existe, esta activo y su precio es valido;
- la cantidad es un entero mayor que cero y maximo 50;
- existe `address_id`;
- la direccion pertenece al cliente;
- el mensaje contiene confirmacion explicita;
- no existe un pedido reciente similar.

Confirmaciones aceptadas, despues de normalizar texto:

- `si`
- `confirmo`
- `confirmado`
- `correcto`
- `dale`
- `ok`
- `esta bien`
- `de acuerdo`
- `procede`

Mensajes como `tal vez`, `despues`, `espera`, `creo que si`, `no se` o `no`
no crean pedidos.

Respuesta de ejemplo abreviada:

```json
{
  "session": {
    "status": "closed",
    "extracted_data": {
      "order_id": "44444444-4444-4444-8444-444444444444",
      "order_number": "ORD-20260630-ABC123",
      "confirmed_at": "2026-06-30T03:00:00+00:00"
    }
  },
  "order": {
    "id": "44444444-4444-4444-8444-444444444444",
    "order_number": "ORD-20260630-ABC123",
    "source_channel": "agent_conversation"
  },
  "reply": "Pedido ORD-20260630-ABC123 creado correctamente. Estado inicial: pendiente."
}
```

La respuesta real incluye el contrato completo de sesion y pedido usado por la
API.

## Condiciones para confirmation_summary

El resumen pendiente se guarda en `conversation_sessions.extracted_data` cuando
la conversacion tiene datos suficientes. Contiene:

- `customer_id`
- `product_id`
- `product_name`
- `quantity`
- `address_id`
- `address_text`
- `unit_price`
- `total`
- `generated_at`
- `status: pending`

Si el cliente tiene una sola direccion y el mensaje contiene una pista como
`de siempre`, el backend puede resolver esa direccion y generar el resumen. Si
el cliente tiene varias direcciones, el agente debe pedir aclaracion.

## Duplicados recientes

Antes de crear un pedido, el backend busca pedidos similares de los ultimos 10
minutos con mismo cliente, direccion, producto, cantidad y estado `pendiente`,
`asignado` o `en_camino`.

Si existe uno, responde `AGENT_ORDER_DUPLICATE_RECENT` y no crea otro. La
confirmacion especial para duplicados queda pendiente para un bloque futuro.

## Webhook WhatsApp/Meta en preparacion

Variables necesarias:

```text
WHATSAPP_WEBHOOK_ENABLED=false
WHATSAPP_WEBHOOK_VERIFY_TOKEN=replace-with-whatsapp-webhook-verify-token
WHATSAPP_APP_SECRET=replace-with-whatsapp-app-secret
```

`WHATSAPP_WEBHOOK_ENABLED` debe estar activo para aceptar verificacion o eventos.
Los otros valores deben configurarse localmente con secretos reales fuera del
repositorio. `apps/api/.env.example` contiene solo placeholders.

### Verificacion GET

`GET /api/v1/whatsapp/webhook`

Parametros esperados:

- `hub.mode=subscribe`
- `hub.verify_token=<WHATSAPP_WEBHOOK_VERIFY_TOKEN>`
- `hub.challenge=<valor-de-meta>`

Si el webhook esta habilitado y el token coincide, la API devuelve
`hub.challenge` como `text/plain`. Si el webhook esta deshabilitado, el modo no
es `subscribe` o el token no coincide, responde `403`.

Ejemplo local:

```bash
curl "http://localhost:8000/api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=$WHATSAPP_WEBHOOK_VERIFY_TOKEN&hub.challenge=test-challenge"
```

### Recepcion POST

`POST /api/v1/whatsapp/webhook`

El endpoint lee el body crudo, valida `X-Hub-Signature-256` con
`WHATSAPP_APP_SECRET` y solo despues parsea JSON. El formato de firma esperado
es:

```http
X-Hub-Signature-256: sha256=<hmac-hex>
```

Si la firma falta o no coincide, responde `401`. Si el evento se procesa,
responde `200` con un resumen interno:

```json
{
  "status": "ok",
  "processed_messages": 1,
  "unsupported_messages": 0,
  "ignored_messages": 0,
  "session_ids": ["33333333-3333-4333-8333-333333333333"],
  "outbound_sent": false
}
```

`outbound_sent: false` es intencional: el webhook no envia mensajes reales a
WhatsApp en 9C.

En 9D el webhook sigue sin crear pedidos reales automaticamente. Solo guarda y
procesa conversaciones; la creacion real queda limitada al endpoint interno
protegido `confirm-order`.

### Payload soportado

El parseo defensivo lee:

- `entry[].changes[].value.messages[]`
- `from`
- `id`
- `timestamp`
- `type`
- `text.body` cuando `type == "text"`
- metadata minima: `messaging_product`, `phone_number_id` y
  `display_phone_number`

Solo los mensajes de texto se envian al motor conversacional persistente. Los
tipos `image`, `audio`, `sticker`, `location` u otros no rompen el endpoint:
se registran como `unsupported_message_type`, responden `200` y no se procesan
como pedido.

### Probar firma HMAC localmente

Ejemplo con valores ficticios locales:

```bash
BODY='{"entry":[{"changes":[{"value":{"messaging_product":"whatsapp","metadata":{"display_phone_number":"593999000000","phone_number_id":"phone-number-id"},"messages":[{"from":"593999999999","id":"wamid.local-test","timestamp":"1710000000","type":"text","text":{"body":"Hola, quiero un bidon de 20 litros"}}]}}]}]}'
SIGNATURE=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$WHATSAPP_APP_SECRET" -binary | xxd -p -c 256)
curl -X POST http://localhost:8000/api/v1/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$BODY"
```

Para probar con Meta real se necesita una URL publica HTTPS. No se debe exponer
el backend directamente a internet sin controles adicionales de seguridad,
observabilidad y rate limiting.

## Acumulacion de extracted_data

La acumulacion es no destructiva:

- un valor nuevo no nulo actualiza el dato acumulado;
- un valor nuevo `null` no borra un dato util existente;
- `missing_fields` se recalcula usando los datos acumulados y no solo el ultimo
  mensaje;
- producto, cantidad y direccion pueden completarse en mensajes separados.

Ejemplo de flujo:

1. Cliente: `Quiero un bidon de 20 litros`.
2. El sistema guarda producto/cantidad y queda `waiting_for_customer` por
   direccion.
3. Cliente: `A la direccion de siempre`.
4. El sistema conserva producto/cantidad, agrega la pista de direccion y pasa a
   `ready_for_confirmation` si no faltan otros datos.

## Seguridad

Los endpoints requieren la variable `AGENT_SIMULATION_TOKEN` y el header
`X-Agent-Simulation-Token`.

Reglas:

- si `AGENT_SIMULATION_TOKEN` falta o contiene un placeholder, el endpoint falla
  cerrado con `AGENT_SIMULATION_NOT_CONFIGURED`;
- si el header falta o no coincide, responde `401` con
  `AGENT_SIMULATION_UNAUTHORIZED`;
- los errores no imprimen el token configurado ni el token recibido;
- `apps/api/.env.example` contiene solo un placeholder;
- no se debe subir `apps/api/.env` ni tokens reales.

El webhook WhatsApp usa `WHATSAPP_WEBHOOK_VERIFY_TOKEN` para verificacion GET y
`WHATSAPP_APP_SECRET` para validar firmas POST. Los errores no imprimen tokens,
secrets ni firmas recibidas.

## Heuristicas actuales

La extraccion es simple y basada en reglas:

- cantidad: digitos y palabras comunes como `un`, `una`, `dos`, `tres`;
- producto: coincidencias como `bidon`, `botellon`, `20 litros`, `20l`,
  `agua`, `botella`;
- direccion: frases como `casa`, `direccion`, `de siempre`, `domicilio`;
- cliente: busqueda por telefono normalizado de Ecuador;
- estado: se consultan solo pedidos asociados al cliente encontrado por
  telefono.

Si falta informacion o hay ambiguedad, el response incluye `missing_fields` y
una respuesta que pide aclaracion.

## Limitaciones

- Las reglas no entienden lenguaje natural complejo.
- No hay auditoria avanzada.
- No hay expiracion automatica de sesiones.
- No hay envio saliente a WhatsApp.
- No hay confirmacion especial para duplicados recientes.
- Los sinonimos reales del negocio pueden requerir ajustes.
- El token de simulacion no reemplaza autenticacion API completa.

## Proximos pasos

- Confirmacion especial para duplicados recientes.
- Simulador visual en el panel admin.
- Envio WhatsApp saliente despues de controles adicionales.
- Rate limiting y auditoria persistente.
- Autenticacion API propia antes de exponer endpoints publicos.
