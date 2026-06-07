from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.customer_address import CustomerAddressResponse
from app.schemas.customer_alias import CustomerAliasResponse
from app.schemas.customer_phone import CustomerPhoneResponse
from app.schemas.search import DuplicateCandidateResponse


class CustomerCreate(BaseModel):
    display_name: str = Field(min_length=1)
    phone: str | None = None
    alias: str | None = None
    address: str | None = None
    reference: str | None = None
    customer_type: str | None = None
    notes: str | None = None


class CustomerSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    normalized_name: str
    customer_type: str | None
    status: str


class CustomerDetailResponse(CustomerSummaryResponse):
    phones: list[CustomerPhoneResponse]
    aliases: list[CustomerAliasResponse]
    addresses: list[CustomerAddressResponse]


class CustomerRegistrationResponse(BaseModel):
    created: bool
    customer: CustomerDetailResponse | None = None
    duplicate_candidates: list[DuplicateCandidateResponse] = Field(default_factory=list)
    message: str
