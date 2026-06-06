from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.customer_alias import CustomerAlias
from app.models.customer_phone import CustomerPhone


def get_customer_by_id(db: Session, customer_id: UUID) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.id == customer_id))


def find_customer_by_normalized_phone(db: Session, normalized_phone: str) -> Customer | None:
    statement = (
        select(Customer)
        .join(CustomerPhone)
        .where(CustomerPhone.normalized_phone == normalized_phone)
    )
    return db.scalars(statement).unique().first()


def find_customers_by_normalized_name(db: Session, normalized_name: str) -> list[Customer]:
    statement = select(Customer).where(Customer.normalized_name == normalized_name)
    return list(db.scalars(statement).unique().all())


def find_customers_by_normalized_alias(db: Session, normalized_alias: str) -> list[Customer]:
    statement = (
        select(Customer)
        .join(CustomerAlias)
        .where(CustomerAlias.normalized_alias == normalized_alias)
    )
    return list(db.scalars(statement).unique().all())


def find_customers_by_normalized_address(
    db: Session, normalized_address: str
) -> list[Customer]:
    statement = (
        select(Customer)
        .join(CustomerAddress)
        .where(CustomerAddress.normalized_address == normalized_address)
    )
    return list(db.scalars(statement).unique().all())


def find_customers_by_normalized_reference(
    db: Session, normalized_reference: str
) -> list[Customer]:
    statement = (
        select(Customer)
        .join(CustomerAddress)
        .where(CustomerAddress.normalized_reference == normalized_reference)
    )
    return list(db.scalars(statement).unique().all())
