from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.order import Order
from app.schemas.agent import AgentIntent
from app.services.agent import simulate_agent_message
from app.services.orders import OrderItemInput, create_order


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def test_agent_detects_greeting(db_session: Session) -> None:
    result = simulate_agent_message(
        db_session,
        phone="+593999111222",
        message="Hola buenas tardes",
    )

    assert result.intent == AgentIntent.GREETING
    assert result.customer.found is False
    assert result.missing_fields == []
    assert "Hola" in result.reply


def test_agent_detects_order_with_product_and_quantity(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    customer = create_test_customer(phone="0999627968")
    product = create_test_product(
        sku="AGENT-BIDON-20",
        name="Bidon 20 Litros",
        unit="bidon",
        price=Decimal("3.50"),
    )

    result = simulate_agent_message(
        db_session,
        phone="+593999627968",
        message="Hola, quiero 2 bidones de 20 litros",
    )

    assert result.intent == AgentIntent.CREATE_ORDER
    assert result.customer.found is True
    assert result.customer.id == customer.id
    assert result.extracted.quantity == 2
    assert result.extracted.product_hint == "bidon 20 litros"
    assert result.extracted.product_id == product.id
    assert result.extracted.product_price == Decimal("3.50")
    assert result.missing_fields == ["address_id"]


def test_agent_order_without_address_requests_confirmation(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(
        sku="AGENT-BOTELLON-20",
        name="Botellon 20 Litros",
        unit="botellon",
    )

    result = simulate_agent_message(
        db_session,
        phone="0999627968",
        message="Necesito un botellon de 20 litros",
    )

    assert result.intent == AgentIntent.CREATE_ORDER
    assert result.extracted.quantity == 1
    assert "address_id" in result.missing_fields
    assert "direccion registrada" in result.reply


def test_agent_finds_existing_customer_by_phone(
    db_session: Session,
    create_test_customer,
) -> None:
    customer = create_test_customer(display_name="Cliente Agente", phone="0999627968")

    result = simulate_agent_message(
        db_session,
        phone="+593999627968",
        message="Hola",
    )

    assert result.customer.found is True
    assert result.customer.id == customer.id
    assert result.customer.display_name == "Cliente Agente"


def test_agent_does_not_invent_missing_customer(db_session: Session) -> None:
    result = simulate_agent_message(
        db_session,
        phone="+593999111222",
        message="Necesito 1 bidon de 20 litros",
    )

    assert result.intent == AgentIntent.CREATE_ORDER
    assert result.customer.found is False
    assert result.customer.id is None
    assert "customer_id" in result.missing_fields
    assert "no encuentro un cliente" in result.reply


def test_agent_answers_price_when_product_is_clear(
    db_session: Session,
    create_test_product,
) -> None:
    product = create_test_product(
        sku="AGENT-PRECIO",
        name="Bidon 20 Litros",
        unit="bidon",
        price=Decimal("4.25"),
    )

    result = simulate_agent_message(
        db_session,
        phone="+593999111222",
        message="Cuanto cuesta el bidon de 20 litros?",
    )

    assert result.intent == AgentIntent.ASK_PRICE
    assert result.extracted.product_id == product.id
    assert result.extracted.product_price == Decimal("4.25")
    assert "4.25" in result.reply


def test_agent_detects_unknown_intent(db_session: Session) -> None:
    result = simulate_agent_message(
        db_session,
        phone="+593999111222",
        message="azul rapido sin contexto",
    )

    assert result.intent == AgentIntent.UNKNOWN
    assert result.customer.found is False
    assert result.missing_fields == []


def test_agent_rejects_invalid_phone(db_session: Session) -> None:
    with pytest.raises(ValueError, match="valid Ecuadorian mobile"):
        simulate_agent_message(
            db_session,
            phone="12345",
            message="Hola",
        )


def test_agent_rejects_empty_message(db_session: Session) -> None:
    with pytest.raises(ValueError, match="Message is required"):
        simulate_agent_message(
            db_session,
            phone="+593999111222",
            message="   ",
        )


def test_agent_order_status_uses_orders_from_matched_customer_only(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    customer = create_test_customer(
        display_name="Cliente Sin Pedido",
        phone="0999627968",
    )
    other_customer = create_test_customer(
        display_name="Cliente Con Pedido",
        phone="0987654321",
    )
    product = create_test_product(sku="AGENT-STATUS", price=Decimal("2.00"))
    create_order(
        db_session,
        customer_id=other_customer.id,
        address_id=other_customer.addresses[0].id,
        items=[OrderItemInput(product_id=product.id, quantity=Decimal("1"))],
    )

    result = simulate_agent_message(
        db_session,
        phone="+593999627968",
        message="Donde esta mi pedido?",
    )

    assert result.intent == AgentIntent.ASK_ORDER_STATUS
    assert result.customer.id == customer.id
    assert "No encuentro pedidos" in result.reply


def test_agent_does_not_create_orders(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(sku="AGENT-NO-CREATE", name="Bidon 20 Litros")
    before_count = _order_count(db_session)

    simulate_agent_message(
        db_session,
        phone="+593999627968",
        message="Quiero dos bidones de 20 litros",
    )

    assert _order_count(db_session) == before_count
