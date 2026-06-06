from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.customer_alias import CustomerAlias
from app.models.customer_phone import CustomerPhone


def get_customer_by_id(db: Session, customer_id: UUID) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.id == customer_id))


def create_customer(
    db: Session,
    *,
    display_name: str,
    normalized_name: str,
    customer_type: str | None = None,
    status: str = "activo",
    notes: str | None = None,
) -> Customer:
    customer = Customer(
        display_name=display_name,
        normalized_name=normalized_name,
        customer_type=customer_type,
        status=status,
        notes=notes,
    )
    db.add(customer)
    db.flush()
    return customer


def find_customer_by_normalized_phone(db: Session, normalized_phone: str) -> Customer | None:
    statement = (
        select(Customer)
        .join(CustomerPhone)
        .where(CustomerPhone.normalized_phone == normalized_phone)
    )
    return db.scalars(statement).unique().first()


def get_phone_by_normalized_phone(
    db: Session, normalized_phone: str
) -> CustomerPhone | None:
    return db.scalar(
        select(CustomerPhone).where(CustomerPhone.normalized_phone == normalized_phone)
    )


def normalized_phone_exists(db: Session, normalized_phone: str) -> bool:
    return get_phone_by_normalized_phone(db, normalized_phone) is not None


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


def create_customer_phone(
    db: Session,
    *,
    customer_id: UUID,
    phone_e164: str,
    normalized_phone: str,
    raw_phone: str | None = None,
    label: str | None = None,
    is_primary: bool = False,
    is_whatsapp: bool = True,
) -> CustomerPhone:
    phone = CustomerPhone(
        customer_id=customer_id,
        phone_e164=phone_e164,
        normalized_phone=normalized_phone,
        raw_phone=raw_phone,
        label=label,
        is_primary=is_primary,
        is_whatsapp=is_whatsapp,
    )
    db.add(phone)
    db.flush()
    return phone


def create_customer_alias(
    db: Session,
    *,
    customer_id: UUID,
    alias: str,
    normalized_alias: str,
    source: str = "manual",
) -> CustomerAlias:
    customer_alias = CustomerAlias(
        customer_id=customer_id,
        alias=alias,
        normalized_alias=normalized_alias,
        source=source,
    )
    db.add(customer_alias)
    db.flush()
    return customer_alias


def create_customer_address(
    db: Session,
    *,
    customer_id: UUID,
    address_text: str,
    normalized_address: str,
    reference: str | None = None,
    normalized_reference: str | None = None,
    label: str | None = None,
    city: str | None = None,
    neighborhood: str | None = None,
    is_primary: bool = False,
    notes: str | None = None,
) -> CustomerAddress:
    address = CustomerAddress(
        customer_id=customer_id,
        label=label,
        address_text=address_text,
        normalized_address=normalized_address,
        reference=reference,
        normalized_reference=normalized_reference,
        city=city,
        neighborhood=neighborhood,
        is_primary=is_primary,
        notes=notes,
    )
    db.add(address)
    db.flush()
    return address
