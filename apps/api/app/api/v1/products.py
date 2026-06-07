from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import DbSession
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


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(payload: ProductCreate, db: DbSession):
    try:
        product = create_product(db, **payload.model_dump())
        db.commit()
        db.refresh(product)
        return product
    except DuplicateProductSkuError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ProductServiceError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search criterion is required.",
        )
    return search_products(db, name=name, sku=sku)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product_endpoint(product_id: UUID, db: DbSession):
    try:
        return get_product(db, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ProductNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProductServiceError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.patch("/{product_id}/deactivate", response_model=ProductResponse)
def deactivate_product_endpoint(product_id: UUID, db: DbSession):
    try:
        product = deactivate_product(db, product_id=product_id)
        db.commit()
        db.refresh(product)
        return product
    except ProductNotFoundError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
