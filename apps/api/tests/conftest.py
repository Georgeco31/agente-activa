from collections.abc import Callable, Generator

import pytest
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.customer_alias import CustomerAlias
from app.models.customer_phone import CustomerPhone
from app.services.normalization import normalize_ecuador_phone, normalize_text


@pytest.fixture
def db_session() -> Generator[Session]:
    db = SessionLocal()
    transaction = db.begin()
    try:
        yield db
    finally:
        if transaction.is_active:
            transaction.rollback()
        db.close()


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
