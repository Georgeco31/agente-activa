from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerAliasCreate(BaseModel):
    alias: str = Field(min_length=1)
    source: str = "manual"


class CustomerAliasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: UUID
    alias: str
    normalized_alias: str
    source: str
