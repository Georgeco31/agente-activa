from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.services.customer_search import (
    search_customer_by_phone,
    search_customers_by_address,
    search_customers_by_alias,
    search_customers_by_name,
    search_customers_by_reference,
)
from app.services.normalization import normalize_ecuador_phone

PHONE_EXACT_SCORE = 100
ALIAS_MATCH_SCORE = 70
ADDRESS_MATCH_SCORE = 60
REFERENCE_MATCH_SCORE = 50
NAME_MATCH_SCORE = 40


@dataclass
class DuplicateCandidate:
    customer_id: UUID
    display_name: str
    reasons: list[str] = field(default_factory=list)
    score: int = 0
    confidence: str = "baja"


def _confidence_from_score(score: int) -> str:
    if score >= 90:
        return "alta"
    if score >= 60:
        return "media"
    return "baja"


def _add_match(
    candidates: dict[UUID, DuplicateCandidate],
    customer: Customer,
    reason: str,
    score: int,
) -> None:
    candidate = candidates.get(customer.id)
    if candidate is None:
        candidate = DuplicateCandidate(customer_id=customer.id, display_name=customer.display_name)
        candidates[customer.id] = candidate

    if reason not in candidate.reasons:
        candidate.reasons.append(reason)

    candidate.score += score
    candidate.confidence = _confidence_from_score(candidate.score)


def _safe_search_customer_by_phone(db: Session, phone: str) -> Customer | None:
    try:
        normalize_ecuador_phone(phone)
    except ValueError:
        return None
    return search_customer_by_phone(db, phone)


def detect_duplicate_customers(
    db: Session,
    *,
    phone: str | None = None,
    name: str | None = None,
    alias: str | None = None,
    address: str | None = None,
    reference: str | None = None,
) -> list[DuplicateCandidate]:
    candidates: dict[UUID, DuplicateCandidate] = {}

    if phone:
        customer = _safe_search_customer_by_phone(db, phone)
        if customer is not None:
            _add_match(candidates, customer, "telefono exacto", PHONE_EXACT_SCORE)

    if name:
        for customer in search_customers_by_name(db, name):
            _add_match(candidates, customer, "nombre normalizado coincidente", NAME_MATCH_SCORE)

    if alias:
        for customer in search_customers_by_alias(db, alias):
            _add_match(candidates, customer, "alias coincidente", ALIAS_MATCH_SCORE)

    if address:
        for customer in search_customers_by_address(db, address):
            _add_match(candidates, customer, "direccion coincidente", ADDRESS_MATCH_SCORE)

    if reference:
        for customer in search_customers_by_reference(db, reference):
            _add_match(candidates, customer, "referencia coincidente", REFERENCE_MATCH_SCORE)

    return sorted(candidates.values(), key=lambda candidate: candidate.score, reverse=True)
