from collections.abc import Mapping
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def create_product(
    db: Session,
    *,
    sku: str,
    name: str,
    normalized_name: str,
    description: str | None,
    unit: str,
    price,
    is_active: bool = True,
) -> Product:
    product = Product(
        sku=sku,
        name=name,
        normalized_name=normalized_name,
        description=description,
        unit=unit,
        price=price,
        is_active=is_active,
    )
    db.add(product)
    db.flush()
    return product


def get_product_by_id(db: Session, product_id: UUID) -> Product | None:
    return db.scalar(select(Product).where(Product.id == product_id))


def get_product_by_sku(db: Session, sku: str) -> Product | None:
    return db.scalar(select(Product).where(Product.sku == sku))


def list_products(db: Session, *, active_only: bool = False) -> list[Product]:
    statement = select(Product).order_by(Product.name)
    if active_only:
        statement = statement.where(Product.is_active.is_(True))
    return list(db.scalars(statement).all())


def find_products_by_normalized_name(db: Session, normalized_name: str) -> list[Product]:
    statement = (
        select(Product)
        .where(Product.normalized_name == normalized_name)
        .order_by(Product.name)
    )
    return list(db.scalars(statement).all())


def update_product(db: Session, product: Product, values: Mapping[str, Any]) -> Product:
    for field_name, value in values.items():
        setattr(product, field_name, value)
    db.flush()
    return product


def deactivate_product(db: Session, product: Product) -> Product:
    product.is_active = False
    db.flush()
    return product
