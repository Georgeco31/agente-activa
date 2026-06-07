from collections.abc import Mapping
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.product import Product
from app.repositories import products as product_repository
from app.services.normalization import normalize_text


class ProductServiceError(ValueError):
    pass


class ProductNotFoundError(ProductServiceError):
    pass


class DuplicateProductSkuError(ProductServiceError):
    pass


def _required_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ProductServiceError(f"{field_name} is required.")
    return cleaned


def _validate_price(price: Decimal) -> None:
    if price < 0:
        raise ProductServiceError("Price cannot be negative.")


def create_product(
    db: Session,
    *,
    sku: str,
    name: str,
    description: str | None,
    unit: str,
    price: Decimal,
    is_active: bool = True,
) -> Product:
    clean_sku = _required_text(sku, "SKU")
    clean_name = _required_text(name, "Name")
    clean_unit = _required_text(unit, "Unit")
    _validate_price(price)

    if product_repository.get_product_by_sku(db, clean_sku) is not None:
        raise DuplicateProductSkuError("Product SKU is already registered.")

    return product_repository.create_product(
        db,
        sku=clean_sku,
        name=clean_name,
        normalized_name=normalize_text(clean_name),
        description=description,
        unit=clean_unit,
        price=price,
        is_active=is_active,
    )


def get_product(db: Session, product_id: UUID) -> Product:
    product = product_repository.get_product_by_id(db, product_id)
    if product is None:
        raise ProductNotFoundError("Product not found.")
    return product


def list_products(db: Session, *, active_only: bool = False) -> list[Product]:
    return product_repository.list_products(db, active_only=active_only)


def search_products(
    db: Session,
    *,
    name: str | None = None,
    sku: str | None = None,
) -> list[Product]:
    matches: dict[UUID, Product] = {}

    if name:
        normalized_name = normalize_text(name)
        if normalized_name:
            for product in product_repository.find_products_by_normalized_name(
                db, normalized_name
            ):
                matches[product.id] = product

    if sku:
        product = product_repository.get_product_by_sku(db, sku.strip())
        if product is not None:
            matches[product.id] = product

    return list(matches.values())


def update_product(
    db: Session,
    *,
    product_id: UUID,
    values: Mapping[str, Any],
) -> Product:
    product = get_product(db, product_id)
    changes = dict(values)

    if "sku" in changes:
        new_sku = _required_text(changes["sku"], "SKU")
        existing = product_repository.get_product_by_sku(db, new_sku)
        if existing is not None and existing.id != product.id:
            raise DuplicateProductSkuError("Product SKU is already registered.")
        changes["sku"] = new_sku

    if "name" in changes:
        clean_name = _required_text(changes["name"], "Name")
        changes["name"] = clean_name
        changes["normalized_name"] = normalize_text(clean_name)

    if "unit" in changes:
        changes["unit"] = _required_text(changes["unit"], "Unit")

    if "price" in changes:
        _validate_price(changes["price"])

    return product_repository.update_product(db, product, changes)


def deactivate_product(db: Session, *, product_id: UUID) -> Product:
    product = get_product(db, product_id)
    return product_repository.deactivate_product(db, product)
