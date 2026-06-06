from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.order_status import OrderStatus

BASE_ORDER_STATUSES = [
    {"code": "pendiente", "name": "Pendiente", "sort_order": 1, "is_final": False},
    {"code": "asignado", "name": "Asignado", "sort_order": 2, "is_final": False},
    {"code": "en_camino", "name": "En camino", "sort_order": 3, "is_final": False},
    {"code": "entregado", "name": "Entregado", "sort_order": 4, "is_final": True},
    {"code": "no_entregado", "name": "No entregado", "sort_order": 5, "is_final": True},
    {"code": "cancelado", "name": "Cancelado", "sort_order": 6, "is_final": True},
]


def seed_order_statuses(db: Session) -> None:
    for status_data in BASE_ORDER_STATUSES:
        status = db.scalar(
            select(OrderStatus).where(OrderStatus.code == status_data["code"])
        )

        if status is None:
            db.add(OrderStatus(**status_data))
            continue

        status.name = status_data["name"]
        status.sort_order = status_data["sort_order"]
        status.is_final = status_data["is_final"]

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed_order_statuses(db)


if __name__ == "__main__":
    main()
