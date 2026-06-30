from typing import Annotated

from fastapi import APIRouter, Query, Request, status
from fastapi.responses import PlainTextResponse

from app.api.deps import DbSession
from app.core.exceptions import ApiError, ErrorCode
from app.services.whatsapp import (
    process_whatsapp_webhook_payload,
    verify_whatsapp_webhook_challenge,
)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


@router.get("/webhook", response_class=PlainTextResponse)
def verify_whatsapp_webhook_endpoint(
    hub_mode: Annotated[str | None, Query(alias="hub.mode")] = None,
    hub_verify_token: Annotated[str | None, Query(alias="hub.verify_token")] = None,
    hub_challenge: Annotated[str | None, Query(alias="hub.challenge")] = None,
) -> PlainTextResponse:
    challenge = verify_whatsapp_webhook_challenge(
        hub_mode=hub_mode,
        hub_verify_token=hub_verify_token,
        hub_challenge=hub_challenge,
    )
    return PlainTextResponse(challenge)


@router.post("/webhook")
async def receive_whatsapp_webhook_endpoint(
    request: Request,
    db: DbSession,
):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256")

    try:
        response = process_whatsapp_webhook_payload(
            db,
            raw_body=raw_body,
            signature_header=signature,
        )
        db.commit()
        return response
    except ApiError:
        db.rollback()
        raise
    except ValueError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc
