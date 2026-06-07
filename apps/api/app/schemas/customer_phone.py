from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerPhoneCreate(BaseModel):
    phone: str = Field(min_length=1)
    label: str | None = None
    is_primary: bool = False
    is_whatsapp: bool = True


class CustomerPhoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    phone_e164: str
    normalized_phone: str
    raw_phone: str | None
    label: str | None
    is_primary: bool
    is_whatsapp: bool
