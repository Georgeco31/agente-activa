from collections.abc import Callable, Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.session import engine
from app.main import app
from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.customer_alias import CustomerAlias
from app.models.customer_phone import CustomerPhone
from app.models.order_status import OrderStatus
from app.models.product import Product
from app.seeds.order_statuses import BASE_ORDER_STATUSES
from app.services.normalization import normalize_ecuador_phone, normalize_text


@pytest.fixture
def db_session() -> Generator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def non_raising_client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_test_customer(db_session: Session) -> Callable[..., Customer]:
    def _create_test_customer(
        *,
        display_name: str = "Maria Gomez",
        phone: str | None = "0999627968",
        alias: str | None = "Dona Maria",
        address: str | None = "Calle 10 # 5-20",
        reference: str | None = "Porton Azul",
    ) -> Customer:
        customer = Customer(
            display_name=display_name,
            normalized_name=normalize_text(display_name),
            customer_type="persona",
            status="activo",
        )

        if phone is not None:
            normalized_phone = normalize_ecuador_phone(phone)
            customer.phones.append(
                CustomerPhone(
                    phone_e164=normalized_phone,
                    normalized_phone=normalized_phone,
                    raw_phone=phone,
                    label="whatsapp",
                    is_primary=True,
                    is_whatsapp=True,
                )
            )

        if alias is not None:
            customer.aliases.append(
                CustomerAlias(
                    alias=alias,
                    normalized_alias=normalize_text(alias),
                    source="test",
                )
            )

        if address is not None:
            customer.addresses.append(
                CustomerAddress(
                    label="casa",
                    address_text=address,
                    normalized_address=normalize_text(address),
                    reference=reference,
                    normalized_reference=normalize_text(reference),
                    is_primary=True,
                )
            )

        db_session.add(customer)
        db_session.flush()
        return customer

    return _create_test_customer


@pytest.fixture
def create_test_product(db_session: Session) -> Callable[..., Product]:
    def _create_test_product(
        *,
        sku: str = "TEST-PRODUCT",
        name: str = "Producto de Prueba",
        unit: str = "unidad",
        price: Decimal = Decimal("10.00"),
        is_active: bool = True,
    ) -> Product:
        product = Product(
            sku=sku,
            name=name,
            normalized_name=normalize_text(name),
            unit=unit,
            price=price,
            is_active=is_active,
        )
        db_session.add(product)
        db_session.flush()
        return product

    return _create_test_product


@pytest.fixture
def order_statuses(db_session: Session) -> dict[str, OrderStatus]:
    statuses: dict[str, OrderStatus] = {}
    for status_data in BASE_ORDER_STATUSES:
        order_status = db_session.scalar(
            select(OrderStatus).where(OrderStatus.code == status_data["code"])
        )
        if order_status is None:
            order_status = OrderStatus(**status_data)
            db_session.add(order_status)
            db_session.flush()
        statuses[order_status.code] = order_status
    return statuses
