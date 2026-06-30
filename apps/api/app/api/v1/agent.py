from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import AgentSimulationAuth, DbSession
from app.core.exceptions import ApiError, ErrorCode
from app.schemas.agent import (
    AgentConversationSessionDetail,
    AgentConversationSimulationResponse,
    AgentSimulationRequest,
    AgentSimulationResponse,
)
from app.services.agent import simulate_agent_message
from app.services.conversations import (
    ConversationNotFoundError,
    close_conversation_session,
    get_conversation_session,
    simulate_conversation_message,
)

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/simulate-message", response_model=AgentSimulationResponse)
def simulate_message_endpoint(
    payload: AgentSimulationRequest,
    db: DbSession,
    _auth: AgentSimulationAuth,
):
    try:
        return simulate_agent_message(
            db,
            phone=payload.phone,
            message=payload.message,
        )
    except ValueError as exc:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc


@router.post(
    "/simulate-conversation-message",
    response_model=AgentConversationSimulationResponse,
)
def simulate_conversation_message_endpoint(
    payload: AgentSimulationRequest,
    db: DbSession,
    _auth: AgentSimulationAuth,
):
    try:
        response = simulate_conversation_message(
            db,
            phone=payload.phone,
            message=payload.message,
        )
        db.commit()
        return response
    except ValueError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc


@router.get(
    "/conversations/{session_id}",
    response_model=AgentConversationSessionDetail,
)
def get_conversation_endpoint(
    session_id: UUID,
    db: DbSession,
    _auth: AgentSimulationAuth,
):
    try:
        return get_conversation_session(db, session_id=session_id)
    except ConversationNotFoundError as exc:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CONVERSATION_SESSION_NOT_FOUND,
            message=str(exc),
        ) from exc


@router.post(
    "/conversations/{session_id}/close",
    response_model=AgentConversationSessionDetail,
)
def close_conversation_endpoint(
    session_id: UUID,
    db: DbSession,
    _auth: AgentSimulationAuth,
):
    try:
        session = close_conversation_session(db, session_id=session_id)
        db.commit()
        db.refresh(session)
        return session
    except ConversationNotFoundError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CONVERSATION_SESSION_NOT_FOUND,
            message=str(exc),
        ) from exc
