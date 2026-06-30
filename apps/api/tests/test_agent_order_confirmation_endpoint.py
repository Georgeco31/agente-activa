import hashlib
import hmac
import json
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import Order
from app.services.conversations import simulate_conversation_message

AGENT_TOKEN = "test-agent-confirm-token"
AGENT_HEADERS = {"X-Agent-Simulation-Token": AGENT_TOKEN}
WHATSAPP_VERIFY_TOKEN = "test-whatsapp-confirm-verify"
WHATSAPP_APP_SECRET = "test-whatsapp-confirm-secret"


@pytest.fixture(autouse=True)
def configured_agent_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "agent_simulation_token", AGENT_TOKEN)


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def _prepare_ready_session(
    db_session: Session,
    create_test_customer,
    create_test_product,
    *,
    sku: str = "AGENT-ENDPOINT",
):
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku=sku, price=Decimal("3.50"))
    first = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="Quiero un bidon de 20 litros",
    )
    second = simulate_conversation_message(
        db_session,
        phone="+593999627968",
        message="A la direccion de siempre",
    )
    assert second.session.id == first.session.id
    return second.session.id


def _confirm_order(client: TestClient, session_id, *, message: str = "confirmo", headers=None):
    return client.post(
        f"/api/v1/agent/conversations/{session_id}/confirm-order",
        json={"message": message},
        headers=AGENT_HEADERS if headers is None else headers,
    )


def _whatsapp_payload(message: str = "confirmo") -> dict:
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "593999000000",
                                "phone_number_id": "phone-number-id",
                            },
                            "messages": [
                                {
                                    "from": "593999627968",
                                    "id": "wamid.agent-confirm",
                                    "timestamp": "1710000000",
                                    "type": "text",
                                    "text": {"body": message},
                                }
                            ],
                        }
                    }
                ]
            }
        ]
    }


def _signed_whatsapp_headers(raw_body: bytes) -> dict[str, str]:
    digest = hmac.new(WHATSAPP_APP_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={digest}",
    }


def test_confirm_order_endpoint_without_token_does_not_create_order(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session_id = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-ENDPOINT-NO-TOKEN",
    )
    before_count = _order_count(db_session)

    response = _confirm_order(client, session_id, headers={})

    assert response.status_code == 401
    assert _order_count(db_session) == before_count


def test_confirm_order_endpoint_with_invalid_token_does_not_create_order(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session_id = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-ENDPOINT-BAD-TOKEN",
    )
    before_count = _order_count(db_session)

    response = _confirm_order(
        client,
        session_id,
        headers={"X-Agent-Simulation-Token": "wrong-token"},
    )

    assert response.status_code == 401
    assert _order_count(db_session) == before_count
    assert "wrong-token" not in response.text


def test_confirm_order_endpoint_with_valid_token_creates_order(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    session_id = _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-ENDPOINT-CREATE",
    )

    response = _confirm_order(client, session_id, message="si")

    assert response.status_code == 201
    data = response.json()
    assert data["order"]["status"]["code"] == "pendiente"
    assert data["order"]["source_channel"] == "agent_conversation"
    assert data["session"]["status"] == "closed"
    assert data["session"]["extracted_data"]["order_number"] == data["order"]["order_number"]


def test_confirm_order_endpoint_valid_token_does_not_create_when_not_ready(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="AGENT-ENDPOINT-NOT-READY")
    response = client.post(
        "/api/v1/agent/simulate-conversation-message",
        json={"phone": "+593999627968", "message": "Quiero un bidon de 20 litros"},
        headers=AGENT_HEADERS,
    )
    before_count = _order_count(db_session)

    confirm_response = _confirm_order(client, response.json()["session"]["id"], message="si")

    assert confirm_response.status_code == 400
    assert confirm_response.json()["error"]["code"] == "AGENT_ORDER_NOT_READY"
    assert _order_count(db_session) == before_count


def test_whatsapp_webhook_does_not_confirm_order_automatically(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
    monkeypatch,
) -> None:
    _prepare_ready_session(
        db_session,
        create_test_customer,
        create_test_product,
        sku="AGENT-WHATSAPP-NO-CONFIRM",
    )
    monkeypatch.setattr(settings, "whatsapp_webhook_enabled", True)
    monkeypatch.setattr(settings, "whatsapp_webhook_verify_token", WHATSAPP_VERIFY_TOKEN)
    monkeypatch.setattr(settings, "whatsapp_app_secret", WHATSAPP_APP_SECRET)
    raw_body = json.dumps(_whatsapp_payload("confirmo"), separators=(",", ":")).encode()
    before_count = _order_count(db_session)

    response = client.post(
        "/api/v1/whatsapp/webhook",
        content=raw_body,
        headers=_signed_whatsapp_headers(raw_body),
    )

    assert response.status_code == 200
    assert response.json()["outbound_sent"] is False
    assert _order_count(db_session) == before_count


def test_agent_9a_9b_and_whatsapp_9c_endpoints_still_work(
    client: TestClient,
    monkeypatch,
) -> None:
    stateless_response = client.post(
        "/api/v1/agent/simulate-message",
        json={"phone": "+593999627968", "message": "Hola"},
        headers=AGENT_HEADERS,
    )
    conversation_response = client.post(
        "/api/v1/agent/simulate-conversation-message",
        json={"phone": "+593999627968", "message": "Hola"},
        headers=AGENT_HEADERS,
    )
    monkeypatch.setattr(settings, "whatsapp_webhook_enabled", True)
    monkeypatch.setattr(settings, "whatsapp_webhook_verify_token", WHATSAPP_VERIFY_TOKEN)
    verify_response = client.get(
        "/api/v1/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": WHATSAPP_VERIFY_TOKEN,
            "hub.challenge": "ok",
        },
    )

    assert stateless_response.status_code == 200
    assert conversation_response.status_code == 200
    assert verify_response.status_code == 200
    assert verify_response.text == "ok"
