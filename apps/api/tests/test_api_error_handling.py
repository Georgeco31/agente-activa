from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1 import products as products_api


def _assert_error(response, *, status_code: int, code: str) -> dict:
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "details"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str)
    assert isinstance(body["error"]["details"], dict)
    return body["error"]


def _create_product(client: TestClient, *, sku: str) -> dict:
    response = client.post(
        "/api/v1/products",
        json={
            "sku": sku,
            "name": f"Producto {sku}",
            "unit": "unidad",
            "price": "5.00",
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_order(
    client: TestClient,
    *,
    customer_id: str,
    address_id: str,
    product_id: str,
) -> dict:
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "address_id": address_id,
            "items": [{"product_id": product_id, "quantity": "1"}],
        },
    )
    assert response.status_code == 201
    return response.json()


def test_missing_customer_returns_uniform_not_found_error(client: TestClient) -> None:
    response = client.get(f"/api/v1/customers/{uuid4()}")

    _assert_error(response, status_code=404, code="CUSTOMER_NOT_FOUND")


def test_customer_duplicate_candidate_returns_uniform_conflict(
    client: TestClient,
    create_test_customer,
) -> None:
    customer = create_test_customer(phone="0999627968")

    response = client.post(
        "/api/v1/customers",
        json={"display_name": "Cliente Duplicado", "phone": "+593999627968"},
    )

    error = _assert_error(
        response,
        status_code=409,
        code="CUSTOMER_DUPLICATE_CANDIDATE_FOUND",
    )
    assert error["details"]["duplicate_candidates"][0]["customer_id"] == str(customer.id)


def test_duplicate_customer_phone_returns_uniform_conflict(
    client: TestClient,
    create_test_customer,
) -> None:
    create_test_customer(phone="0999627968")
    other_customer = create_test_customer(display_name="Otro Cliente", phone=None)

    response = client.post(
        f"/api/v1/customers/{other_customer.id}/phones",
        json={"phone": "+593999627968"},
    )

    _assert_error(response, status_code=409, code="CUSTOMER_PHONE_ALREADY_EXISTS")


def test_missing_product_returns_uniform_not_found_error(client: TestClient) -> None:
    response = client.get(f"/api/v1/products/{uuid4()}")

    _assert_error(response, status_code=404, code="PRODUCT_NOT_FOUND")


def test_duplicate_product_sku_returns_uniform_conflict(client: TestClient) -> None:
    _create_product(client, sku="ERROR-DUPLICATE")

    response = client.post(
        "/api/v1/products",
        json={
            "sku": "ERROR-DUPLICATE",
            "name": "Producto Repetido",
            "unit": "unidad",
            "price": "8.00",
        },
    )

    _assert_error(response, status_code=409, code="PRODUCT_SKU_ALREADY_EXISTS")


def test_negative_product_price_returns_uniform_validation_error(client: TestClient) -> None:
    response = client.post(
        "/api/v1/products",
        json={
            "sku": "ERROR-NEGATIVE",
            "name": "Producto Invalido",
            "unit": "unidad",
            "price": "-1.00",
        },
    )

    error = _assert_error(response, status_code=422, code="VALIDATION_ERROR")
    assert error["details"]["errors"]


def test_missing_order_returns_uniform_not_found_error(client: TestClient) -> None:
    response = client.get(f"/api/v1/orders/{uuid4()}")

    _assert_error(response, status_code=404, code="ORDER_NOT_FOUND")


def test_order_with_missing_customer_returns_clear_error(
    client: TestClient,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    address_owner = create_test_customer(phone=None)
    product = create_test_product(sku="ERROR-NO-CUSTOMER")

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(uuid4()),
            "address_id": str(address_owner.addresses[0].id),
            "items": [{"product_id": str(product.id), "quantity": "1"}],
        },
    )

    _assert_error(response, status_code=404, code="CUSTOMER_NOT_FOUND")


def test_order_with_missing_product_returns_clear_error(
    client: TestClient,
    create_test_customer,
    order_statuses,
) -> None:
    customer = create_test_customer(phone=None)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(customer.id),
            "address_id": str(customer.addresses[0].id),
            "items": [{"product_id": str(uuid4()), "quantity": "1"}],
        },
    )

    _assert_error(response, status_code=404, code="ORDER_PRODUCT_NOT_FOUND")


def test_order_with_inactive_product_returns_clear_error(
    client: TestClient,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ERROR-INACTIVE", is_active=False)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(customer.id),
            "address_id": str(customer.addresses[0].id),
            "items": [{"product_id": str(product.id), "quantity": "1"}],
        },
    )

    _assert_error(response, status_code=400, code="ORDER_PRODUCT_INACTIVE")


def test_order_with_address_from_another_customer_returns_clear_error(
    client: TestClient,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    customer = create_test_customer(display_name="Cliente Pedido", phone=None)
    other_customer = create_test_customer(display_name="Otro Cliente", phone=None)
    product = create_test_product(sku="ERROR-WRONG-ADDRESS")

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(customer.id),
            "address_id": str(other_customer.addresses[0].id),
            "items": [{"product_id": str(product.id), "quantity": "1"}],
        },
    )

    _assert_error(
        response,
        status_code=400,
        code="ORDER_ADDRESS_NOT_BELONG_TO_CUSTOMER",
    )


def test_unknown_order_status_returns_clear_error(
    client: TestClient,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ERROR-STATUS", price=Decimal("5.00"))
    order = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        product_id=str(product.id),
    )

    response = client.patch(
        f"/api/v1/orders/{order['id']}/status",
        json={"status_code": "estado_inexistente"},
    )

    _assert_error(response, status_code=404, code="ORDER_STATUS_NOT_FOUND")


def test_invalid_payload_returns_uniform_validation_error(client: TestClient) -> None:
    response = client.post("/api/v1/orders", json={})

    error = _assert_error(response, status_code=422, code="VALIDATION_ERROR")
    assert len(error["details"]["errors"]) >= 3


def test_unexpected_error_is_safe(
    non_raising_client: TestClient,
    monkeypatch,
) -> None:
    def raise_unexpected_error(*_args, **_kwargs):
        raise RuntimeError("secret-token-must-not-leak")

    monkeypatch.setattr(products_api, "list_products", raise_unexpected_error)

    response = non_raising_client.get("/api/v1/products")

    error = _assert_error(response, status_code=500, code="INTERNAL_SERVER_ERROR")
    assert error["message"] == "Internal server error."
    assert "secret-token-must-not-leak" not in response.text


def test_health_endpoint_still_works(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
