from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.product import Product
from app.repositories import orders as order_repository
from app.services.action_history import record_action

PENDING_STATUS_CODE = "pendiente"
CANCELLED_STATUS_CODE = "cancelado"
ZERO_AMOUNT = Decimal("0.00")


class OrderServiceError(ValueError):
    pass


class OrderNotFoundError(OrderServiceError):
    pass


class CustomerNotFoundError(OrderServiceError):
    pass


class AddressNotFoundError(OrderServiceError):
    pass


class AddressCustomerMismatchError(OrderServiceError):
    pass


class ProductNotFoundError(OrderServiceError):
    pass


class InactiveProductError(OrderServiceError):
    pass


class OrderStatusNotFoundError(OrderServiceError):
    pass


class DeliveryRouteNotFoundError(OrderServiceError):
    pass


class FinalizedOrderError(OrderServiceError):
    pass


@dataclass
class OrderItemInput:
    product_id: UUID
    quantity: Decimal
    unit_price: Decimal | None = None


@dataclass
class ValidatedOrderItem:
    product: Product
    quantity: Decimal
    unit_price: Decimal
    line_total: Decimal


def _generate_order_number(db: Session) -> str:
    for _ in range(10):
        order_number = f"ORD-{datetime.now(UTC):%Y%m%d}-{uuid4().hex[:12].upper()}"
        if order_repository.get_order_by_number(db, order_number) is None:
            return order_number
    raise OrderServiceError("Could not generate a unique order number.")


def _validate_items(db: Session, items: list[OrderItemInput]) -> list[ValidatedOrderItem]:
    if not items:
        raise OrderServiceError("Order must contain at least one item.")

    validated_items: list[ValidatedOrderItem] = []
    for item in items:
        if item.quantity <= 0:
            raise OrderServiceError("Item quantity must be greater than zero.")

        product = order_repository.get_product_by_id(db, item.product_id)
        if product is None:
            raise ProductNotFoundError("Product not found.")
        if not product.is_active:
            raise InactiveProductError("Inactive products cannot be ordered.")

        unit_price = item.unit_price if item.unit_price is not None else product.price
        if unit_price < 0:
            raise OrderServiceError("Item unit price cannot be negative.")

        validated_items.append(
            ValidatedOrderItem(
                product=product,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=item.quantity * unit_price,
            )
        )

    return validated_items


def create_order(
    db: Session,
    *,
    customer_id: UUID,
    address_id: UUID,
    items: list[OrderItemInput],
    notes: str | None = None,
    delivery_route_id: UUID | None = None,
) -> Order:
    customer = order_repository.get_customer_by_id(db, customer_id)
    if customer is None:
        raise CustomerNotFoundError("Customer not found.")

    address = order_repository.get_address_by_id(db, address_id)
    if address is None:
        raise AddressNotFoundError("Address not found.")
    if address.customer_id != customer_id:
        raise AddressCustomerMismatchError("Address does not belong to customer.")

    if (
        delivery_route_id is not None
        and order_repository.get_delivery_route_by_id(db, delivery_route_id) is None
    ):
        raise DeliveryRouteNotFoundError("Delivery route not found.")

    pending_status = order_repository.get_status_by_code(db, PENDING_STATUS_CODE)
    if pending_status is None:
        raise OrderStatusNotFoundError("Pending order status is not configured.")

    validated_items = _validate_items(db, items)
    subtotal = sum((item.line_total for item in validated_items), start=ZERO_AMOUNT)
    delivery_fee = ZERO_AMOUNT
    total = subtotal + delivery_fee

    order = order_repository.create_order(
        db,
        order_number=_generate_order_number(db),
        customer_id=customer_id,
        customer_address_id=address_id,
        order_status_id=pending_status.id,
        delivery_route_id=delivery_route_id,
        notes=notes,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
        confirmed_at=datetime.now(UTC),
    )

    for item in validated_items:
        order_repository.create_order_item(
            db,
            order_id=order.id,
            product_id=item.product.id,
            product_name_snapshot=item.product.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
        )

    record_action(
        db,
        entity_type="order",
        entity_id=order.id,
        customer_id=customer_id,
        order_id=order.id,
        action_type="order_created",
        description="Order created.",
        new_value={
            "order_number": order.order_number,
            "status_code": PENDING_STATUS_CODE,
            "total": str(total),
        },
    )
    db.flush()
    return get_order(db, order.id)


def get_order(db: Session, order_id: UUID) -> Order:
    order = order_repository.get_order_by_id(db, order_id)
    if order is None:
        raise OrderNotFoundError("Order not found.")
    return order


def list_orders(
    db: Session,
    *,
    customer_id: UUID | None = None,
    status_code: str | None = None,
) -> list[Order]:
    if status_code is not None and order_repository.get_status_by_code(db, status_code) is None:
        raise OrderStatusNotFoundError("Order status not found.")
    return order_repository.list_orders(
        db,
        customer_id=customer_id,
        status_code=status_code,
    )


def update_order_status(db: Session, *, order_id: UUID, status_code: str) -> Order:
    order = get_order(db, order_id)
    if order.status.is_final:
        raise FinalizedOrderError("Finalized orders cannot change status.")

    new_status = order_repository.get_status_by_code(db, status_code)
    if new_status is None:
        raise OrderStatusNotFoundError("Order status not found.")

    old_status_code = order.status.code
    order_repository.update_order_status(db, order, new_status)
    record_action(
        db,
        entity_type="order",
        entity_id=order.id,
        customer_id=order.customer_id,
        order_id=order.id,
        action_type="order_status_changed",
        description="Order status changed.",
        old_value={"status_code": old_status_code},
        new_value={"status_code": new_status.code},
    )
    return get_order(db, order.id)


def cancel_order(db: Session, *, order_id: UUID) -> Order:
    order = get_order(db, order_id)
    if order.status.is_final:
        raise FinalizedOrderError("Finalized orders cannot be cancelled.")

    cancelled_status = order_repository.get_status_by_code(db, CANCELLED_STATUS_CODE)
    if cancelled_status is None:
        raise OrderStatusNotFoundError("Cancelled order status is not configured.")

    old_status_code = order.status.code
    order_repository.update_order_status(db, order, cancelled_status)
    record_action(
        db,
        entity_type="order",
        entity_id=order.id,
        customer_id=order.customer_id,
        order_id=order.id,
        action_type="order_cancelled",
        description="Order cancelled.",
        old_value={"status_code": old_status_code},
        new_value={"status_code": CANCELLED_STATUS_CODE},
    )
    return get_order(db, order.id)
