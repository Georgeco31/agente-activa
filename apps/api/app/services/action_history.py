from uuid import UUID

from sqlalchemy.orm import Session

from app.models.action_history import ActionHistory
from app.repositories.action_history import create_action_history


def record_action(
    db: Session,
    *,
    entity_type: str,
    entity_id: UUID,
    action_type: str,
    description: str | None = None,
    customer_id: UUID | None = None,
    order_id: UUID | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    performed_by_type: str = "system",
    performed_by_id: str | None = None,
) -> ActionHistory:
    return create_action_history(
        db,
        entity_type=entity_type,
        entity_id=entity_id,
        action_type=action_type,
        description=description,
        customer_id=customer_id,
        order_id=order_id,
        old_value=old_value,
        new_value=new_value,
        performed_by_type=performed_by_type,
        performed_by_id=performed_by_id,
    )
