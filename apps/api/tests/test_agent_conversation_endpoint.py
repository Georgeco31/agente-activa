from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import Order

AGENT_TOKEN = "test-agent-conversation-token"
AGENT_HEADERS = {"X-Agent-Simulation-Token": AGENT_TOKEN}


@pytest.fixture(autouse=True)
def configured_agent_token(monkeypatch) -> None:
    monkeypatch.setattr(settings, "agent_simulation_token", AGENT_TOKEN)


def _payload(
    *,
    phone: str = "+593999627968",
    message: str = "Hola, quiero un bidon de 20 litros",
) -> dict:
    return {"phone": phone, "message": message}


def _post_conversation(client: TestClient, *, json: dict | None = None, headers=None):
    return client.post(
        "/api/v1/agent/simulate-conversation-message",
        json=json or _payload(),
        headers=headers if headers is not None else AGENT_HEADERS,
    )


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def test_simulate_conversation_endpoint_with_valid_token(
    client: TestClient,
    create_test_customer,
    create_test_product,
) -> None:
    customer = create_test_customer(phone="0999627968")
    product = create_test_product(
        name="Bidon 20 Litros",
        sku="CONV-ENDPOINT",
        price=Decimal("3.50"),
    )

    response = _post_conversation(client)

    assert response.status_code == 200
    data = response.json()
    assert data["session"]["status"] == "waiting_for_customer"
    assert data["session"]["current_intent"] == "create_order"
    assert data["analysis"]["customer"]["id"] == str(customer.id)
    assert data["analysis"]["extracted"]["quantity"] == 1
    assert data["analysis"]["extracted"]["product_id"] == str(product.id)
    assert data["analysis"]["missing_fields"] == ["address_id"]


def test_simulate_conversation_endpoint_requires_token(client: TestClient) -> None:
    response = _post_conversation(client, headers={})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AGENT_SIMULATION_UNAUTHORIZED"


def test_simulate_conversation_endpoint_rejects_invalid_token(client: TestClient) -> None:
    response = _post_conversation(
        client,
        headers={"X-Agent-Simulation-Token": "wrong-token"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AGENT_SIMULATION_UNAUTHORIZED"
    assert "wrong-token" not in response.text


def test_get_conversation_endpoint_returns_session_messages(
    client: TestClient,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="CONV-GET")
    created = _post_conversation(client).json()

    response = client.get(
        f"/api/v1/agent/conversations/{created['session']['id']}",
        headers=AGENT_HEADERS,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["session"]["id"]
    assert data["status"] == "waiting_for_customer"
    assert data["extracted_data"]["quantity"] == 1
    assert [message["direction"] for message in data["messages"]] == [
        "inbound",
        "outbound",
    ]


def test_close_conversation_endpoint_marks_session_closed(
    client: TestClient,
    create_test_customer,
) -> None:
    create_test_customer(phone="0999627968")
    created = _post_conversation(client, json=_payload(message="Hola")).json()

    response = client.post(
        f"/api/v1/agent/conversations/{created['session']['id']}/close",
        headers=AGENT_HEADERS,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "closed"


def test_new_endpoint_message_after_close_creates_new_session(
    client: TestClient,
    create_test_customer,
) -> None:
    create_test_customer(phone="0999627968")
    first = _post_conversation(client, json=_payload(message="Hola")).json()
    close_response = client.post(
        f"/api/v1/agent/conversations/{first['session']['id']}/close",
        headers=AGENT_HEADERS,
    )
    assert close_response.status_code == 200

    second = _post_conversation(client, json=_payload(message="Hola de nuevo")).json()

    assert second["session"]["id"] != first["session"]["id"]


def test_conversation_endpoint_accumulates_data_between_messages(
    client: TestClient,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    product = create_test_product(name="Bidon 20 Litros", sku="CONV-ENDPOINT-ACC")
    first = _post_conversation(
        client,
        json=_payload(message="Quiero dos bidones de 20 litros"),
    ).json()

    second_response = _post_conversation(
        client,
        json=_payload(message="A la direccion de siempre"),
    )

    assert second_response.status_code == 200
    second = second_response.json()
    assert second["session"]["id"] == first["session"]["id"]
    assert second["session"]["status"] == "ready_for_confirmation"
    assert second["analysis"]["extracted"]["quantity"] == 2
    assert second["analysis"]["extracted"]["product_id"] == str(product.id)
    assert second["analysis"]["extracted"]["address_hint"] == "de siempre"
    assert second["analysis"]["missing_fields"] == []


def test_conversation_endpoint_does_not_create_orders(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(name="Bidon 20 Litros", sku="CONV-ENDPOINT-NO-ORDER")
    before_count = _order_count(db_session)

    response = _post_conversation(client)

    assert response.status_code == 200
    assert _order_count(db_session) == before_count
