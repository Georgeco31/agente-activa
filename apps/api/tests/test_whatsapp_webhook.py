import hashlib
import hmac
import json
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.conversation_message import ConversationMessage
from app.models.order import Order

WHATSAPP_VERIFY_TOKEN = "test-whatsapp-verify-token"
WHATSAPP_APP_SECRET = "test-whatsapp-app-secret"
AGENT_TOKEN = "test-agent-token"


@pytest.fixture(autouse=True)
def configured_whatsapp_settings(monkeypatch) -> None:
    monkeypatch.setattr(settings, "whatsapp_webhook_enabled", True)
    monkeypatch.setattr(settings, "whatsapp_webhook_verify_token", WHATSAPP_VERIFY_TOKEN)
    monkeypatch.setattr(settings, "whatsapp_app_secret", WHATSAPP_APP_SECRET)


def _json_body(payload: dict) -> bytes:
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _signed_headers(raw_body: bytes, *, secret: str = WHATSAPP_APP_SECRET) -> dict[str, str]:
    digest = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={digest}",
    }


def _text_payload(
    *,
    phone: str = "593999627968",
    message: str = "Hola, quiero un bidon de 20 litros",
    message_id: str = "wamid.test-text",
) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "waba-test-id",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "593999000000",
                                "phone_number_id": "phone-number-id",
                            },
                            "messages": [
                                {
                                    "from": phone,
                                    "id": message_id,
                                    "timestamp": "1710000000",
                                    "type": "text",
                                    "text": {"body": message},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def _unsupported_payload(
    *,
    phone: str = "593999627968",
    message_type: str = "image",
) -> dict:
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "waba-test-id",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "593999000000",
                                "phone_number_id": "phone-number-id",
                            },
                            "messages": [
                                {
                                    "from": phone,
                                    "id": "wamid.test-unsupported",
                                    "timestamp": "1710000001",
                                    "type": message_type,
                                    message_type: {"id": "media-id"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


def _post_signed_webhook(client: TestClient, payload: dict):
    raw_body = _json_body(payload)
    return client.post(
        "/api/v1/whatsapp/webhook",
        content=raw_body,
        headers=_signed_headers(raw_body),
    )


def _message_count(db_session: Session, session_id: UUID) -> int:
    return (
        db_session.scalar(
            select(func.count())
            .select_from(ConversationMessage)
            .where(ConversationMessage.session_id == session_id)
        )
        or 0
    )


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def test_get_webhook_with_valid_verify_token_returns_challenge(client: TestClient) -> None:
    response = client.get(
        "/api/v1/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": WHATSAPP_VERIFY_TOKEN,
            "hub.challenge": "challenge-123",
        },
    )

    assert response.status_code == 200
    assert response.text == "challenge-123"
    assert response.headers["content-type"].startswith("text/plain")


def test_get_webhook_with_invalid_verify_token_returns_403(client: TestClient) -> None:
    response = client.get(
        "/api/v1/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "challenge-123",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "WHATSAPP_WEBHOOK_FORBIDDEN"
    assert WHATSAPP_VERIFY_TOKEN not in response.text
    assert "wrong-token" not in response.text


def test_get_webhook_disabled_fails_closed(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(settings, "whatsapp_webhook_enabled", False)

    response = client.get(
        "/api/v1/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": WHATSAPP_VERIFY_TOKEN,
            "hub.challenge": "challenge-123",
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "WHATSAPP_WEBHOOK_DISABLED"


def test_post_webhook_without_signature_rejects(client: TestClient) -> None:
    response = client.post(
        "/api/v1/whatsapp/webhook",
        content=_json_body(_text_payload()),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "WHATSAPP_WEBHOOK_UNAUTHORIZED"


def test_post_webhook_with_invalid_signature_rejects(client: TestClient) -> None:
    raw_body = _json_body(_text_payload())
    response = client.post(
        "/api/v1/whatsapp/webhook",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "WHATSAPP_WEBHOOK_UNAUTHORIZED"


def test_post_webhook_with_valid_signature_processes_text_message(
    client: TestClient,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="WHATSAPP-TEXT")

    response = _post_signed_webhook(client, _text_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["processed_messages"] == 1
    assert data["unsupported_messages"] == 0
    assert data["outbound_sent"] is False
    assert len(data["session_ids"]) == 1


def test_post_text_message_creates_and_reuses_conversation(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="WHATSAPP-REUSE")

    first_response = _post_signed_webhook(
        client,
        _text_payload(message="Hola", message_id="wamid.first"),
    )
    second_response = _post_signed_webhook(
        client,
        _text_payload(message="Quiero un bidon de 20 litros", message_id="wamid.second"),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    first_session_id = first_response.json()["session_ids"][0]
    second_session_id = second_response.json()["session_ids"][0]
    assert second_session_id == first_session_id
    assert _message_count(db_session, UUID(first_session_id)) == 4


def test_post_unsupported_message_type_does_not_break(
    client: TestClient,
    db_session: Session,
) -> None:
    response = _post_signed_webhook(client, _unsupported_payload(message_type="image"))

    assert response.status_code == 200
    data = response.json()
    assert data["processed_messages"] == 0
    assert data["unsupported_messages"] == 1
    assert data["outbound_sent"] is False

    session_id = UUID(data["session_ids"][0])
    message = db_session.scalar(
        select(ConversationMessage).where(ConversationMessage.session_id == session_id)
    )
    assert message is not None
    assert message.intent == "unknown"
    assert message.message_metadata["unsupported_message_type"] == "image"
    assert message.message_metadata["provider"]["provider_message_id"] == "wamid.test-unsupported"


def test_post_webhook_does_not_create_orders(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="WHATSAPP-NO-ORDER")
    before_count = _order_count(db_session)

    response = _post_signed_webhook(client, _text_payload())

    assert response.status_code == 200
    assert _order_count(db_session) == before_count


def test_post_webhook_does_not_send_real_messages(
    client: TestClient,
    create_test_customer,
) -> None:
    create_test_customer(phone="0999627968")

    response = _post_signed_webhook(client, _text_payload(message="Hola"))

    assert response.status_code == 200
    assert response.json()["outbound_sent"] is False


def test_webhook_errors_do_not_expose_secrets(client: TestClient) -> None:
    raw_body = _json_body(_text_payload())
    response = client.post(
        "/api/v1/whatsapp/webhook",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 401
    assert WHATSAPP_APP_SECRET not in response.text
    assert WHATSAPP_VERIFY_TOKEN not in response.text
    assert "sha256=invalid" not in response.text


def test_whatsapp_webhook_does_not_break_agent_endpoints(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "agent_simulation_token", AGENT_TOKEN)
    headers = {"X-Agent-Simulation-Token": AGENT_TOKEN}

    stateless_response = client.post(
        "/api/v1/agent/simulate-message",
        json={"phone": "+593999627968", "message": "Hola"},
        headers=headers,
    )
    conversation_response = client.post(
        "/api/v1/agent/simulate-conversation-message",
        json={"phone": "+593999627968", "message": "Hola"},
        headers=headers,
    )

    assert stateless_response.status_code == 200
    assert conversation_response.status_code == 200
