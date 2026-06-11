from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, and_, cast, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.order import Order
from app.models.order_status import OrderStatus
from app.models.product import Product

ECUADOR_TIMEZONE = "America/Guayaquil"


@dataclass(frozen=True)
class StatusMetric:
    code: str
    name: str
    count: int
    total: Decimal


@dataclass(frozen=True)
class DailySalesMetric:
    sale_date: date
    delivered_orders_count: int
    sales_total: Decimal


@dataclass(frozen=True)
class CatalogMetric:
    active_products: int
    total_customers: int


def get_daily_status_metrics(
    db: Session,
    *,
    start_at: datetime,
    end_at: datetime,
) -> list[StatusMetric]:
    statement = (
        select(
            OrderStatus.code,
            OrderStatus.name,
            func.count(Order.id).label("order_count"),
            func.coalesce(func.sum(Order.total), 0).label("order_total"),
        )
        .outerjoin(
            Order,
            and_(
                Order.order_status_id == OrderStatus.id,
                Order.created_at >= start_at,
                Order.created_at < end_at,
            ),
        )
        .group_by(OrderStatus.id, OrderStatus.code, OrderStatus.name, OrderStatus.sort_order)
        .order_by(OrderStatus.sort_order)
    )
    return [
        StatusMetric(
            code=row.code,
            name=row.name,
            count=row.order_count,
            total=row.order_total,
        )
        for row in db.execute(statement)
    ]


def get_monthly_sales(
    db: Session,
    *,
    start_at: datetime,
    end_at: datetime,
) -> list[DailySalesMetric]:
    local_sale_date = cast(func.timezone(ECUADOR_TIMEZONE, Order.created_at), Date)
    statement = (
        select(
            local_sale_date.label("sale_date"),
            func.count(Order.id).label("delivered_orders_count"),
            func.coalesce(func.sum(Order.total), 0).label("sales_total"),
        )
        .join(OrderStatus)
        .where(
            OrderStatus.code == "entregado",
            Order.created_at >= start_at,
            Order.created_at < end_at,
        )
        .group_by(local_sale_date)
        .order_by(local_sale_date)
    )
    return [
        DailySalesMetric(
            sale_date=row.sale_date,
            delivered_orders_count=row.delivered_orders_count,
            sales_total=row.sales_total,
        )
        for row in db.execute(statement)
    ]


def get_catalog_metrics(db: Session) -> CatalogMetric:
    statement = select(
        select(func.count(Product.id))
        .where(Product.is_active.is_(True))
        .scalar_subquery()
        .label("active_products"),
        select(func.count(Customer.id)).scalar_subquery().label("total_customers"),
    )
    row = db.execute(statement).one()
    return CatalogMetric(
        active_products=row.active_products,
        total_customers=row.total_customers,
    )


def get_recent_orders(db: Session, *, limit: int = 8) -> list[Order]:
    statement = (
        select(Order)
        .options(
            selectinload(Order.status),
            selectinload(Order.customer).selectinload(Customer.phones),
            selectinload(Order.customer_address),
        )
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    return list(db.scalars(statement).unique().all())
