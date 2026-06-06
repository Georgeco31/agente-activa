from sqlalchemy.orm import Session

from app.services.duplicate_detection import detect_duplicate_customers


def test_detects_duplicate_by_exact_phone(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(phone="0999627968")

    result = detect_duplicate_customers(db_session, phone="+593999627968")

    assert len(result) == 1
    assert result[0].customer_id == customer.id
    assert "telefono exacto" in result[0].reasons
    assert result[0].score >= 100
    assert result[0].confidence == "alta"


def test_detects_possible_duplicate_by_alias(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(alias="Dona Maria")

    result = detect_duplicate_customers(db_session, alias="Do\u00f1a Mar\u00eda")

    assert len(result) == 1
    assert result[0].customer_id == customer.id
    assert "alias coincidente" in result[0].reasons
    assert result[0].confidence == "media"


def test_detects_possible_duplicate_by_address_and_reference(
    db_session: Session, create_test_customer
) -> None:
    customer = create_test_customer(address="Calle 10 # 5-20", reference="Porton Azul")

    result = detect_duplicate_customers(
        db_session,
        address="calle 10 5 20",
        reference="Port\u00f3n Azul",
    )

    assert len(result) == 1
    assert result[0].customer_id == customer.id
    assert "direccion coincidente" in result[0].reasons
    assert "referencia coincidente" in result[0].reasons
    assert result[0].score >= 110
    assert result[0].confidence == "alta"


def test_returns_no_duplicate_when_there_are_no_matches(db_session: Session) -> None:
    result = detect_duplicate_customers(
        db_session,
        phone="0988888888",
        name="Cliente Nuevo",
        alias="Alias Nuevo",
        address="Direccion Nueva",
        reference="Referencia Nueva",
    )

    assert result == []


def test_duplicate_result_includes_match_reasons(
    db_session: Session, create_test_customer
) -> None:
    create_test_customer(display_name="Maria Gomez", alias="Dona Maria")

    result = detect_duplicate_customers(
        db_session,
        name="Maria Gomez",
        alias="Do\u00f1a Mar\u00eda",
    )

    assert result
    assert "nombre normalizado coincidente" in result[0].reasons
    assert "alias coincidente" in result[0].reasons


def test_duplicate_result_includes_score_and_confidence(
    db_session: Session, create_test_customer
) -> None:
    create_test_customer(alias="Dona Maria")

    result = detect_duplicate_customers(db_session, alias="Dona Maria")

    assert result
    assert isinstance(result[0].score, int)
    assert result[0].score > 0
    assert result[0].confidence in {"baja", "media", "alta"}
