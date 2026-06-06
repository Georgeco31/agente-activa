from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories import customers as customer_repository
from app.services.normalization import normalize_ecuador_phone, normalize_text


def _unique_customers(customers: Iterable[Customer]) -> list[Customer]:
    unique: dict[str, Customer] = {}
    for customer in customers:
        unique[str(customer.id)] = customer
    return list(unique.values())


def search_customer_by_phone(db: Session, phone: str) -> Customer | None:
    normalized_phone = normalize_ecuador_phone(phone)
    return customer_repository.find_customer_by_normalized_phone(db, normalized_phone)


def search_customers_by_name(db: Session, name: str) -> list[Customer]:
    normalized_name = normalize_text(name)
    if not normalized_name:
        return []
    return customer_repository.find_customers_by_normalized_name(db, normalized_name)


def search_customers_by_alias(db: Session, alias: str) -> list[Customer]:
    normalized_alias = normalize_text(alias)
    if not normalized_alias:
        return []
    return customer_repository.find_customers_by_normalized_alias(db, normalized_alias)


def search_customers_by_address(db: Session, address: str) -> list[Customer]:
    normalized_address = normalize_text(address)
    if not normalized_address:
        return []
    return customer_repository.find_customers_by_normalized_address(db, normalized_address)


def search_customers_by_reference(db: Session, reference: str) -> list[Customer]:
    normalized_reference = normalize_text(reference)
    if not normalized_reference:
        return []
    return customer_repository.find_customers_by_normalized_reference(db, normalized_reference)


def search_customers(
    db: Session,
    *,
    phone: str | None = None,
    name: str | None = None,
    alias: str | None = None,
    address: str | None = None,
    reference: str | None = None,
) -> list[Customer]:
    matches: list[Customer] = []

    if phone:
        customer = search_customer_by_phone(db, phone)
        if customer is not None:
            matches.append(customer)

    if name:
        matches.extend(search_customers_by_name(db, name))

    if alias:
        matches.extend(search_customers_by_alias(db, alias))

    if address:
        matches.extend(search_customers_by_address(db, address))

    if reference:
        matches.extend(search_customers_by_reference(db, reference))

    return _unique_customers(matches)
