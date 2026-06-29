from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.order import Order
from app.models.product import Product
from app.schemas.agent import (
    AgentCustomerMatch,
    AgentExtraction,
    AgentIntent,
    AgentSimulationResponse,
)
from app.services.customer_search import search_customer_by_phone
from app.services.normalization import normalize_ecuador_phone, normalize_text
from app.services.orders import list_orders
from app.services.products import list_products

NUMBER_WORDS = {
    "un": 1,
    "una": 1,
    "uno": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
}

GREETING_TERMS = {"hola", "buenas", "buenos dias", "buenas tardes", "buenas noches"}
ORDER_TERMS = {
    "quiero",
    "necesito",
    "mandame",
    "enviame",
    "enviar",
    "pedido",
    "pedir",
    "comprar",
}
PRICE_TERMS = {"precio", "cuanto cuesta", "cuanto vale", "valor", "cuanto es"}
STATUS_TERMS = {"donde esta", "estado", "seguimiento", "mi pedido", "como va"}
CANCEL_TERMS = {"cancelar", "cancela", "anular", "anula", "cancelacion"}
ADDRESS_TERMS = {"casa", "direccion", "de siempre", "domicilio", "entrega"}
PRODUCT_TERMS = {
    "bidon",
    "bidones",
    "botellon",
    "botellones",
    "20 litros",
    "20l",
    "20 l",
    "agua",
    "botella",
    "botellas",
}


def _contains_any(normalized_message: str, terms: set[str]) -> bool:
    return any(term in normalized_message for term in terms)


def _extract_quantity(normalized_message: str) -> int | None:
    tokens = normalized_message.split()
    for index, token in enumerate(tokens):
        if token.isdigit():
            next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
            if next_token in {"litro", "litros", "l"}:
                continue
            quantity = int(token)
            return quantity if quantity > 0 else None

        quantity = NUMBER_WORDS.get(token)
        if quantity is not None:
            return quantity

    return None


def _extract_product_hint(normalized_message: str) -> str | None:
    has_bidon = "bidon" in normalized_message or "bidones" in normalized_message
    has_botellon = "botellon" in normalized_message or "botellones" in normalized_message
    has_twenty_liters = any(
        term in normalized_message for term in ("20 litros", "20l", "20 l")
    )

    if has_botellon and has_twenty_liters:
        return "botellon 20 litros"
    if has_bidon and has_twenty_liters:
        return "bidon 20 litros"
    if has_botellon:
        return "botellon"
    if has_bidon:
        return "bidon"
    if has_twenty_liters:
        return "20 litros"
    if "botella" in normalized_message or "botellas" in normalized_message:
        return "botella"
    if "agua" in normalized_message:
        return "agua"
    return None


def _extract_address_hint(normalized_message: str) -> str | None:
    for term in ("de siempre", "direccion", "casa", "domicilio", "entrega"):
        if term in normalized_message:
            return term
    return None


def _match_product(
    products: list[Product],
    *,
    normalized_message: str,
    product_hint: str | None,
) -> Product | None:
    if not product_hint:
        return None

    normalized_hint = normalize_text(product_hint)
    hint_terms = set(normalized_hint.split())
    best_product: Product | None = None
    best_score = 0

    for product in products:
        normalized_name = product.normalized_name or normalize_text(product.name)
        product_terms = set(normalized_name.split())
        score = 0

        if normalized_name and normalized_name in normalized_message:
            score += 5
        if normalized_hint and normalized_hint in normalized_name:
            score += 4
        score += len(hint_terms & product_terms)

        if score > best_score:
            best_product = product
            best_score = score

    return best_product if best_score >= 2 else None


def _detect_intent(
    normalized_message: str,
    *,
    product_hint: str | None,
    address_hint: str | None,
) -> tuple[AgentIntent, float]:
    has_order_signal = _contains_any(normalized_message, ORDER_TERMS) or product_hint is not None

    if _contains_any(normalized_message, CANCEL_TERMS):
        return AgentIntent.CANCEL_ORDER, 0.87
    if _contains_any(normalized_message, PRICE_TERMS):
        return AgentIntent.ASK_PRICE, 0.86
    if _contains_any(normalized_message, STATUS_TERMS):
        return AgentIntent.ASK_ORDER_STATUS, 0.84
    if has_order_signal:
        return AgentIntent.CREATE_ORDER, 0.85
    if address_hint is not None:
        return AgentIntent.PROVIDE_ADDRESS, 0.72
    if _contains_any(normalized_message, GREETING_TERMS):
        return AgentIntent.GREETING, 0.8
    return AgentIntent.UNKNOWN, 0.35


def _customer_match(customer: Customer | None) -> AgentCustomerMatch:
    if customer is None:
        return AgentCustomerMatch(found=False)
    return AgentCustomerMatch(
        found=True,
        id=customer.id,
        display_name=customer.display_name,
    )


