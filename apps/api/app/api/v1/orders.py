from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.core.exceptions import ApiError, ErrorCode
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.orders import (
    AddressCustomerMismatchError,
    AddressNotFoundError,
    CustomerNotFoundError,
    DeliveryRouteNotFoundError,
    FinalizedOrderError,
    InactiveProductError,
    OrderItemInput,
    OrderNotFoundError,
    OrderServiceError,
    OrderStatusNotFoundError,
    ProductNotFoundError,
    cancel_order,
    create_order,
    get_order,
    list_orders,
    update_order_status,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_api_error(exc: OrderServiceError) -> ApiError:
    if isinstance(exc, OrderNotFoundError):
        return ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.ORDER_NOT_FOUND,
            message=str(exc),
        )
    if isinstance(exc, CustomerNotFoundError):
        return ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.CUSTOMER_NOT_FOUND,
            message=str(exc),
        )
    if isinstance(exc, AddressNotFoundError):
        return ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.ORDER_ADDRESS_NOT_FOUND,
            message=str(exc),
        )
    if isinstance(exc, ProductNotFoundError):
        return ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.ORDER_PRODUCT_NOT_FOUND,
            message=str(exc),
        )
    if isinstance(exc, DeliveryRouteNotFoundError):
        return ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.DELIVERY_ROUTE_NOT_FOUND,
            message=str(exc),
        )
    if isinstance(exc, OrderStatusNotFoundError):
        return ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.ORDER_STATUS_NOT_FOUND,
            message=str(exc),
        )
    if isinstance(exc, AddressCustomerMismatchError):
        return ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.ORDER_ADDRESS_NOT_BELONG_TO_CUSTOMER,
            message=str(exc),
        )
    if isinstance(exc, InactiveProductError):
        return ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.ORDER_PRODUCT_INACTIVE,
            message=str(exc),
        )
    if isinstance(exc, FinalizedOrderError):
        return ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.ORDER_ALREADY_FINALIZED,
            message=str(exc),
        )

    message = str(exc)
    if "at least one item" in message.lower():
        code = ErrorCode.ORDER_INVALID_ITEMS
    elif "quantity" in message.lower():
        code = ErrorCode.ORDER_INVALID_QUANTITY
    elif "price" in message.lower():
        code = ErrorCode.ORDER_INVALID_PRICE
    else:
        code = ErrorCode.BUSINESS_RULE_ERROR

    return ApiError(
        status_code=status.HTTP_400_BAD_REQUEST,
        code=code,
        message=message,
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_endpoint(payload: OrderCreate, db: DbSession):
    try:
        order = create_order(
            db,
            customer_id=payload.customer_id,
            address_id=payload.address_id,
            items=[
                OrderItemInput(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in payload.items
            ],
            notes=payload.notes,
            delivery_route_id=payload.delivery_route_id,
        )
        db.commit()
        return order
    except OrderServiceError as exc:
        db.rollback()
        raise _order_api_error(exc) from exc


@router.get("", response_model=list[OrderResponse])
def list_orders_endpoint(
    db: DbSession,
    customer_id: Annotated[UUID | None, Query()] = None,
    status_code: Annotated[str | None, Query()] = None,
):
    try:
        return list_orders(db, customer_id=customer_id, status_code=status_code)
    except OrderStatusNotFoundError as exc:
        raise _order_api_error(exc) from exc


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_endpoint(order_id: UUID, db: DbSession):
    try:
        return get_order(db, order_id)
    except OrderNotFoundError as exc:
        raise _order_api_error(exc) from exc


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status_endpoint(
    order_id: UUID,
    payload: OrderStatusUpdate,
    db: DbSession,
):
    try:
        order = update_order_status(db, order_id=order_id, status_code=payload.status_code)
        db.commit()
        return order
    except OrderServiceError as exc:
        db.rollback()
        raise _order_api_error(exc) from exc


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order_endpoint(order_id: UUID, db: DbSession):
    try:
        order = cancel_order(db, order_id=order_id)
        db.commit()
        return order
    except OrderServiceError as exc:
        db.rollback()
        raise _order_api_error(exc) from exc
