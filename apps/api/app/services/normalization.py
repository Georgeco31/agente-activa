import re
import unicodedata

ECUADOR_COUNTRY_CODE = "593"
ECUADOR_MOBILE_PREFIX = "9"
ECUADOR_MOBILE_DIGITS = 9


def normalize_ecuador_phone(phone: str) -> str:
    if phone is None:
        raise ValueError("Phone is required.")

    raw_phone = str(phone).strip()
    if not raw_phone:
        raise ValueError("Phone is required.")

    if re.search(r"[A-Za-z]", raw_phone):
        raise ValueError("Phone contains invalid characters.")

    cleaned_phone = re.sub(r"[\s().-]+", "", raw_phone)
    if cleaned_phone.count("+") > 1 or ("+" in cleaned_phone and not cleaned_phone.startswith("+")):
        raise ValueError("Phone has an invalid international format.")

    digits = re.sub(r"\D", "", cleaned_phone)
    if not digits:
        raise ValueError("Phone is required.")

    if digits.startswith(ECUADOR_COUNTRY_CODE):
        national_number = digits[len(ECUADOR_COUNTRY_CODE) :]
    elif digits.startswith("0"):
        national_number = digits[1:]
    else:
        national_number = digits

    if (
        len(national_number) != ECUADOR_MOBILE_DIGITS
        or not national_number.startswith(ECUADOR_MOBILE_PREFIX)
    ):
        raise ValueError("Phone is not a valid Ecuadorian mobile number.")

    return f"+{ECUADOR_COUNTRY_CODE}{national_number}"


def normalize_text(value: str) -> str:
    if value is None:
        return ""

    text = str(value).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()
