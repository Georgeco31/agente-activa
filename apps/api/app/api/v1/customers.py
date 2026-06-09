from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.core.exceptions import ApiError, ErrorCode
from app.repositories import customers as customer_repository
from app.schemas.customer import (
    CustomerCreate,
    CustomerDetailResponse,
    CustomerRegistrationResponse,
    CustomerSummaryResponse,
)
from app.schemas.customer_address import CustomerAddressCreate, CustomerAddressResponse
from app.schemas.customer_alias import CustomerAliasCreate, CustomerAliasResponse
from app.schemas.customer_phone import CustomerPhoneCreate, CustomerPhoneResponse
from app.schemas.search import DuplicateCandidateResponse, DuplicateDetectionRequest
from app.services.customer_registration import (
    CustomerNotFoundError,
    CustomerRegistrationError,
    PhoneAlreadyRegisteredError,
    add_address_to_customer,
    add_alias_to_customer,
    add_phone_to_customer,
    register_customer_safely,
)
from app.services.customer_search import search_customers
from app.services.duplicate_detection import detect_duplicate_customers

router = APIRouter(prefix="/customers", tags=["customers"])


def _duplicate_responses(candidates: list) -> list[DuplicateCandidateResponse]:
    return [DuplicateCandidateResponse.model_validate(candidate) for candidate in candidates]


@router.post(
    "",
    response_model=CustomerRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(payload: CustomerCreate, db: DbSession):
    try:
        result = register_customer_safely(db, **payload.model_dump())
        db.commit()
    except PhoneAlreadyRegisteredError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.CUSTOMER_PHONE_ALREADY_EXISTS,
            message=str(exc),
        ) from exc
    except CustomerRegistrationError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc

    duplicate_candidates = _duplicate_responses(result.duplicate_candidates)
    response = CustomerRegistrationResponse(
        created=result.created,
        customer=(
            CustomerDetailResponse.model_validate(result.customer)
            if result.customer is not None
            else None
        ),
        duplicate_candidates=duplicate_candidates,
        message=result.message,
    )

    if not result.created:
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.CUSTOMER_DUPLICATE_CANDIDATE_FOUND,
            message=result.message,
            details={
                "duplicate_candidates": [
                    candidate.model_dump(mode="json") for candidate in duplicate_candidates
                ]
            },
        )

    return response


@router.get("/search", response_model=list[CustomerSummaryResponse])
def find_customers(
    db: DbSession,
    phone: str | None = Query(default=None),
    name: str | None = Query(default=None),
    alias: str | None = Query(default=None),
    address: str | None = Query(default=None),
    reference: str | None = Query(default=None),
):
    if not any([phone, name, alias, address, reference]):
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message="At least one search criterion is required.",
        )

    try:
        return search_customers(
            db,
            phone=phone,
            name=name,
            alias=alias,
            address=address,
            reference=reference,
        )
    except ValueError as exc:
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc


@router.post("/detect-duplicates", response_model=list[DuplicateCandidateResponse])
def detect_duplicates(payload: DuplicateDetectionRequest, db: DbSession):
    return detect_duplicate_customers(db, **payload.model_dump())


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
def get_customer(customer_id: UUID, db: DbSession):
    customer = customer_repository.get_customer_by_id(db, customer_id)
    if customer is None:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CUSTOMER_NOT_FOUND,
            message="Customer not found.",
        )
    return customer


@router.post(
    "/{customer_id}/phones",
    response_model=CustomerPhoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_phone(customer_id: UUID, payload: CustomerPhoneCreate, db: DbSession):
    try:
        phone = add_phone_to_customer(db, customer_id=customer_id, **payload.model_dump())
        db.commit()
        db.refresh(phone)
        return phone
    except PhoneAlreadyRegisteredError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.CUSTOMER_PHONE_ALREADY_EXISTS,
            message=str(exc),
        ) from exc
    except CustomerNotFoundError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CUSTOMER_NOT_FOUND,
            message=str(exc),
        ) from exc
    except CustomerRegistrationError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc
    except ValueError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc


@router.post(
    "/{customer_id}/aliases",
    response_model=CustomerAliasResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_alias(customer_id: UUID, payload: CustomerAliasCreate, db: DbSession):
    try:
        alias = add_alias_to_customer(db, customer_id=customer_id, **payload.model_dump())
        db.commit()
        db.refresh(alias)
        return alias
    except CustomerNotFoundError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CUSTOMER_NOT_FOUND,
            message=str(exc),
        ) from exc
    except CustomerRegistrationError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc


@router.post(
    "/{customer_id}/addresses",
    response_model=CustomerAddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer_address(customer_id: UUID, payload: CustomerAddressCreate, db: DbSession):
    try:
        address = add_address_to_customer(db, customer_id=customer_id, **payload.model_dump())
        db.commit()
        db.refresh(address)
        return address
    except CustomerNotFoundError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CUSTOMER_NOT_FOUND,
            message=str(exc),
        ) from exc
    except CustomerRegistrationError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message=str(exc),
        ) from exc
