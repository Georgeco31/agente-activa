from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.action_history import ActionHistory
from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession
from app.models.customer_address import CustomerAddress
from app.models.order import Order
from app.schemas.agent import ConversationStatus
from app.services.agent_orders import (
    AgentOrderDuplicateRecentError,
    AgentOrderInvalidConfirmationError,
    AgentOrderNotReadyError,
    confirm_order_from_conversation,
)
from app.services.conversations import simulate_conversation_message
from app.services.normalization import normalize_text
from app.services.orders import OrderItemInput, create_order


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def _prepare_ready_session(
    db_session: Session,
    create_test_customer,
    create_test_product,
    *,
    sku: str = "AGENT-CONFIRM",
):
    customer = create_test_customer(phone="0999627968")
    product = create_test_product(
        name="Bidon 20 Litros",
        sku=sku,
        price=Decimal("3.50"),
    )
    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero un bidon de 20 litros",
    )
    second = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="A la direccion de siempre",
    )
    assert second.session.id == first.session.id

    session = db_session.get(ConversationSession, second.session.id)
    assert session is not None
    assert session.status == ConversationStatus.READY_FOR_CONFIRMATION.value
    assert session.extracted_data["confirmation_summary"]["status"] == "pending"
    return session, customer, product


def _replace_confirmation_summary(
    db_session: Session,
    session: ConversationSession,
    **values,
) -> None:
    extracted_data = dict(session.extracted_data)
    summary = dict(extracted_data["confirmation_summary"])
    summary.update(values)
    extracted_data["confirmation_summary"] = summary
    session.extracted_data = extracted_data
    db_session.flush()


def test_ready_session_does_not_create_order_without_explicit_confirmation(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-NO-CONFIRM",
    )
    before_count = _order_count(db_session)

    with pytest.raises(AgentOrderInvalidConfirmationError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="hola")

    assert _order_count(db_session) == before_count


def test_explicit_confirmation_creates_order_when_data_is_complete(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-CREATE",
    )

    response = confirm_order_from_conversation(
        db_session,
        session_id=session.id,
        message="confirmo",
    )

    assert response.order.customer_id == customer.id
    assert response.order.status.code == "pendiente"
    assert response.order.source_channel == "agent_conversation"
    assert response.order.total == Decimal("3.50")


def test_ambiguous_confirmation_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-AMBIGUOUS",
    )
    before_count = _order_count(db_session)

    with pytest.raises(AgentOrderInvalidConfirmationError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="tal vez")

    assert _order_count(db_session) == before_count


def test_missing_customer_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-NO-CUSTOMER",
    )
    session.customer_id = None
    db_session.flush()
    before_count = _order_count(db_session)

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")

    assert _order_count(db_session) == before_count


def test_phone_not_associated_to_customer_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-PHONE-MISMATCH",
    )
    session.normalized_phone = "+593999111111"
    db_session.flush()
    before_count = _order_count(db_session)

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")

    assert _order_count(db_session) == before_count


def test_missing_product_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-NO-PRODUCT",
    )
    _replace_confirmation_summary(db_session, session, product_id=str(uuid4()))

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")


def test_inactive_product_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-INACTIVE",
    )
    product.is_active = False
    db_session.flush()

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")


def test_invalid_quantity_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-BAD-QTY",
    )
    _replace_confirmation_summary(db_session, session, quantity="1")

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")


def test_quantity_above_limit_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-QTY-LIMIT",
    )
    _replace_confirmation_summary(db_session, session, quantity=51)

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")


def test_missing_address_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-NO-ADDRESS",
    )
    _replace_confirmation_summary(db_session, session, address_id=str(uuid4()))

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")


def test_address_from_other_customer_does_not_create_order(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-WRONG-ADDRESS",
    )
    other_customer = create_test_customer(
        display_name="Otro Cliente Agente",
        phone="0987654321",
    )
    _replace_confirmation_summary(
        db_session,
        session,
        address_id=str(other_customer.addresses[0].id),
    )

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")


def test_multiple_customer_addresses_require_clarification_before_confirmation(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    customer = create_test_customer(phone="0999627968")
    customer.addresses.append(
        CustomerAddress(
            label="trabajo",
            address_text="Avenida 20 # 10-30",
            normalized_address=normalize_text("Avenida 20 # 10-30"),
            reference="Recepcion",
            normalized_reference=normalize_text("Recepcion"),
            is_primary=False,
        )
    )
    create_test_product(name="Bidon 20 Litros", sku="AGENT-MULTI-ADDRESS")
    db_session.flush()

    simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero un bidon de 20 litros",
    )
    response = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="A la direccion de siempre",
    )
    session = db_session.get(ConversationSession, response.session.id)
    before_count = _order_count(db_session)

    with pytest.raises(AgentOrderNotReadyError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")

    assert response.session.status == ConversationStatus.WAITING_FOR_CUSTOMER
    assert response.analysis.missing_fields == ["address_id"]
    assert response.analysis.extracted.address_id is None
    assert "varias direcciones" in response.analysis.reply
    assert "confirmation_summary" not in session.extracted_data
    assert _order_count(db_session) == before_count


def test_session_closes_and_order_id_is_stored_after_creation(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-CLOSES",
    )

    response = confirm_order_from_conversation(db_session, session_id=session.id, message="ok")

    stored_session = db_session.get(ConversationSession, session.id)
    assert stored_session.status == ConversationStatus.CLOSED.value
    assert stored_session.extracted_data["order_id"] == str(response.order.id)
    assert stored_session.extracted_data["order_number"] == response.order.order_number
    assert stored_session.extracted_data["confirmation_summary"]["status"] == "confirmed"


def test_confirmation_saves_internal_outbound_message(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-OUTBOUND",
    )

    response = confirm_order_from_conversation(db_session, session_id=session.id, message="dale")

    message = db_session.scalar(
        select(ConversationMessage)
        .where(
            ConversationMessage.session_id == session.id,
            ConversationMessage.message_metadata["order_number"].astext
            == response.order.order_number,
        )
        .order_by(ConversationMessage.created_at.desc())
    )
    assert message is not None
    assert message.direction == "outbound"
    assert message.message_metadata["sent_to_provider"] is False


def test_confirmation_records_agent_audit_action(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, _customer, _product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-AUDIT",
    )

    response = confirm_order_from_conversation(
        db_session,
        session_id=session.id,
        message="de acuerdo",
    )

    action = db_session.scalar(
        select(ActionHistory).where(
            ActionHistory.order_id == response.order.id,
            ActionHistory.action_type == "order_created_by_agent",
        )
    )
    assert action is not None
    assert action.new_value["conversation_session_id"] == str(session.id)
    assert action.new_value["confirmed_by_customer"] is True


def test_recent_duplicate_blocks_creation(
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session, customer, product = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-DUPLICATE",
    )
    create_order(
        db_session,
        customer_id=customer.id,
        address_id=customer.addresses[0].id,
        items=[OrderItemInput(product_id=product.id, quantity=Decimal("1"))],
    )
    before_count = _order_count(db_session)

    with pytest.raises(AgentOrderDuplicateRecentError):
        confirm_order_from_conversation(db_session, session_id=session.id, message="si")

    assert _order_count(db_session) == before_count
