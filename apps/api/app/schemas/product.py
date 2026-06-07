from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    unit: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=80)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    unit: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_has_changes(self):
        if not self.model_fields_set:
            raise ValueError("At least one field is required.")
        return self


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sku: str
    name: str
    normalized_name: str
    description: str | None
    unit: str
    price: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
