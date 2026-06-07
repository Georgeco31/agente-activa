from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
