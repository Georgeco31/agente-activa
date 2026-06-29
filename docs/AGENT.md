# Agente conversacional

Esta guia documenta el Bloque 9A: nucleo conversacional backend y simulador
interno. El objetivo es preparar el futuro agente de WhatsApp sin conectar
WhatsApp real ni exponer webhooks publicos.

## Que hace 9A

- Recibe un mensaje simulado con telefono y texto.
- Normaliza telefono y texto usando reglas existentes.
- Busca el cliente por telefono normalizado.
- Detecta una intencion operativa basica.
- Extrae cantidad, pista de producto y pista de direccion cuando aparecen.
- Consulta productos activos para resolver una pista de producto.
- Consulta pedidos del cliente solo para responder estado de pedido.
- Devuelve una respuesta simulada para el cliente.

El endpoint no escribe en la base de datos. Solo interpreta, consulta y
responde.

## Que no hace todavia

- No conecta WhatsApp real.
- No crea webhook publico.
- No envia mensajes reales.
- No usa OpenAI ni APIs externas.
- No crea pedidos.
- No cancela pedidos.
- No modifica clientes.
- No modifica productos.
- No guarda estado conversacional.
- No crea tablas ni migraciones.
- No implementa una pantalla `/agent` en el panel.

## Intenciones soportadas

- `greeting`: saludo simple.
- `create_order`: mensaje que parece pedido.
- `ask_price`: consulta de precio.
- `ask_order_status`: consulta de estado del pedido.
- `cancel_order`: solicitud de cancelacion.
- `provide_address`: mensaje que aporta referencia de direccion.
- `unknown`: mensaje no reconocido.

## Endpoint interno

`POST /api/v1/agent/simulate-message`

Header obligatorio:

```http
X-Agent-Simulation-Token: <AGENT_SIMULATION_TOKEN>
```

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

## Seguridad

El endpoint requiere la variable `AGENT_SIMULATION_TOKEN` y el header
`X-Agent-Simulation-Token`.

Reglas:

- si `AGENT_SIMULATION_TOKEN` falta o contiene un placeholder, el endpoint falla
  cerrado con `AGENT_SIMULATION_NOT_CONFIGURED`;
- si el header falta o no coincide, responde `401` con
  `AGENT_SIMULATION_UNAUTHORIZED`;
- los errores no imprimen el token configurado ni el token recibido;
- `apps/api/.env.example` contiene solo un placeholder;
- no se debe subir `apps/api/.env` ni tokens reales.

## Ejemplo curl

```bash
curl -X POST http://localhost:8000/api/v1/agent/simulate-message \
  -H "Content-Type: application/json" \
  -H "X-Agent-Simulation-Token: $AGENT_SIMULATION_TOKEN" \
  -d '{"phone":"+593999999999","message":"Hola, quiero un bidon de 20 litros"}'
```

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
- No hay memoria entre mensajes.
- No hay confirmacion de pedido.
- No hay auditoria conversacional.
- Los sinonimos reales del negocio pueden requerir ajustes.
- El token de simulacion no reemplaza autenticacion API completa.

## Proximos pasos

- Persistencia conversacional.
- Simulador visual en el panel admin.
- Flujo de confirmacion antes de crear pedidos reales.
- Webhook WhatsApp seguro con verificacion de firma.
- Rate limiting y auditoria persistente.
- Autenticacion API propia antes de exponer endpoints publicos.
