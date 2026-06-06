import pytest

from app.services.normalization import normalize_ecuador_phone, normalize_text


def test_normalize_ecuador_phone_with_local_zero_prefix() -> None:
    assert normalize_ecuador_phone("0999627968") == "+593999627968"


def test_normalize_ecuador_phone_without_local_zero_prefix() -> None:
    assert normalize_ecuador_phone("999627968") == "+593999627968"


def test_normalize_ecuador_phone_already_in_e164_format() -> None:
    assert normalize_ecuador_phone("+593999627968") == "+593999627968"


def test_normalize_ecuador_phone_with_spaces_hyphens_and_parentheses() -> None:
    assert normalize_ecuador_phone("(099) 962-7968") == "+593999627968"


def test_normalize_ecuador_phone_rejects_empty_phone() -> None:
    with pytest.raises(ValueError):
        normalize_ecuador_phone("   ")


@pytest.mark.parametrize(
    "phone",
    [
        "12345",
        "022345678",
        "+573001112233",
        "abc0999627968",
    ],
)
def test_normalize_ecuador_phone_rejects_invalid_phone(phone: str) -> None:
    with pytest.raises(ValueError):
        normalize_ecuador_phone(phone)


def test_normalize_text_removes_accents() -> None:
    assert normalize_text("Arbol Caf\u00e9 Ni\u00f1o") == "arbol cafe nino"


def test_normalize_text_lowercases_uppercase_text() -> None:
    assert normalize_text("CLIENTE NORTE") == "cliente norte"


def test_normalize_text_removes_unnecessary_signs() -> None:
    assert normalize_text("Tienda #5, Sector-A!") == "tienda 5 sector a"


def test_normalize_text_removes_extra_spaces() -> None:
    assert normalize_text("  Calle   10    Casa   Azul  ") == "calle 10 casa azul"


def test_normalize_text_normalizes_dona_maria_porton_azul() -> None:
    assert normalize_text("Do\u00f1a Mar\u00eda, Port\u00f3n Azul") == "dona maria porton azul"
