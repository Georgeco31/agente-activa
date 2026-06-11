from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.order import OrderAddressResponse, OrderCustomerResponse, OrderStatusResponse


class DashboardSummaryResponse(BaseModel):
    orders_today: int
    pending_orders: int
    assigned_orders: int
    en_route_orders: int
    delivered_orders: int
    not_delivered_orders: int
    cancelled_orders: int
    sales_total_today: Decimal
    sales_total_month: Decimal
    active_products: int
    total_customers: int


class DashboardStatusCountResponse(BaseModel):
    code: str
    name: str
    count: int


class DashboardDailySalesResponse(BaseModel):
    day: int
    date: date
    sales_total: Decimal
    delivered_orders_count: int


class DashboardRecentOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    customer: OrderCustomerResponse
    address: OrderAddressResponse = Field(validation_alias="customer_address")
    status: OrderStatusResponse
    total: Decimal
    created_at: datetime


class DashboardAlertResponse(BaseModel):
    code: str
    label: str
    count: int
    severity: Literal["info", "warning", "danger"]
    status_code: str


class DashboardOverviewResponse(BaseModel):
    selected_date: date
    month: int
    year: int
    summary: DashboardSummaryResponse
    orders_by_status: list[DashboardStatusCountResponse]
    monthly_sales: list[DashboardDailySalesResponse]
    recent_orders: list[DashboardRecentOrderResponse]
    alerts: list[DashboardAlertResponse]

    @model_validator(mode="after")
    def validate_period(self):
        if not 1 <= self.month <= 12:
            raise ValueError("Month must be between 1 and 12.")
        return self
