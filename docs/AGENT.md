# Agente conversacional

Esta guia documenta los Bloques 9A y 9B del agente interno. El objetivo es
preparar el futuro agente de WhatsApp sin conectar WhatsApp real, sin exponer
webhooks publicos y sin crear pedidos reales automaticamente.

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
pedir confirmacion en un bloque futuro. No significa que exista un pedido real.

## Que no hace todavia

- No conecta WhatsApp real.
- No crea webhook publico.
- No envia mensajes reales.
- No usa OpenAI ni APIs externas.
- No crea pedidos.
- No cancela pedidos.
- No modifica pedidos.
- No modifica clientes.
- No modifica productos.
- No confirma pedidos.
- No implementa job automatico de expiracion.
- No implementa una pantalla `/agent` en el panel.

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
  futura, pero no se crea un pedido real.
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
- No hay confirmacion de pedido.
- No hay auditoria avanzada.
- No hay expiracion automatica de sesiones.
- Los sinonimos reales del negocio pueden requerir ajustes.
- El token de simulacion no reemplaza autenticacion API completa.

## Proximos pasos

- Flujo de confirmacion antes de crear pedidos reales.
- Simulador visual en el panel admin.
- Webhook WhatsApp seguro con verificacion de firma.
- Rate limiting y auditoria persistente.
- Autenticacion API propia antes de exponer endpoints publicos.
