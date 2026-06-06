from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.customer_alias import CustomerAlias
from app.models.customer_phone import CustomerPhone
from app.repositories import customers as customer_repository
from app.services.action_history import record_action
from app.services.duplicate_detection import DuplicateCandidate, detect_duplicate_customers
from app.services.normalization import normalize_ecuador_phone, normalize_text

STRONG_DUPLICATE_SCORE = 90


class CustomerRegistrationError(ValueError):
    pass


class PhoneAlreadyRegisteredError(CustomerRegistrationError):
    pass


class CustomerNotFoundError(CustomerRegistrationError):
    pass


class DuplicateCustomerFoundError(CustomerRegistrationError):
    def __init__(self, duplicate_candidates: list[DuplicateCandidate]) -> None:
        super().__init__("Possible duplicate customers were found.")
        self.duplicate_candidates = duplicate_candidates


@dataclass
class CustomerRegistrationResult:
    created: bool
    customer: Customer | None = None
    duplicate_candidates: list[DuplicateCandidate] = field(default_factory=list)
    message: str = ""


def _get_existing_phone_owner_id(db: Session, normalized_phone: str) -> UUID | None:
    phone = customer_repository.get_phone_by_normalized_phone(db, normalized_phone)
    if phone is None:
        return None
    return phone.customer_id


def _ensure_customer_exists(db: Session, customer_id: UUID) -> Customer:
    customer = customer_repository.get_customer_by_id(db, customer_id)
    if customer is None:
        raise CustomerNotFoundError("Customer does not exist.")
    return customer


def _record_duplicate_candidates(
    db: Session, duplicate_candidates: list[DuplicateCandidate]
) -> None:
    for candidate in duplicate_candidates:
        record_action(
            db,
            entity_type="customer",
            entity_id=candidate.customer_id,
            customer_id=candidate.customer_id,
            action_type="duplicate_candidate_found",
            description="Possible duplicate customer found before registration.",
            new_value={
                "reasons": candidate.reasons,
                "score": candidate.score,
                "confidence": candidate.confidence,
            },
        )


def add_phone_to_customer(
    db: Session,
    *,
    customer_id: UUID,
    phone: str,
    label: str | None = "whatsapp",
    is_primary: bool = False,
    is_whatsapp: bool = True,
) -> CustomerPhone:
    _ensure_customer_exists(db, customer_id)
    normalized_phone = normalize_ecuador_phone(phone)
    existing_owner_id = _get_existing_phone_owner_id(db, normalized_phone)

    if existing_owner_id is not None:
        raise PhoneAlreadyRegisteredError("Phone is already registered.")

    customer_phone = customer_repository.create_customer_phone(
        db,
        customer_id=customer_id,
        phone_e164=normalized_phone,
        normalized_phone=normalized_phone,
        raw_phone=phone,
        label=label,
        is_primary=is_primary,
        is_whatsapp=is_whatsapp,
    )
    record_action(
        db,
        entity_type="customer_phone",
        entity_id=customer_phone.id,
        customer_id=customer_id,
        action_type="phone_added",
        description="Phone added to customer.",
        new_value={"phone_e164": normalized_phone, "label": label},
    )
    return customer_phone


def add_alias_to_customer(
    db: Session,
    *,
    customer_id: UUID,
    alias: str,
    source: str = "manual",
) -> CustomerAlias:
    _ensure_customer_exists(db, customer_id)
    normalized_alias = normalize_text(alias)
    if not normalized_alias:
        raise CustomerRegistrationError("Alias is required.")

    customer_alias = customer_repository.create_customer_alias(
        db,
        customer_id=customer_id,
        alias=alias,
        normalized_alias=normalized_alias,
        source=source,
    )
    record_action(
        db,
        entity_type="customer_alias",
        entity_id=customer_alias.id,
        customer_id=customer_id,
        action_type="alias_added",
        description="Alias added to customer.",
        new_value={"alias": alias, "normalized_alias": normalized_alias, "source": source},
    )
    return customer_alias


def add_address_to_customer(
    db: Session,
    *,
    customer_id: UUID,
    address: str,
    reference: str | None = None,
    label: str | None = None,
    city: str | None = None,
    neighborhood: str | None = None,
    is_primary: bool = False,
    notes: str | None = None,
) -> CustomerAddress:
    _ensure_customer_exists(db, customer_id)
    normalized_address = normalize_text(address)
    normalized_reference = normalize_text(reference)
    if not normalized_address:
        raise CustomerRegistrationError("Address is required.")

    customer_address = customer_repository.create_customer_address(
        db,
        customer_id=customer_id,
        address_text=address,
        normalized_address=normalized_address,
        reference=reference,
        normalized_reference=normalized_reference,
        label=label,
        city=city,
        neighborhood=neighborhood,
        is_primary=is_primary,
        notes=notes,
    )
    record_action(
        db,
        entity_type="customer_address",
        entity_id=customer_address.id,
        customer_id=customer_id,
        action_type="address_added",
        description="Address added to customer.",
        new_value={
            "address": address,
            "normalized_address": normalized_address,
            "reference": reference,
            "normalized_reference": normalized_reference,
        },
    )
    return customer_address


def register_customer_safely(
    db: Session,
    *,
    display_name: str,
    phone: str | None = None,
    alias: str | None = None,
    address: str | None = None,
    reference: str | None = None,
    customer_type: str | None = None,
    notes: str | None = None,
) -> CustomerRegistrationResult:
    normalized_name = normalize_text(display_name)
    if not normalized_name:
        raise CustomerRegistrationError("Display name is required.")

    duplicate_candidates = detect_duplicate_customers(
        db,
        phone=phone,
        name=display_name,
        alias=alias,
        address=address,
        reference=reference,
    )
    strong_candidates = [
        candidate
        for candidate in duplicate_candidates
        if candidate.score >= STRONG_DUPLICATE_SCORE or "telefono exacto" in candidate.reasons
    ]

    if strong_candidates:
        _record_duplicate_candidates(db, strong_candidates)
        return CustomerRegistrationResult(
            created=False,
            duplicate_candidates=strong_candidates,
            message="Possible duplicate customers found.",
        )

    if phone is not None:
        normalized_phone = normalize_ecuador_phone(phone)
        if customer_repository.normalized_phone_exists(db, normalized_phone):
            raise PhoneAlreadyRegisteredError("Phone is already registered.")

    customer = customer_repository.create_customer(
        db,
        display_name=display_name,
        normalized_name=normalized_name,
        customer_type=customer_type,
        notes=notes,
    )
    record_action(
        db,
        entity_type="customer",
        entity_id=customer.id,
        customer_id=customer.id,
        action_type="customer_created",
        description="Customer created.",
        new_value={
            "display_name": display_name,
            "normalized_name": normalized_name,
            "customer_type": customer_type,
        },
    )

    if phone is not None:
        add_phone_to_customer(
            db,
            customer_id=customer.id,
            phone=phone,
            label="whatsapp",
            is_primary=True,
            is_whatsapp=True,
        )

    if alias is not None:
        add_alias_to_customer(db, customer_id=customer.id, alias=alias)

    if address is not None:
        add_address_to_customer(
            db,
            customer_id=customer.id,
            address=address,
            reference=reference,
            label="principal",
            is_primary=True,
        )

    return CustomerRegistrationResult(
        created=True,
        customer=customer,
        duplicate_candidates=[],
        message="Customer created.",
    )
