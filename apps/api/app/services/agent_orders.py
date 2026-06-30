from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation_session import ConversationSession
from app.models.order import Order
from app.repositories import conversations as conversation_repository
from app.repositories import orders as order_repository
from app.schemas.agent import (
    AgentConversationSessionDetail,
    AgentIntent,
    AgentOrderConfirmationResponse,
    ConversationMessageDirection,
    ConversationStatus,
)
from app.schemas.order import OrderResponse
from app.services.action_history import record_action
from app.services.conversations import ConversationNotFoundError, get_conversation_session
from app.services.normalization import normalize_text
from app.services.orders import OrderItemInput, create_order

AGENT_ORDER_SOURCE = "agent_conversation"
MAX_AGENT_ORDER_QUANTITY = 50
RECENT_DUPLICATE_WINDOW_MINUTES = 10
RECENT_DUPLICATE_STATUS_CODES = {"pendiente", "asignado", "en_camino"}

EXPLICIT_CONFIRMATIONS = {
    "si",
    "confirmo",
    "confirmado",
    "correcto",
    "dale",
    "ok",
    "esta bien",
    "de acuerdo",
    "procede",
}
AMBIGUOUS_OR_NEGATIVE_CONFIRMATIONS = {
    "tal vez",
    "despues",
    "espera",
    "creo que si",
    "no se",
    "no",
}


class AgentOrderError(ValueError):
    pass


class AgentOrderNotReadyError(AgentOrderError):
    pass


class AgentOrderInvalidConfirmationError(AgentOrderError):
    pass


class AgentOrderDuplicateRecentError(AgentOrderError):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid_from_summary(summary: dict[str, Any], field_name: str) -> UUID:
    value = summary.get(field_name)
    try:
        return UUID(str(value))
    except (TypeError, ValueError) as exc:
        raise AgentOrderNotReadyError(f"{field_name} is required.") from exc


def _quantity_from_summary(summary: dict[str, Any]) -> int:
    quantity = summary.get("quantity")
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise AgentOrderNotReadyError("Quantity must be an integer.")
    if quantity <= 0:
        raise AgentOrderNotReadyError("Quantity must be greater than zero.")
    if quantity > MAX_AGENT_ORDER_QUANTITY:
        raise AgentOrderNotReadyError(
            f"Quantity must be less than or equal to {MAX_AGENT_ORDER_QUANTITY}."
        )
    return quantity


def _ensure_explicit_confirmation(message: str) -> None:
    normalized_message = normalize_text(message)
    if normalized_message in EXPLICIT_CONFIRMATIONS:
        return
    if (
        normalized_message in AMBIGUOUS_OR_NEGATIVE_CONFIRMATIONS
        or "tal vez" in normalized_message
        or "creo que si" in normalized_message
    ):
        raise AgentOrderInvalidConfirmationError(
            "Confirmation is ambiguous. Please confirm clearly before creating the order."
        )
    raise AgentOrderInvalidConfirmationError(
        "Order was not confirmed. Please send a clear confirmation."
    )


def _pending_confirmation_summary(session: ConversationSession) -> dict[str, Any]:
    extracted_data = dict(session.extracted_data or {})
    summary = extracted_data.get("confirmation_summary")
    if not isinstance(summary, dict) or summary.get("status") != "pending":
        raise AgentOrderNotReadyError("Conversation does not have a pending confirmation summary.")
    return summary


def _ensure_session_can_create_order(session: ConversationSession) -> None:
    if session.status == ConversationStatus.CLOSED.value:
        raise AgentOrderNotReadyError("Conversation is closed.")
    if session.status != ConversationStatus.READY_FOR_CONFIRMATION.value:
        raise AgentOrderNotReadyError("Conversation is not ready for confirmation.")


def _validate_customer_phone(session: ConversationSession) -> None:
    customer = session.customer
    if customer is None:
        raise AgentOrderNotReadyError("Customer is required.")
    if not any(phone.normalized_phone == session.normalized_phone for phone in customer.phones):
        raise AgentOrderNotReadyError("Conversation phone is not associated with the customer.")


def _validate_order_inputs(
    db: Session,
    *,
    session: ConversationSession,
    summary: dict[str, Any],
) -> tuple[UUID, UUID, UUID, int, Decimal]:
    if session.customer_id is None:
        raise AgentOrderNotReadyError("Customer is required.")

    customer_id = _uuid_from_summary(summary, "customer_id")
    product_id = _uuid_from_summary(summary, "product_id")
    address_id = _uuid_from_summary(summary, "address_id")
    quantity = _quantity_from_summary(summary)

    if customer_id != session.customer_id:
        raise AgentOrderNotReadyError("Confirmation customer does not match conversation.")

    product = order_repository.get_product_by_id(db, product_id)
    if product is None:
        raise AgentOrderNotReadyError("Product not found.")
    if not product.is_active:
        raise AgentOrderNotReadyError("Inactive products cannot be ordered.")
    if product.price < 0:
        raise AgentOrderNotReadyError("Product price is invalid.")

    address = order_repository.get_address_by_id(db, address_id)
    if address is None:
        raise AgentOrderNotReadyError("Address not found.")
    if address.customer_id != customer_id:
        raise AgentOrderNotReadyError("Address does not belong to customer.")

    return customer_id, product_id, address_id, quantity, product.price


