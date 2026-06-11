from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.order import Order

SELECTED_DATE = "2026-06-11"
SELECTED_PERIOD = {"date": SELECTED_DATE, "year": 2026, "month": 6}


def _create_dashboard_order(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
    *,
    suffix: str,
    status_code: str,
    total: Decimal,
    created_at: datetime,
    with_phone: bool = False,
) -> Order:
    customer = create_test_customer(
        display_name=f"Cliente Dashboard {suffix}",
        phone="0999627968" if with_phone else None,
        address=f"Av. Dashboard {suffix}",
        reference=f"Referencia {suffix}",
    )
    product = create_test_product(
        sku=f"DASHBOARD-{suffix}",
        name=f"Producto Dashboard {suffix}",
        price=total,
    )
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": str(customer.id),
            "address_id": str(customer.addresses[0].id),
            "items": [{"product_id": str(product.id), "quantity": "1"}],
        },
    )
    assert response.status_code == 201

    order = db_session.get(Order, UUID(response.json()["id"]))
    assert order is not None
    order.status = order_statuses[status_code]
    order.order_status_id = order_statuses[status_code].id
    order.created_at = created_at
    db_session.flush()
    return order


def test_dashboard_returns_zero_daily_totals_when_no_orders(
    client: TestClient, order_statuses
) -> None:
    response = client.get(
        "/api/v1/dashboard/overview",
        params={"date": "2099-01-15", "year": 2099, "month": 1},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["selected_date"] == "2099-01-15"
    assert data["summary"]["orders_today"] == 0
    assert data["summary"]["sales_total_today"] == "0.00"
    assert data["summary"]["sales_total_month"] == "0.00"
    assert len(data["orders_by_status"]) == 6
    assert all(status["count"] == 0 for status in data["orders_by_status"])
    assert len(data["monthly_sales"]) == 31
    assert data["alerts"] == []


def test_dashboard_sales_only_count_delivered_orders(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    for index, (status_code, total) in enumerate(
        [
            ("entregado", Decimal("12.50")),
            ("pendiente", Decimal("20.00")),
            ("cancelado", Decimal("30.00")),
            ("no_entregado", Decimal("40.00")),
        ]
    ):
        _create_dashboard_order(
            client,
            db_session,
            create_test_customer,
            create_test_product,
            order_statuses,
            suffix=f"SALE-{index}",
            status_code=status_code,
            total=total,
            created_at=datetime(2026, 6, 11, 15, index, tzinfo=UTC),
        )

    response = client.get("/api/v1/dashboard/overview", params=SELECTED_PERIOD)

    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["orders_today"] == 4
    assert summary["delivered_orders"] == 1
    assert summary["pending_orders"] == 1
    assert summary["cancelled_orders"] == 1
    assert summary["not_delivered_orders"] == 1
    assert summary["sales_total_today"] == "12.50"
    assert summary["sales_total_month"] == "12.50"


def test_dashboard_monthly_sales_contains_every_day_and_delivered_totals(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    for suffix, total, created_at in [
        ("MONTH-2", Decimal("8.00"), datetime(2026, 6, 2, 14, tzinfo=UTC)),
        ("MONTH-10", Decimal("17.00"), datetime(2026, 6, 10, 14, tzinfo=UTC)),
        ("OTHER-MONTH", Decimal("99.00"), datetime(2026, 5, 10, 14, tzinfo=UTC)),
    ]:
        _create_dashboard_order(
            client,
            db_session,
            create_test_customer,
            create_test_product,
            order_statuses,
            suffix=suffix,
            status_code="entregado",
            total=total,
            created_at=created_at,
        )

    response = client.get("/api/v1/dashboard/overview", params=SELECTED_PERIOD)

    assert response.status_code == 200
    data = response.json()
    assert len(data["monthly_sales"]) == 30
    assert data["monthly_sales"][1] == {
        "day": 2,
        "date": "2026-06-02",
        "sales_total": "8.00",
        "delivered_orders_count": 1,
    }
    assert data["monthly_sales"][9]["sales_total"] == "17.00"
    assert data["summary"]["sales_total_month"] == "25.00"


def test_dashboard_recent_orders_include_dispatch_information(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    order = _create_dashboard_order(
        client,
        db_session,
        create_test_customer,
        create_test_product,
        order_statuses,
        suffix="RECENT",
        status_code="pendiente",
        total=Decimal("9.75"),
        created_at=datetime(2026, 6, 11, 16, tzinfo=UTC),
        with_phone=True,
    )

    response = client.get("/api/v1/dashboard/overview", params=SELECTED_PERIOD)

    assert response.status_code == 200
    recent_order = next(
        item for item in response.json()["recent_orders"] if item["id"] == str(order.id)
    )
    assert recent_order["customer"]["display_name"] == "Cliente Dashboard RECENT"
    assert recent_order["customer"]["primary_phone"] == "+593999627968"
    assert recent_order["address"]["address"] == "Av. Dashboard RECENT"
    assert recent_order["address"]["reference"] == "Referencia RECENT"
    assert recent_order["status"]["code"] == "pendiente"
    assert recent_order["total"] == "9.75"


def test_dashboard_exposes_operational_alerts(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    _create_dashboard_order(
        client,
        db_session,
        create_test_customer,
        create_test_product,
        order_statuses,
        suffix="ALERT",
        status_code="pendiente",
        total=Decimal("5.00"),
        created_at=datetime(2026, 6, 11, 17, tzinfo=UTC),
    )

    response = client.get("/api/v1/dashboard/overview", params=SELECTED_PERIOD)

    assert response.status_code == 200
    assert response.json()["alerts"] == [
        {
            "code": "pending_orders",
            "label": "Pedidos pendientes",
            "count": 1,
            "severity": "warning",
            "status_code": "pendiente",
        }
    ]


def test_dashboard_uses_bounded_queries(
    client: TestClient,
    db_session: Session,
    create_test_customer,
    create_test_product,
    order_statuses,
) -> None:
    def create_order(suffix: str) -> None:
        _create_dashboard_order(
            client,
            db_session,
            create_test_customer,
            create_test_product,
            order_statuses,
            suffix=suffix,
            status_code="pendiente",
            total=Decimal("6.00"),
            created_at=datetime(2026, 6, 11, 18, tzinfo=UTC),
        )

    def count_dashboard_queries() -> int:
        statements: list[str] = []
        connection = db_session.connection()

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
            response = client.get("/api/v1/dashboard/overview", params=SELECTED_PERIOD)
        finally:
            event.remove(connection, "before_cursor_execute", count_selects)

        assert response.status_code == 200
        return len(statements)

    create_order("QUERY-ONE")
    single_order_query_count = count_dashboard_queries()

    create_order("QUERY-TWO")
    create_order("QUERY-THREE")
    multiple_orders_query_count = count_dashboard_queries()

    assert single_order_query_count <= 8
    assert multiple_orders_query_count == single_order_query_count


def test_dashboard_rejects_invalid_month(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/overview", params={"month": 13})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
