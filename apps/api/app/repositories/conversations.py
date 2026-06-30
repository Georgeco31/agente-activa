from collections.abc import Iterable, Mapping
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.conversation_message import ConversationMessage
from app.models.conversation_session import ConversationSession


def _session_load_options():
    return (
        selectinload(ConversationSession.messages),
        selectinload(ConversationSession.customer),
    )


def get_session_by_id(db: Session, session_id: UUID) -> ConversationSession | None:
    statement = (
        select(ConversationSession)
        .options(*_session_load_options())
        .where(ConversationSession.id == session_id)
    )
    return db.scalar(statement)


def find_latest_session_by_phone_and_statuses(
    db: Session,
    *,
    normalized_phone: str,
    statuses: Iterable[str],
) -> ConversationSession | None:
    statement = (
        select(ConversationSession)
        .options(*_session_load_options())
        .where(
            ConversationSession.normalized_phone == normalized_phone,
            ConversationSession.status.in_(list(statuses)),
        )
        .order_by(ConversationSession.last_message_at.desc())
    )
    return db.scalars(statement).unique().first()


def create_session(
    db: Session,
    *,
    phone: str,
    normalized_phone: str,
    customer_id: UUID | None,
    status: str,
    current_intent: str | None,
    extracted_data: dict[str, Any],
    missing_fields: list[str],
) -> ConversationSession:
    session = ConversationSession(
        phone=phone,
        normalized_phone=normalized_phone,
        customer_id=customer_id,
        status=status,
        current_intent=current_intent,
        extracted_data=extracted_data,
        missing_fields=missing_fields,
    )
    db.add(session)
    db.flush()
    return session


def update_session(
    db: Session,
    session: ConversationSession,
    values: Mapping[str, Any],
) -> ConversationSession:
    for field_name, value in values.items():
        setattr(session, field_name, value)
    db.flush()
    return session


def create_message(
    db: Session,
    *,
    session_id: UUID,
    direction: str,
    phone: str,
    message: str,
    intent: str | None = None,
    confidence: Decimal | None = None,
    message_metadata: dict[str, Any] | None = None,
) -> ConversationMessage:
    conversation_message = ConversationMessage(
        session_id=session_id,
        direction=direction,
        phone=phone,
        message=message,
        intent=intent,
        confidence=confidence,
        message_metadata=message_metadata,
        created_at=datetime.now(UTC),
    )
    db.add(conversation_message)
    db.flush()
    return conversation_message
