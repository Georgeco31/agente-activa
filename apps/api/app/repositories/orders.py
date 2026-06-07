from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.customer import Customer
from app.models.customer_address import CustomerAddress
from app.models.delivery_route import DeliveryRoute
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.order_status import OrderStatus
from app.models.product import Product


def get_customer_by_id(db: Session, customer_id: UUID) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.id == customer_id))


def get_address_by_id(db: Session, address_id: UUID) -> CustomerAddress | None:
    return db.scalar(select(CustomerAddress).where(CustomerAddress.id == address_id))


def get_product_by_id(db: Session, product_id: UUID) -> Product | None:
    return db.scalar(select(Product).where(Product.id == product_id))


def get_delivery_route_by_id(db: Session, delivery_route_id: UUID) -> DeliveryRoute | None:
    return db.scalar(select(DeliveryRoute).where(DeliveryRoute.id == delivery_route_id))


def get_status_by_code(db: Session, code: str) -> OrderStatus | None:
    return db.scalar(select(OrderStatus).where(OrderStatus.code == code))


def get_order_by_number(db: Session, order_number: str) -> Order | None:
    return db.scalar(select(Order).where(Order.order_number == order_number))


def create_order(
    db: Session,
    *,
    order_number: str,
    customer_id: UUID,
    customer_address_id: UUID,
    order_status_id: UUID,
    delivery_route_id: UUID | None,
    notes: str | None,
    subtotal: Decimal,
    delivery_fee: Decimal,
    total: Decimal,
    confirmed_at: datetime,
) -> Order:
    order = Order(
        order_number=order_number,
        customer_id=customer_id,
        customer_address_id=customer_address_id,
        order_status_id=order_status_id,
        delivery_route_id=delivery_route_id,
        notes=notes,
        source_channel="manual",
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        confirmed_at=confirmed_at,
    )
    db.add(order)
    db.flush()
    return order


def create_order_item(
    db: Session,
    *,
    order_id: UUID,
    product_id: UUID,
    product_name_snapshot: str,
    quantity: Decimal,
    unit_price: Decimal,
    line_total: Decimal,
) -> OrderItem:
    item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        product_name_snapshot=product_name_snapshot,
        quantity=quantity,
        unit_price=unit_price,
        line_total=line_total,
    )
    db.add(item)
    db.flush()
    return item


def get_order_by_id(db: Session, order_id: UUID) -> Order | None:
    statement = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.status))
        .where(Order.id == order_id)
    )
    return db.scalar(statement)


def list_orders(
    db: Session,
    *,
    customer_id: UUID | None = None,
    status_code: str | None = None,
) -> list[Order]:
    statement = select(Order).options(selectinload(Order.items), selectinload(Order.status))

    if customer_id is not None:
        statement = statement.where(Order.customer_id == customer_id)

    if status_code is not None:
        statement = statement.join(OrderStatus).where(OrderStatus.code == status_code)

    statement = statement.order_by(Order.created_at.desc())
    return list(db.scalars(statement).unique().all())


def update_order_status(db: Session, order: Order, order_status: OrderStatus) -> Order:
    order.status = order_status
    order.order_status_id = order_status.id
    db.flush()
    return order