def _ensure_no_recent_duplicate(
    db: Session,
    *,
    customer_id: UUID,
    address_id: UUID,
    product_id: UUID,
    quantity: int,
) -> None:
    duplicate = order_repository.find_recent_similar_order(
        db,
        customer_id=customer_id,
        customer_address_id=address_id,
        product_id=product_id,
        quantity=Decimal(quantity),
        created_after=_now() - timedelta(minutes=RECENT_DUPLICATE_WINDOW_MINUTES),
        status_codes=RECENT_DUPLICATE_STATUS_CODES,
    )
    if duplicate is not None:
        raise AgentOrderDuplicateRecentError(
            "A recent similar order already exists for this customer."
        )


def _record_agent_audit(
    db: Session,
    *,
    session: ConversationSession,
    order: Order,
) -> None:
    record_action(
        db,
        entity_type="order",
        entity_id=order.id,
        customer_id=order.customer_id,
        order_id=order.id,
        action_type="order_created_by_agent",
        description="Order created from agent conversation.",
        new_value={
            "conversation_session_id": str(session.id),
            "phone": session.phone,
            "order_id": str(order.id),
            "order_number": order.order_number,
            "confirmed_by_customer": True,
            "source": AGENT_ORDER_SOURCE,
        },
        performed_by_type="agent",
        performed_by_id=str(session.id),
    )


def _close_session_with_order(
    db: Session,
    *,
    session: ConversationSession,
    order: Order,
) -> str:
    confirmed_at = _now().isoformat()
    extracted_data = dict(session.extracted_data or {})
    confirmation_summary = dict(extracted_data.get("confirmation_summary") or {})
    confirmation_summary["status"] = "confirmed"
    confirmation_summary["confirmed_at"] = confirmed_at
    extracted_data.update(
        {
            "confirmation_summary": confirmation_summary,
            "order_id": str(order.id),
            "order_number": order.order_number,
            "confirmed_at": confirmed_at,
            "order_created": True,
        }
    )
    reply = f"Pedido {order.order_number} creado correctamente. Estado inicial: pendiente."

    conversation_repository.update_session(
        db,
        session,
        {
            "status": ConversationStatus.CLOSED.value,
            "extracted_data": extracted_data,
            "missing_fields": [],
            "last_message_at": _now(),
        },
    )
    conversation_repository.create_message(
        db,
        session_id=session.id,
        direction=ConversationMessageDirection.OUTBOUND.value,
        phone=session.phone,
        message=reply,
        intent=AgentIntent.CREATE_ORDER.value,
        confidence=None,
        message_metadata={
            "order_id": str(order.id),
            "order_number": order.order_number,
            "source": AGENT_ORDER_SOURCE,
            "sent_to_provider": False,
        },
    )
    return reply


def confirm_order_from_conversation(
    db: Session,
    *,
    session_id: UUID,
    message: str,
) -> AgentOrderConfirmationResponse:
    try:
        session = get_conversation_session(db, session_id=session_id)
    except ConversationNotFoundError:
        raise

    _ensure_session_can_create_order(session)
    _ensure_explicit_confirmation(message)
    summary = _pending_confirmation_summary(session)
    _validate_customer_phone(session)
    customer_id, product_id, address_id, quantity, unit_price = _validate_order_inputs(
        db,
        session=session,
        summary=summary,
    )
    _ensure_no_recent_duplicate(
        db,
        customer_id=customer_id,
        address_id=address_id,
        product_id=product_id,
        quantity=quantity,
    )

    order = create_order(
        db,
        customer_id=customer_id,
        address_id=address_id,
        items=[
            OrderItemInput(
                product_id=product_id,
                quantity=Decimal(quantity),
                unit_price=unit_price,
            )
        ],
        notes=f"Created from agent conversation {session.id}.",
        source_channel=AGENT_ORDER_SOURCE,
    )
    _record_agent_audit(db, session=session, order=order)
    reply = _close_session_with_order(db, session=session, order=order)
    session = get_conversation_session(db, session_id=session.id)

    return AgentOrderConfirmationResponse(
        session=AgentConversationSessionDetail.model_validate(session),
        order=OrderResponse.model_validate(order),
        reply=reply,
    )
