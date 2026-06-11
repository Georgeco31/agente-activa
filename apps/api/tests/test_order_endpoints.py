from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session


def _create_order(
    client: TestClient,
    *,
    customer_id: str,
    address_id: str,
    items: list[dict],
    notes: str | None = None,
):
    payload = {
        "customer_id": customer_id,
        "address_id": address_id,
        "items": items,
    }
    if notes is not None:
        payload["notes"] = notes
    return client.post("/api/v1/orders", json=payload)


def _assert_dispatch_context(data: dict, customer) -> None:
    assert data["customer_id"] == str(customer.id)
    assert data["address_id"] == str(customer.addresses[0].id)
    assert data["customer"] == {
        "id": str(customer.id),
        "display_name": customer.display_name,
        "primary_phone": (
            next((phone.phone_e164 for phone in customer.phones if phone.is_primary), None)
        ),
    }
    assert data["address"] == {
        "id": str(customer.addresses[0].id),
        "address": customer.addresses[0].address_text,
        "reference": customer.addresses[0].reference,
    }


def test_create_order_with_one_product(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-ONE", price=Decimal("9.50"))

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "2"}],
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == "19.00"
    assert data["order_number"].startswith("ORD-")
    _assert_dispatch_context(data, customer)


def test_create_order_with_multiple_products(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product_one = create_test_product(sku="ORDER-MULTI-1", price=Decimal("5.00"))
    product_two = create_test_product(sku="ORDER-MULTI-2", price=Decimal("7.50"))

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[
            {"product_id": str(product_one.id), "quantity": "2"},
            {"product_id": str(product_two.id), "quantity": "1"},
        ],
    )

    assert response.status_code == 201
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == "17.50"


def test_create_order_uses_product_price_when_unit_price_is_missing(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-PRICE", price=Decimal("8.75"))

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "3"}],
    )

    assert response.status_code == 201
    assert response.json()["items"][0]["unit_price"] == "8.75"
    assert response.json()["items"][0]["line_total"] == "26.25"


def test_create_order_rejects_empty_items(
    client: TestClient, create_test_customer, order_statuses
) -> None:
    customer = create_test_customer(phone=None)

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[],
    )

    assert response.status_code == 422


def test_create_order_rejects_zero_quantity(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-ZERO")

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "0"}],
    )

    assert response.status_code == 422


def test_create_order_rejects_negative_price(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-NEGATIVE")

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1", "unit_price": "-1"}],
    )

    assert response.status_code == 422


def test_create_order_rejects_missing_customer(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    address_owner = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-NO-CUSTOMER")

    response = _create_order(
        client,
        customer_id=str(uuid4()),
        address_id=str(address_owner.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CUSTOMER_NOT_FOUND"
    assert response.json()["error"]["message"] == "Customer not found."


def test_create_order_rejects_missing_address(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-NO-ADDRESS")

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(uuid4()),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ORDER_ADDRESS_NOT_FOUND"
    assert response.json()["error"]["message"] == "Address not found."


def test_create_order_rejects_address_from_another_customer(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(display_name="Cliente Pedido", phone=None)
    other_customer = create_test_customer(display_name="Otro Cliente", phone=None)
    product = create_test_product(sku="ORDER-WRONG-ADDRESS")

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(other_customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ORDER_ADDRESS_NOT_BELONG_TO_CUSTOMER"
    assert response.json()["error"]["message"] == "Address does not belong to customer."


def test_create_order_rejects_missing_product(
    client: TestClient, create_test_customer, order_statuses
) -> None:
    customer = create_test_customer(phone=None)

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(uuid4()), "quantity": "1"}],
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "ORDER_PRODUCT_NOT_FOUND"
    assert response.json()["error"]["message"] == "Product not found."


def test_create_order_rejects_inactive_product(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-INACTIVE", is_active=False)

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "ORDER_PRODUCT_INACTIVE"
    assert response.json()["error"]["message"] == "Inactive products cannot be ordered."


def test_get_order_by_id(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-GET")
    created = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    ).json()

    response = client.get(f"/api/v1/orders/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    _assert_dispatch_context(data, customer)


def test_list_orders(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-LIST")
    created = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    ).json()

    response = client.get("/api/v1/orders")

    assert response.status_code == 200
    orders = response.json()
    assert created["id"] in [order["id"] for order in orders]
    created_order = next(order for order in orders if order["id"] == created["id"])
    _assert_dispatch_context(created_order, customer)


def test_order_returns_null_when_customer_has_no_primary_phone(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone="0999627968")
    customer.phones[0].is_primary = False
    product = create_test_product(sku="ORDER-NO-PRIMARY-PHONE")

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    assert response.status_code == 201
    assert response.json()["customer"]["primary_phone"] is None


def test_list_orders_uses_bounded_queries(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    customer = create_test_customer()
    product = create_test_product(sku="ORDER-QUERY-COUNT")
    _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    connection = db_session.connection()

    def count_list_queries() -> int:
        statements: list[str] = []

        def count_selects(
            _connection,
            _cursor,
            statement,
            _parameters,
            _context,
            _executemany,
        ) -> None:
            if statement.lstrip().upper().startswith("SELECT"):
                statements.append(statement)

        db_session.expire_all()
        event.listen(connection, "before_cursor_execute", count_selects)
        try:
            response = client.get("/api/v1/orders")
        finally:
            event.remove(connection, "before_cursor_execute", count_selects)

        assert response.status_code == 200
        return len(statements)

    single_order_query_count = count_list_queries()

    for index in range(2):
        _create_order(
            client,
            customer_id=str(customer.id),
            address_id=str(customer.addresses[0].id),
            items=[{"product_id": str(product.id), "quantity": str(index + 2)}],
        )

    multiple_orders_query_count = count_list_queries()

    assert single_order_query_count <= 6
    assert multiple_orders_query_count == single_order_query_count


def test_filter_orders_by_customer(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(display_name="Cliente Filtro", phone=None)
    product = create_test_product(sku="ORDER-FILTER-CUSTOMER")
    created = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    ).json()

    response = client.get("/api/v1/orders", params={"customer_id": str(customer.id)})

    assert response.status_code == 200
    assert [order["id"] for order in response.json()] == [created["id"]]


def test_filter_orders_by_status(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-FILTER-STATUS")
    created = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    ).json()

    response = client.get("/api/v1/orders", params={"status_code": "pendiente"})

    assert response.status_code == 200
    assert created["id"] in [order["id"] for order in response.json()]


def test_update_order_status_to_assigned(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-ASSIGN")
    created = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    ).json()

    response = client.patch(
        f"/api/v1/orders/{created['id']}/status",
        json={"status_code": "asignado"},
    )

    assert response.status_code == 200
    assert response.json()["status"]["code"] == "asignado"


def test_cancel_order(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-CANCEL")
    created = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    ).json()

    response = client.patch(f"/api/v1/orders/{created['id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"]["code"] == "cancelado"


def test_initial_order_status_is_pending(
    client: TestClient, create_test_customer, create_test_product, order_statuses
) -> None:
    customer = create_test_customer(phone=None)
    product = create_test_product(sku="ORDER-PENDING")

    response = _create_order(
        client,
        customer_id=str(customer.id),
        address_id=str(customer.addresses[0].id),
        items=[{"product_id": str(product.id), "quantity": "1"}],
    )

    assert response.status_code == 201
    assert response.json()["status"]["code"] == "pendiente"


def test_health_endpoint_still_works(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
