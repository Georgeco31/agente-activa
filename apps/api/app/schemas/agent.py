from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class AgentIntent(StrEnum):
    GREETING = "greeting"
    CREATE_ORDER = "create_order"
    ASK_PRICE = "ask_price"
    ASK_ORDER_STATUS = "ask_order_status"
    CANCEL_ORDER = "cancel_order"
    PROVIDE_ADDRESS = "provide_address"
    UNKNOWN = "unknown"


class AgentSimulationRequest(BaseModel):
    phone: str = Field(min_length=1)
    message: str


class AgentCustomerMatch(BaseModel):
    found: bool
    id: UUID | None = None
    display_name: str | None = None


class AgentExtraction(BaseModel):
    quantity: int | None = None
    product_hint: str | None = None
    product_id: UUID | None = None
    product_name: str | None = None
    product_price: Decimal | None = None
    address_hint: str | None = None


class AgentSimulationResponse(BaseModel):
    intent: AgentIntent
    confidence: float = Field(ge=0, le=1)
    customer: AgentCustomerMatch
    extracted: AgentExtraction
    missing_fields: list[str] = Field(default_factory=list)
    reply: str
