from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import DbSession
from app.core.exceptions import ApiError, ErrorCode
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services.products import (
    DuplicateProductSkuError,
    ProductNotFoundError,
    ProductServiceError,
    create_product,
    deactivate_product,
    get_product,
    list_products,
    search_products,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])


def _product_business_error(exc: ProductServiceError) -> ApiError:
    code = (
        ErrorCode.PRODUCT_INVALID_PRICE
        if "price" in str(exc).lower()
        else ErrorCode.BUSINESS_RULE_ERROR
    )
    return ApiError(
        status_code=status.HTTP_400_BAD_REQUEST,
        code=code,
        message=str(exc),
    )


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: DbSession):
    try:
        product = create_product(db, **payload.model_dump())
        db.commit()
        db.refresh(product)
        return product
    except DuplicateProductSkuError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.PRODUCT_SKU_ALREADY_EXISTS,
            message=str(exc),
        ) from exc
    except ProductServiceError as exc:
        db.rollback()
        raise _product_business_error(exc) from exc


@router.get("", response_model=list[ProductResponse])
def list_products_endpoint(
    db: DbSession,
    active_only: bool = Query(default=False),
):
    return list_products(db, active_only=active_only)


@router.get("/search", response_model=list[ProductResponse])
def search_products_endpoint(
    db: DbSession,
    name: str | None = Query(default=None),
    sku: str | None = Query(default=None),
):
    if not any([name, sku]):
        raise ApiError(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ErrorCode.BUSINESS_RULE_ERROR,
            message="At least one search criterion is required.",
        )
    return search_products(db, name=name, sku=sku)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(product_id: UUID, db: DbSession):
    try:
        return get_product(db, product_id)
    except ProductNotFoundError as exc:
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.PRODUCT_NOT_FOUND,
            message=str(exc),
        ) from exc


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(product_id: UUID, payload: ProductUpdate, db: DbSession):
    try:
        product = update_product(
            db,
            product_id=product_id,
            values=payload.model_dump(exclude_unset=True),
        )
        db.commit()
        db.refresh(product)
        return product
    except DuplicateProductSkuError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_409_CONFLICT,
            code=ErrorCode.PRODUCT_SKU_ALREADY_EXISTS,
            message=str(exc),
        ) from exc
    except ProductNotFoundError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.PRODUCT_NOT_FOUND,
            message=str(exc),
        ) from exc
    except ProductServiceError as exc:
        db.rollback()
        raise _product_business_error(exc) from exc


@router.patch("/{product_id}/deactivate", response_model=ProductResponse)
def deactivate_product_endpoint(product_id: UUID, db: DbSession):
    try:
        product = deactivate_product(db, product_id=product_id)
        db.commit()
        db.refresh(product)
        return product
    except ProductNotFoundError as exc:
        db.rollback()
        raise ApiError(
            status_code=status.HTTP_404_NOT_FOUND,
            code=ErrorCode.PRODUCT_NOT_FOUND,
            message=str(exc),
        ) from exc
