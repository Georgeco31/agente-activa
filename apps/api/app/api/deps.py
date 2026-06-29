from secrets import compare_digest
from typing import Annotated

from fastapi import Depends, Header, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ApiError, ErrorCode
from app.db.session import get_db

DbSession = Annotated[Session, Depends(get_db)]


def _configured_agent_simulation_token() -> str:
    token = settings.agent_simulation_token.strip() if settings.agent_simulation_token else ""
    if not token or "replace-with" in token:
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.AGENT_SIMULATION_NOT_CONFIGURED,
            message="Agent simulation token is not configured.",
        )
    return token


def require_agent_simulation_token(
    x_agent_simulation_token: Annotated[
        str | None,
        Header(alias="X-Agent-Simulation-Token"),
    ] = None,
) -> None:
    configured_token = _configured_agent_simulation_token()
    if not x_agent_simulation_token or not compare_digest(
        x_agent_simulation_token,
        configured_token,
    ):
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.AGENT_SIMULATION_UNAUTHORIZED,
            message="Invalid agent simulation token.",
        )


AgentSimulationAuth = Annotated[None, Depends(require_agent_simulation_token)]
