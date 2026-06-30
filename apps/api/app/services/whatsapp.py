from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from secrets import compare_digest
from string import hexdigits
from typing import Any

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ApiError, ErrorCode
from app.services.conversations import (
    record_unsupported_conversation_message,
    simulate_conversation_message,
)


@dataclass(frozen=True)
class WhatsAppInboundMessage:
    phone: str
    message_id: str | None
    timestamp: str | None
    message_type: str | None
    text_body: str | None
    provider_metadata: dict[str, Any]


def _is_placeholder(value: str | None) -> bool:
    normalized_value = value.strip().lower() if value else ""
    return (
        not normalized_value
        or "replace-with" in normalized_value
        or "placeholder" in normalized_value
    )


def _ensure_webhook_enabled() -> None:
    if not settings.whatsapp_webhook_enabled:
        raise ApiError(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.WHATSAPP_WEBHOOK_DISABLED,
            message="WhatsApp webhook is not enabled.",
        )


def _configured_verify_token() -> str:
    token = settings.whatsapp_webhook_verify_token
    if _is_placeholder(token):
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.WHATSAPP_WEBHOOK_NOT_CONFIGURED,
            message="WhatsApp webhook verify token is not configured.",
        )
    return token.strip()


def _configured_app_secret() -> str:
    secret = settings.whatsapp_app_secret
    if _is_placeholder(secret):
        raise ApiError(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=ErrorCode.WHATSAPP_WEBHOOK_NOT_CONFIGURED,
            message="WhatsApp app secret is not configured.",
        )
    return secret.strip()


def verify_whatsapp_webhook_challenge(
    *,
    hub_mode: str | None,
    hub_verify_token: str | None,
    hub_challenge: str | None,
) -> str:
    _ensure_webhook_enabled()
    configured_token = _configured_verify_token()
    if (
        hub_mode != "subscribe"
        or not hub_verify_token
        or not hub_challenge
        or not compare_digest(hub_verify_token, configured_token)
    ):
        raise ApiError(
            status_code=status.HTTP_403_FORBIDDEN,
            code=ErrorCode.WHATSAPP_WEBHOOK_FORBIDDEN,
            message="WhatsApp webhook verification failed.",
        )
    return hub_challenge


def _validate_signature(*, raw_body: bytes, signature_header: str | None) -> None:
    _ensure_webhook_enabled()
    app_secret = _configured_app_secret()
    if not signature_header or not signature_header.startswith("sha256="):
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.WHATSAPP_WEBHOOK_UNAUTHORIZED,
            message="Invalid WhatsApp webhook signature.",
        )

    received_digest = signature_header.removeprefix("sha256=")
    has_invalid_digest = len(received_digest) != 64 or any(
        character not in hexdigits for character in received_digest
    )
    if has_invalid_digest:
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.WHATSAPP_WEBHOOK_UNAUTHORIZED,
            message="Invalid WhatsApp webhook signature.",
        )

    expected_digest = hmac.new(
        app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()
    if not compare_digest(received_digest, expected_digest):
        raise ApiError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code=ErrorCode.WHATSAPP_WEBHOOK_UNAUTHORIZED,
            message="Invalid WhatsApp webhook signature.",
        )


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _parse_whatsapp_messages(payload: dict[str, Any]) -> list[WhatsAppInboundMessage]:
    inbound_messages: list[WhatsAppInboundMessage] = []
    for entry in _as_list(payload.get("entry")):
        for change in _as_list(_as_dict(entry).get("changes")):
            value = _as_dict(_as_dict(change).get("value"))
            metadata = _as_dict(value.get("metadata"))
            provider_base_metadata = {
                "provider": "whatsapp",
                "messaging_product": value.get("messaging_product"),
                "phone_number_id": metadata.get("phone_number_id"),
                "display_phone_number": metadata.get("display_phone_number"),
            }

            for message in _as_list(value.get("messages")):
                message_data = _as_dict(message)
                message_type = message_data.get("type")
                text_data = _as_dict(message_data.get("text"))
                text_body = text_data.get("body") if message_type == "text" else None
                provider_metadata = {
                    **provider_base_metadata,
                    "provider_message_id": message_data.get("id"),
                    "provider_timestamp": message_data.get("timestamp"),
                    "message_type": message_type,
                }
                inbound_messages.append(
                    WhatsAppInboundMessage(
                        phone=str(message_data.get("from") or ""),
                        message_id=message_data.get("id"),
                        timestamp=message_data.get("timestamp"),
                        message_type=message_type,
                        text_body=text_body,
                        provider_metadata=provider_metadata,
                    )
                )
    return inbound_messages


def _load_signed_payload(raw_body: bytes, signature_header: str | None) -> dict[str, Any]:
    _validate_signature(raw_body=raw_body, signature_header=signature_header)
    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message="Invalid WhatsApp webhook payload.",
        ) from exc
    return _as_dict(payload)


def process_whatsapp_webhook_payload(
    db: Session,
    *,
    raw_body: bytes,
    signature_header: str | None,
) -> dict[str, Any]:
    payload = _load_signed_payload(raw_body, signature_header)
    inbound_messages = _parse_whatsapp_messages(payload)
    processed_messages = 0
    unsupported_messages = 0
    ignored_messages = 0
    session_ids: list[str] = []

    for inbound_message in inbound_messages:
        phone = inbound_message.phone.strip()
        text_body = inbound_message.text_body.strip() if inbound_message.text_body else ""
        if inbound_message.message_type == "text" and text_body:
            response = simulate_conversation_message(
                db,
                phone=phone,
                message=text_body,
                provider_metadata=inbound_message.provider_metadata,
            )
            session_ids.append(str(response.session.id))
            processed_messages += 1
            continue

        if phone:
            session = record_unsupported_conversation_message(
                db,
                phone=phone,
                message_type=inbound_message.message_type,
                provider_metadata=inbound_message.provider_metadata,
            )
            session_ids.append(str(session.id))
            unsupported_messages += 1
        else:
            ignored_messages += 1

    return {
        "status": "ok",
        "processed_messages": processed_messages,
        "unsupported_messages": unsupported_messages,
        "ignored_messages": ignored_messages,
        "session_ids": session_ids,
        "outbound_sent": False,
    }
