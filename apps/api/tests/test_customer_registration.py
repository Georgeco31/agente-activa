import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action_history import ActionHistory
from app.models.customer import Customer
from app.services.customer_registration import (
    PhoneAlreadyRegisteredError,
    add_address_to_customer,
    add_alias_to_customer,
    add_phone_to_customer,
    register_customer_safely,
)


def _history_actions(db_session: Session, customer: Customer) -> list[str]:
    statement = (
        select(ActionHistory.action_type)
        .where(ActionHistory.customer_id == customer.id)
        .order_by(ActionHistory.created_at)
    )
    return list(db_session.scalars(statement).all())


def test_registers_new_customer_with_phone_alias_and_address(db_session: Session) -> None:
    result = register_customer_safely(
        db_session,
        display_name="Cliente Nuevo",
        phone="0987654321",
        alias="Tienda Agua Norte",
        address="Av. Siempre Viva # 123",
        reference="Porton Verde",
    )

    assert result.created is True
    assert result.customer is not None
    assert result.customer.display_name == "Cliente Nuevo"
    assert len(result.customer.phones) == 1
    assert len(result.customer.aliases) == 1
    assert len(result.customer.addresses) == 1


def test_register_customer_saves_normalized_name(db_session: Session) -> None:
    result = register_customer_safely(db_session, display_name="Do\u00f1a Mar\u00eda")

    assert result.customer is not None
    assert result.customer.normalized_name == "dona maria"


def test_register_customer_saves_phone_in_e164_format(db_session: Session) -> None:
    result = register_customer_safely(
        db_session,
        display_name="Cliente Telefono",
        phone="(099) 962-7968",
    )

    assert result.customer is not None
    assert result.customer.phones[0].phone_e164 == "+593999627968"
    assert result.customer.phones[0].normalized_phone == "+593999627968"


def test_register_customer_saves_normalized_alias(db_session: Session) -> None:
    result = register_customer_safely(
        db_session,
        display_name="Cliente Alias",
        alias="Do\u00f1a Mar\u00eda",
    )

    assert result.customer is not None
    assert result.customer.aliases[0].normalized_alias == "dona maria"


def test_register_customer_saves_normalized_address_and_reference(
    db_session: Session,
) -> None:
    result = register_customer_safely(
        db_session,
        display_name="Cliente Direccion",
        address="Calle 10 # 5-20",
        reference="Port\u00f3n Azul",
    )

    assert result.customer is not None
    assert result.customer.addresses[0].normalized_address == "calle 10 5 20"
    assert result.customer.addresses[0].normalized_reference == "porton azul"


def test_rejects_phone_already_registered_to_another_customer(
    db_session: Session, create_test_customer
) -> None:
    create_test_customer(display_name="Cliente Existente", phone="0999627968")
    other_customer = create_test_customer(display_name="Cliente Nuevo", phone=None)

    with pytest.raises(PhoneAlreadyRegisteredError):
        add_phone_to_customer(
            db_session,
            customer_id=other_customer.id,
            phone="+593999627968",
        )


def test_detects_duplicate_before_creating_customer(
    db_session: Session, create_test_customer
) -> None:
    existing_customer = create_test_customer(phone="0999627968")

    result = register_customer_safely(
        db_session,
        display_name="Cliente Duplicado",
        phone="+593999627968",
    )

    assert result.created is False
    assert result.customer is None
    assert result.duplicate_candidates
    assert result.duplicate_candidates[0].customer_id == existing_customer.id


def test_associates_new_phone_to_existing_customer(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(phone=None)

    phone = add_phone_to_customer(
        db_session,
        customer_id=customer.id,
        phone="0991112223",
        label="nuevo",
    )

    assert phone.customer_id == customer.id
    assert phone.normalized_phone == "+593991112223"


def test_associates_new_alias_to_existing_customer(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(alias=None)

    alias = add_alias_to_customer(
        db_session,
        customer_id=customer.id,
        alias="Se\u00f1ora del Port\u00f3n",
    )

    assert alias.customer_id == customer.id
    assert alias.normalized_alias == "senora del porton"


def test_associates_new_address_to_existing_customer(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(address=None)

    address = add_address_to_customer(
        db_session,
        customer_id=customer.id,
        address="Av. Quito y Loja",
        reference="Frente al parque",
    )

    assert address.customer_id == customer.id
    assert address.normalized_address == "av quito y loja"
    assert address.normalized_reference == "frente al parque"


def test_registers_history_when_customer_is_created(db_session: Session) -> None:
    result = register_customer_safely(db_session, display_name="Cliente Historial")

    assert result.customer is not None
    assert "customer_created" in _history_actions(db_session, result.customer)


def test_registers_history_when_phone_is_added(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(phone=None)

    add_phone_to_customer(db_session, customer_id=customer.id, phone="0991112223")

    assert "phone_added" in _history_actions(db_session, customer)


def test_registers_history_when_alias_is_added(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(alias=None)

    add_alias_to_customer(db_session, customer_id=customer.id, alias="Alias Nuevo")

    assert "alias_added" in _history_actions(db_session, customer)


def test_registers_history_when_address_is_added(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(address=None)

    add_address_to_customer(
        db_session,
        customer_id=customer.id,
        address="Calle Nueva",
        reference="Casa blanca",
    )

    assert "address_added" in _history_actions(db_session, customer)
