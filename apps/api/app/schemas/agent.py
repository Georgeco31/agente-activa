from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order import OrderResponse


class AgentIntent(StrEnum):
    GREETING = "greeting"
    CREATE_ORDER = "create_order"
    ASK_PRICE = "ask_price"
    ASK_ORDER_STATUS = "ask_order_status"
    CANCEL_ORDER = "cancel_order"
    PROVIDE_ADDRESS = "provide_address"
    UNKNOWN = "unknown"


class ConversationStatus(StrEnum):
    ACTIVE = "active"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    READY_FOR_CONFIRMATION = "ready_for_confirmation"
    CLOSED = "closed"
    EXPIRED = "expired"


class ConversationMessageDirection(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    SYSTEM = "system"


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
    address_id: UUID | None = None
    address_hint: str | None = None


class AgentSimulationResponse(BaseModel):
    intent: AgentIntent
    confidence: float = Field(ge=0, le=1)
    customer: AgentCustomerMatch
    extracted: AgentExtraction
    missing_fields: list[str] = Field(default_factory=list)
    reply: str


class AgentConversationSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ConversationStatus
    current_intent: AgentIntent | None = None


class AgentConversationMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    direction: ConversationMessageDirection
    phone: str
    message: str
    intent: AgentIntent | None = None
    confidence: Decimal | None = None
    message_metadata: dict[str, Any] | None = None
    created_at: datetime


class AgentConversationSessionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    normalized_phone: str
    customer_id: UUID | None
    status: ConversationStatus
    current_intent: AgentIntent | None = None
    extracted_data: dict[str, Any]
    missing_fields: list[str]
    last_message_at: datetime
    created_at: datetime
    updated_at: datetime
    messages: list[AgentConversationMessageResponse] = Field(default_factory=list)


class AgentConversationSimulationResponse(BaseModel):
    session: AgentConversationSessionSummary
    analysis: AgentSimulationResponse


class AgentOrderConfirmationRequest(BaseModel):
    message: str = Field(min_length=1)


class AgentOrderConfirmationResponse(BaseModel):
    session: AgentConversationSessionDetail
    order: OrderResponse
    reply: str
