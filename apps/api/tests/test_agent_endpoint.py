from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import Order

AGENT_TOKEN = "test-agent-simulation-token"
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


def _post_simulation(client: TestClient, *, json: dict | None = None, headers=None):
    return client.post(
        "/api/v1/agent/simulate-message",
        json=json or _payload(),
        headers=headers if headers is not None else AGENT_HEADERS,
    )


def _order_count(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(Order)) or 0


def test_simulate_message_endpoint_returns_agent_response(
    client: TestClient,
    create_test_customer,
    create_test_product,
) -> None:
    customer = create_test_customer(phone="0999627968")
    product = create_test_product(
        sku="ENDPOINT-AGENT",
        name="Bidon 20 Litros",
        unit="bidon",
        price=Decimal("3.50"),
    )

    response = _post_simulation(client)

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "create_order"
    assert data["customer"] == {
        "found": True,
        "id": str(customer.id),
        "display_name": customer.display_name,
    }
    assert data["extracted"]["quantity"] == 1
    assert data["extracted"]["product_id"] == str(product.id)
    assert data["extracted"]["product_name"] == "Bidon 20 Litros"
    assert data["extracted"]["product_price"] == "3.50"
    assert data["missing_fields"] == ["address_id"]


def test_simulate_message_requires_token(client: TestClient) -> None:
    response = _post_simulation(client, headers={})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AGENT_SIMULATION_UNAUTHORIZED"


def test_simulate_message_rejects_invalid_token(client: TestClient) -> None:
    response = _post_simulation(
        client,
        headers={"X-Agent-Simulation-Token": "wrong-token"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AGENT_SIMULATION_UNAUTHORIZED"
    assert "wrong-token" not in response.text


def test_simulate_message_fails_closed_without_configured_token(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(settings, "agent_simulation_token", None)

    response = _post_simulation(client)

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "AGENT_SIMULATION_NOT_CONFIGURED"


def test_simulate_message_fails_closed_with_placeholder_token(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "agent_simulation_token",
        "replace-with-agent-simulation-token",
    )

    response = _post_simulation(client)

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "AGENT_SIMULATION_NOT_CONFIGURED"


def test_simulate_message_rejects_invalid_phone(client: TestClient) -> None:
    response = _post_simulation(client, json=_payload(phone="12345"))

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BUSINESS_RULE_ERROR"
    assert "valid Ecuadorian mobile" in response.json()["error"]["message"]


def test_simulate_message_rejects_empty_message(client: TestClient) -> None:
    response = _post_simulation(client, json=_payload(message="   "))

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "BUSINESS_RULE_ERROR"
    assert response.json()["error"]["message"] == "Message is required."


def test_simulate_message_does_not_create_orders(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
) -> None:
    create_test_customer(phone="0999627968")
    create_test_product(sku="ENDPOINT-NO-ORDER", name="Bidon 20 Litros")
    before_count = _order_count(db_session)

    response = _post_simulation(client)

    assert response.status_code == 200
    assert _order_count(db_session) == before_count
