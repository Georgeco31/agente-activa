from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerAddressCreate(BaseModel):
    address: str = Field(min_length=1)
    reference: str | None = None
    label: str | None = None
    city: str | None = None
    neighborhood: str | None = None
    is_primary: bool = False
    notes: str | None = None


class CustomerAddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    address_text: str
    normalized_address: str
    reference: str | None
    normalized_reference: str | None
    label: str | None
    city: str | None
    neighborhood: str | None
    is_primary: bool
    notes: str | None
