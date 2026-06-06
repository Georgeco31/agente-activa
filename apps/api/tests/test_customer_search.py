from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.services.customer_search import (
    search_customer_by_phone,
    search_customers,
    search_customers_by_address,
    search_customers_by_alias,
    search_customers_by_name,
    search_customers_by_reference,
)


def test_search_customer_by_normalized_phone(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(phone="0999627968")

    result = search_customer_by_phone(db_session, "0999627968")

    assert result is not None
    assert result.id == customer.id


def test_search_customers_by_normalized_name(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(display_name="Maria Gomez")

    result = search_customers_by_name(db_session, "  MARIA   GOMEZ ")

    assert [item.id for item in result] == [customer.id]


def test_search_customers_by_normalized_alias(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(alias="Dona Maria")

    result = search_customers_by_alias(db_session, "Do\u00f1a Mar\u00eda")

    assert [item.id for item in result] == [customer.id]


def test_search_customers_by_normalized_address(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(address="Calle 10 # 5-20")

    result = search_customers_by_address(db_session, "calle 10 5 20")

    assert [item.id for item in result] == [customer.id]


def test_search_customers_by_normalized_reference(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(reference="Porton Azul")

    result = search_customers_by_reference(db_session, "Port\u00f3n Azul")

    assert [item.id for item in result] == [customer.id]


def test_search_customers_returns_no_results(db_session: Session) -> None:
    assert search_customers_by_name(db_session, "Cliente Inexistente") == []


def test_search_customers_combines_multiple_fields_without_duplicates(
    db_session: Session, create_test_customer
) -> None:
    customer: Customer = create_test_customer(
        display_name="Maria Gomez",
        phone="0999627968",
        alias="Dona Maria",
    )

    result = search_customers(
        db_session,
        phone="0999627968",
        name="Maria Gomez",
        alias="Dona Maria",
    )

    assert [item.id for item in result] == [customer.id]