def _customer_has_registered_address(customer: Customer | None) -> bool:
    return bool(customer and customer.addresses)


def _missing_fields(
    *,
    intent: AgentIntent,
    customer: Customer | None,
    quantity: int | None,
    product: Product | None,
) -> list[str]:
    if intent != AgentIntent.CREATE_ORDER:
        return []

    missing: list[str] = []
    if customer is None:
        missing.append("customer_id")
    if quantity is None:
        missing.append("quantity")
    if product is None:
        missing.append("product_id")
    missing.append("address_id")
    return missing


def _format_price(price: Decimal) -> str:
    return f"{price:.2f}"


def _reply_for_create_order(
    *,
    customer: Customer | None,
    quantity: int | None,
    product: Product | None,
) -> str:
    if customer is None:
        return (
            "Puedo ayudarte con el pedido, pero no encuentro un cliente registrado "
            "con este telefono. Indicame tu nombre y direccion."
        )
    if product is None:
        return "Claro. Que producto deseas pedir?"
    if quantity is None:
        return "Claro. Cuantas unidades deseas?"
    if _customer_has_registered_address(customer):
        return "Claro. Deseas que lo enviemos a tu direccion registrada?"
    return "Claro. A que direccion lo enviamos?"


def _reply_for_price(product: Product | None) -> str:
    if product is None:
        return "De que producto deseas consultar el precio?"
    return f"El precio de {product.name} es {_format_price(product.price)} por {product.unit}."


def _reply_for_order_status(customer: Customer | None, orders: list[Order]) -> str:
    if customer is None:
        return "No encuentro un cliente registrado con este telefono para consultar pedidos."
    if not orders:
        return "No encuentro pedidos registrados para este cliente."
    latest_order = orders[0]
    return (
        f"Tu ultimo pedido {latest_order.order_number} esta en estado "
        f"{latest_order.status.name}."
    )


def _reply_for_cancel_order(customer: Customer | None) -> str:
    if customer is None:
        return "No encuentro un cliente registrado con este telefono para revisar cancelaciones."
    return (
        "Puedo ayudarte a revisar una cancelacion, pero esta simulacion no cancela "
        "pedidos automaticamente."
    )


def _build_reply(
    *,
    intent: AgentIntent,
    customer: Customer | None,
    quantity: int | None,
    product: Product | None,
    orders: list[Order],
) -> str:
    if intent == AgentIntent.GREETING:
        return "Hola. Que necesitas pedir hoy?"
    if intent == AgentIntent.CREATE_ORDER:
        return _reply_for_create_order(
            customer=customer,
            quantity=quantity,
            product=product,
        )
    if intent == AgentIntent.ASK_PRICE:
        return _reply_for_price(product)
    if intent == AgentIntent.ASK_ORDER_STATUS:
        return _reply_for_order_status(customer, orders)
    if intent == AgentIntent.CANCEL_ORDER:
        return _reply_for_cancel_order(customer)
    if intent == AgentIntent.PROVIDE_ADDRESS:
        return "Recibi la referencia de direccion. Aun necesito confirmar el pedido."
    return "No estoy seguro de como ayudarte con ese mensaje. Puedes reformularlo?"


def simulate_agent_message(
    db: Session,
    *,
    phone: str,
    message: str,
) -> AgentSimulationResponse:
    if not message or not message.strip():
        raise ValueError("Message is required.")

    normalized_phone = normalize_ecuador_phone(phone)
    normalized_message = normalize_text(message)
    if not normalized_message:
        raise ValueError("Message is required.")

    customer = search_customer_by_phone(db, normalized_phone)
    product_hint = _extract_product_hint(normalized_message)
    address_hint = _extract_address_hint(normalized_message)
    quantity = _extract_quantity(normalized_message)
    intent, confidence = _detect_intent(
        normalized_message,
        product_hint=product_hint,
        address_hint=address_hint,
    )

    active_products = list_products(db, active_only=True)
    product = _match_product(
        active_products,
        normalized_message=normalized_message,
        product_hint=product_hint,
    )
    orders = (
        list_orders(db, customer_id=customer.id)
        if intent == AgentIntent.ASK_ORDER_STATUS and customer is not None
        else []
    )

    missing_fields = _missing_fields(
        intent=intent,
        customer=customer,
        quantity=quantity,
        product=product,
    )

    return AgentSimulationResponse(
        intent=intent,
        confidence=confidence,
        customer=_customer_match(customer),
        extracted=AgentExtraction(
            quantity=quantity,
            product_hint=product_hint,
            product_id=product.id if product else None,
            product_name=product.name if product else None,
            product_price=product.price if product else None,
            address_hint=address_hint,
        ),
        missing_fields=missing_fields,
        reply=_build_reply(
            intent=intent,
            customer=customer,
            quantity=quantity,
            product=product,
            orders=orders,
        ),
    )
