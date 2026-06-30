from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation_session import ConversationSession
from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.product import Product
from app.repositories import conversations as conversation_repository
from app.schemas.agent import (
    AgentConversationSessionSummary,
    AgentConversationSimulationResponse,
    AgentExtraction,
    AgentIntent,
    AgentSimulationResponse,
    ConversationMessageDirection,
    ConversationStatus,
)
from app.services.agent import simulate_agent_message
from app.services.normalization import normalize_ecuador_phone

OPEN_SESSION_STATUSES = {
    ConversationStatus.ACTIVE.value,
    ConversationStatus.WAITING_FOR_CUSTOMER.value,
    ConversationStatus.READY_FOR_CONFIRMATION.value,
}

SINGLE_ADDRESS_HINTS = {"casa", "de siempre", "direccion", "domicilio", "entrega"}


class ConversationNotFoundError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(UTC)


def _json_model(value) -> dict[str, Any]:
    return value.model_dump(mode="json")


def _merge_extracted_data(
    current_data: dict[str, Any] | None,
    new_data: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(current_data or {})
    for field_name, value in new_data.items():
        if value is not None:
            merged[field_name] = value
    return merged


def _uuid_from_data(value: Any) -> UUID | None:
    if value is None:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        return None


def _resolve_single_customer_address(
    db: Session,
    *,
    customer_id: UUID | None,
    extracted_data: dict[str, Any],
) -> dict[str, Any]:
    if customer_id is None or extracted_data.get("address_id") is not None:
        return extracted_data

    address_hint = extracted_data.get("address_hint")
    if address_hint not in SINGLE_ADDRESS_HINTS:
        return extracted_data

    customer = db.get(Customer, customer_id)
    if customer is None or len(customer.addresses) != 1:
        return extracted_data

    address = customer.addresses[0]
    return {
        **extracted_data,
        "address_id": str(address.id),
        "address_text": address.address_text,
        "address_reference": address.reference,
    }


def _next_intent(
    current_intent: str | None,
    incoming_intent: AgentIntent,
) -> str:
    if (
        current_intent
        and incoming_intent
        in {
            AgentIntent.GREETING,
            AgentIntent.PROVIDE_ADDRESS,
            AgentIntent.UNKNOWN,
        }
    ):
        return current_intent
    return incoming_intent.value


def _missing_fields_for_accumulated_data(
    *,
    current_intent: str | None,
    customer_id: UUID | None,
    extracted_data: dict[str, Any],
) -> list[str]:
    if current_intent != AgentIntent.CREATE_ORDER.value:
        return []

    missing: list[str] = []
    if customer_id is None:
        missing.append("customer_id")
    if extracted_data.get("quantity") is None:
        missing.append("quantity")
    if extracted_data.get("product_id") is None:
        missing.append("product_id")
    if extracted_data.get("address_id") is None:
        missing.append("address_id")
    return missing


def _build_confirmation_summary(
    db: Session,
    *,
    customer_id: UUID | None,
    extracted_data: dict[str, Any],
) -> dict[str, Any] | None:
    if customer_id is None:
        return None

    product_id = _uuid_from_data(extracted_data.get("product_id"))
    address_id = _uuid_from_data(extracted_data.get("address_id"))
    quantity = extracted_data.get("quantity")
    if product_id is None or address_id is None or not isinstance(quantity, int):
        return None

    customer = db.get(Customer, customer_id)
    product = db.get(Product, product_id)
    address = db.get(CustomerAddress, address_id)
    if customer is None or product is None or address is None:
        return None
    if address.customer_id != customer.id:
        return None

    unit_price = product.price
    total = unit_price * quantity
    return {
        "customer_id": str(customer.id),
        "customer_name": customer.display_name,
        "product_id": str(product.id),
        "product_name": product.name,
        "quantity": quantity,
        "address_id": str(address.id),
        "address_text": address.address_text,
        "unit_price": f"{unit_price:.2f}",
        "total": f"{total:.2f}",
        "generated_at": _now().isoformat(),
        "status": "pending",
    }


def _reply_for_accumulated_state(
    db: Session,
    *,
    customer_id: UUID | None,
    extracted_data: dict[str, Any],
    missing_fields: list[str],
    fallback_reply: str,
) -> str:
    if "address_id" not in missing_fields:
        return fallback_reply
    if extracted_data.get("address_hint") not in SINGLE_ADDRESS_HINTS:
        return fallback_reply
    if customer_id is None:
        return fallback_reply

    customer = db.get(Customer, customer_id)
    if customer is not None and len(customer.addresses) > 1:
        return "Tengo varias direcciones registradas. Indicame a cual enviamos el pedido."
    return fallback_reply


def _status_for_session(
    *,
    current_intent: str | None,
    missing_fields: list[str],
) -> str:
    if current_intent == AgentIntent.CREATE_ORDER.value:
        return (
            ConversationStatus.READY_FOR_CONFIRMATION.value
            if not missing_fields
            else ConversationStatus.WAITING_FOR_CUSTOMER.value
        )
    return ConversationStatus.ACTIVE.value


def _analysis_with_accumulated_data(
    analysis: AgentSimulationResponse,
    *,
    extracted_data: dict[str, Any],
    missing_fields: list[str],
    reply: str | None = None,
) -> AgentSimulationResponse:
    return AgentSimulationResponse(
        intent=analysis.intent,
        confidence=analysis.confidence,
        customer=analysis.customer,
        extracted=AgentExtraction(**extracted_data),
        missing_fields=missing_fields,
        reply=reply if reply is not None else analysis.reply,
    )


def _confidence_as_decimal(confidence: float | None) -> Decimal | None:
    if confidence is None:
        return None
    return Decimal(str(confidence))


def _session_summary(session: ConversationSession) -> AgentConversationSessionSummary:
    return AgentConversationSessionSummary.model_validate(session)


def _get_or_create_open_session(
    db: Session,
    *,
    phone: str,
    normalized_phone: str,
) -> ConversationSession:
    session = conversation_repository.find_latest_session_by_phone_and_statuses(
        db,
        normalized_phone=normalized_phone,
        statuses=OPEN_SESSION_STATUSES,
    )
    if session is not None:
        return session

    return conversation_repository.create_session(
        db,
        phone=phone,
        normalized_phone=normalized_phone,
        customer_id=None,
        status=ConversationStatus.ACTIVE.value,
        current_intent=None,
        extracted_data={},
        missing_fields=[],
    )


def simulate_conversation_message(
    db: Session,
    *,
    phone: str,
    message: str,
    provider_metadata: dict[str, Any] | None = None,
) -> AgentConversationSimulationResponse:
    normalized_phone = normalize_ecuador_phone(phone)
    session = _get_or_create_open_session(
        db,
        phone=phone,
        normalized_phone=normalized_phone,
    )

    analysis = simulate_agent_message(db, phone=phone, message=message)
    incoming_extracted = _json_model(analysis.extracted)
    extracted_data = _merge_extracted_data(session.extracted_data, incoming_extracted)
    customer_id = analysis.customer.id or session.customer_id
    extracted_data = _resolve_single_customer_address(
        db,
        customer_id=customer_id,
        extracted_data=extracted_data,
    )
    current_intent = _next_intent(session.current_intent, analysis.intent)
    missing_fields = _missing_fields_for_accumulated_data(
        current_intent=current_intent,
        customer_id=customer_id,
        extracted_data=extracted_data,
    )
    status = _status_for_session(
        current_intent=current_intent,
        missing_fields=missing_fields,
    )
    if status == ConversationStatus.READY_FOR_CONFIRMATION.value:
        confirmation_summary = _build_confirmation_summary(
            db,
            customer_id=customer_id,
            extracted_data=extracted_data,
        )
        if confirmation_summary is not None:
            extracted_data["confirmation_summary"] = confirmation_summary
    else:
        extracted_data.pop("confirmation_summary", None)

    reply = _reply_for_accumulated_state(
        db,
        customer_id=customer_id,
        extracted_data=extracted_data,
        missing_fields=missing_fields,
        fallback_reply=analysis.reply,
    )
    accumulated_analysis = _analysis_with_accumulated_data(
        analysis,
        extracted_data=extracted_data,
        missing_fields=missing_fields,
        reply=reply,
    )

    conversation_repository.update_session(
        db,
        session,
        {
            "phone": phone,
            "normalized_phone": normalized_phone,
            "customer_id": customer_id,
            "status": status,
            "current_intent": current_intent,
            "extracted_data": extracted_data,
            "missing_fields": missing_fields,
            "last_message_at": _now(),
        },
    )
    inbound_metadata: dict[str, Any] = {
        "extracted": incoming_extracted,
        "missing_fields": analysis.missing_fields,
    }
    outbound_metadata: dict[str, Any] = {
        "extracted_data": extracted_data,
        "missing_fields": missing_fields,
        "sent_to_provider": False,
    }
    if provider_metadata is not None:
        inbound_metadata["provider"] = provider_metadata
        outbound_metadata["provider"] = provider_metadata

    conversation_repository.create_message(
        db,
        session_id=session.id,
        direction=ConversationMessageDirection.INBOUND.value,
        phone=phone,
        message=message,
        intent=analysis.intent.value,
        confidence=_confidence_as_decimal(analysis.confidence),
        message_metadata=inbound_metadata,
    )
    conversation_repository.create_message(
        db,
        session_id=session.id,
        direction=ConversationMessageDirection.OUTBOUND.value,
        phone=phone,
        message=accumulated_analysis.reply,
        intent=analysis.intent.value,
        confidence=_confidence_as_decimal(analysis.confidence),
        message_metadata=outbound_metadata,
    )

    return AgentConversationSimulationResponse(
        session=_session_summary(session),
        analysis=accumulated_analysis,
    )


def record_unsupported_conversation_message(
    db: Session,
    *,
    phone: str,
    message_type: str | None,
    provider_metadata: dict[str, Any] | None = None,
) -> AgentConversationSessionSummary:
    normalized_phone = normalize_ecuador_phone(phone)
    session = _get_or_create_open_session(
        db,
        phone=phone,
        normalized_phone=normalized_phone,
    )
    unsupported_type = message_type or "unknown"
    current_intent = session.current_intent or AgentIntent.UNKNOWN.value
    status = session.status or ConversationStatus.ACTIVE.value

    conversation_repository.update_session(
        db,
        session,
        {
            "phone": phone,
            "normalized_phone": normalized_phone,
            "status": status,
            "current_intent": current_intent,
            "last_message_at": _now(),
        },
    )
    conversation_repository.create_message(
        db,
        session_id=session.id,
        direction=ConversationMessageDirection.INBOUND.value,
        phone=phone,
        message=f"Unsupported WhatsApp message type: {unsupported_type}",
        intent=AgentIntent.UNKNOWN.value,
        confidence=None,
        message_metadata={
            "unsupported_message_type": unsupported_type,
            "provider": provider_metadata or {},
        },
    )
    return _session_summary(session)


def get_conversation_session(db: Session, *, session_id: UUID) -> ConversationSession:
    session = conversation_repository.get_session_by_id(db, session_id)
    if session is None:
        raise ConversationNotFoundError("Conversation session not found.")
    return session


def close_conversation_session(db: Session, *, session_id: UUID) -> ConversationSession:
    session = get_conversation_session(db, session_id=session_id)
    conversation_repository.update_session(
        db,
        session,
        {
            "status": ConversationStatus.CLOSED.value,
            "last_message_at": _now(),
        },
    )
    return session
