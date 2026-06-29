from fastapi import APIRouter, status

from app.api.deps import AgentSimulationAuth, DbSession
from app.core.exceptions import ApiError, ErrorCode
from app.schemas.agent import AgentSimulationRequest, AgentSimulationResponse
from app.services.agent import simulate_agent_message

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
