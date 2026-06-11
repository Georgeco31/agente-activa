from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal | None = Field(default=None, ge=0)


class OrderCreate(BaseModel):
    customer_id: UUID
    address_id: UUID
    items: list[OrderItemCreate] = Field(min_length=1)
    notes: str | None = None
    delivery_route_id: UUID | None = None


class OrderStatusUpdate(BaseModel):
    status_code: str = Field(min_length=1)


class OrderStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    is_final: bool


class OrderCustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    primary_phone: str | None = None

    @model_validator(mode="before")
    @classmethod
    def resolve_primary_phone(cls, value):
        if isinstance(value, dict):
            return value

        primary_phone = next(
            (phone.phone_e164 for phone in value.phones if phone.is_primary),
            None,
        )
        return {
            "id": value.id,
            "display_name": value.display_name,
            "primary_phone": primary_phone,
        }


class OrderAddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    address: str = Field(validation_alias="address_text")
    reference: str | None


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_name_snapshot: str
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    customer_id: UUID
    address_id: UUID = Field(validation_alias="customer_address_id")
    customer: OrderCustomerResponse
    address: OrderAddressResponse = Field(validation_alias="customer_address")
    status: OrderStatusResponse
    delivery_route_id: UUID | None
    notes: str | None
    source_channel: str
    subtotal: Decimal
    delivery_fee: Decimal
    total: Decimal
    confirmed_at: datetime | None
    created_at: datetime
    items: list[OrderItemResponse]
