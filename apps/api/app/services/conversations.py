from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.conversation_session import ConversationSession
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
    if extracted_data.get("address_id") is None and extracted_data.get("address_hint") is None:
        missing.append("address_id")
    return missing


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
) -> AgentSimulationResponse:
    return AgentSimulationResponse(
        intent=analysis.intent,
        confidence=analysis.confidence,
        customer=analysis.customer,
        extracted=AgentExtraction(**extracted_data),
        missing_fields=missing_fields,
        reply=analysis.reply,
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
    accumulated_analysis = _analysis_with_accumulated_data(
        analysis,
        extracted_data=extracted_data,
        missing_fields=missing_fields,
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
        message=analysis.reply,
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
