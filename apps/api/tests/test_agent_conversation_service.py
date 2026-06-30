from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.order import Order
from app.schemas.agent import ConversationStatus
from app.services.conversations import close_conversation_session, simulate_conversation_message


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def _message_count(db_session: Session, session_id) -> int:
    return (
        db_session.scalar(
            select(func.count())
            .select_from(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
        )
        or 0
    )


def test_conversation_creates_new_session_with_first_message(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    customer = create_test_customer(phone="0999627968")
    product = create_test_product(name="Bidon 20 Litros", sku="CONV-FIRST")

    response = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Hola, quiero un bidon de 20 litros",
    )

    session = db_session.get(ConversationSession, response.session.id)
    assert session is not None
    assert session.normalized_phone == "+593999627968"
    assert session.customer_id == customer.id
    assert session.current_intent == "create_order"
    assert session.extracted_data["quantity"] == 1
    assert session.extracted_data["product_id"] == str(product.id)
    assert response.session.status == ConversationStatus.WAITING_FOR_CUSTOMER
    assert response.analysis.missing_fields == ["address_id"]


def test_conversation_reuses_active_session_by_phone(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="CONV-REUSE")

    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero un bidon de 20 litros",
    )
    second = simulate_conversation_message(
        db_session,
        phone="0999627968",
        message="A la direccion de siempre",
    )

    assert second.session.id == first.session.id
    assert _message_count(db_session, first.session.id) == 4


def test_conversation_stores_inbound_and_outbound_messages(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="CONV-MESSAGES")

    response = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Necesito 2 bidones de 20 litros",
    )

    messages = db_session.scalars(
        select(ConversationMessage)
        .where(ConversationMessage.session_id == response.session.id)
        .order_by(ConversationMessage.created_at)
    ).all()
    assert [message.direction for message in messages] == ["inbound", "outbound"]
    assert messages[0].message == "Necesito 2 bidones de 20 litros"
    assert messages[0].intent == "create_order"
    assert messages[1].message == response.analysis.reply
    assert messages[1].message_metadata["missing_fields"] == ["address_id"]


def test_conversation_accumulates_extracted_data_between_messages(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    product = create_test_product(name="Bidon 20 Litros", sku="CONV-ACCUMULATE")

    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero dos bidones de 20 litros",
    )
    second = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="A la direccion de siempre",
    )

    assert second.session.id == first.session.id
    assert second.analysis.extracted.quantity == 2
    assert second.analysis.extracted.product_id == product.id
    assert second.analysis.extracted.address_hint == "de siempre"
    assert second.analysis.missing_fields == []
    assert second.session.status == ConversationStatus.READY_FOR_CONFIRMATION


def test_conversation_does_not_overwrite_valid_fields_with_null(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    product = create_test_product(name="Bidon 20 Litros", sku="CONV-NO-OVERWRITE")

    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero 3 bidones de 20 litros",
    )
    second = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Hola",
    )

    assert second.session.id == first.session.id
    assert second.analysis.extracted.quantity == 3
    assert second.analysis.extracted.product_id == product.id
    assert "address_id" in second.analysis.missing_fields


def test_conversation_updates_missing_fields_after_address_hint(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="CONV-MISSING")

    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero un bidon de 20 litros",
    )
    second = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="A mi casa de siempre",
    )

    assert first.analysis.missing_fields == ["address_id"]
    assert second.analysis.missing_fields == []


def test_conversation_associates_existing_customer(
    db_session: Session,
    create_test_customer,
) -> None:
    customer = create_test_customer(display_name="Cliente Conversacion", phone="0999627968")

    response = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Hola",
    )

    assert response.analysis.customer.found is True
    assert response.analysis.customer.id == customer.id
    assert db_session.get(ConversationSession, response.session.id).customer_id == customer.id


def test_conversation_keeps_session_without_missing_customer(db_session: Session) -> None:
    response = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero un bidon de 20 litros",
    )

    session = db_session.get(ConversationSession, response.session.id)
    assert response.analysis.customer.found is False
    assert session is not None
    assert session.customer_id is None
    assert "customer_id" in response.analysis.missing_fields


def test_close_conversation_session_marks_session_closed(
    db_session: Session,
    create_test_customer,
) -> None:
    create_test_customer(phone="0999627968")
    response = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Hola",
    )

    session = close_conversation_session(db_session, session_id=response.session.id)

    assert session.status == ConversationStatus.CLOSED.value
    assert _message_count(db_session, session.id) == 2


def test_new_message_after_closed_session_creates_new_session(
    db_session: Session,
    create_test_customer,
) -> None:
    create_test_customer(phone="0999627968")
    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Hola",
    )
    close_conversation_session(db_session, session_id=first.session.id)

    second = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Hola otra vez",
    )

    assert second.session.id != first.session.id


def test_conversation_does_not_create_orders(
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(
        name="Bidon 20 Litros",
        sku="CONV-NO-ORDER",
        price=Decimal("3.50"),
    )
    before_count = _order_count(db_session)

    simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero 2 bidones de 20 litros",
    )

    assert _order_count(db_session) == before_count
