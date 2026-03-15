"""CRUD operations for items."""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.item import Item, ItemCreate, ItemUpdate


def create_item(session: Session, item: ItemCreate, owner_id: int) -> Item:
    db_item = Item(**item.model_dump(), owner_id=owner_id)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def get_item(session: Session, item_id: int) -> Optional[Item]:
    return session.get(Item, item_id)


def get_items(
    session: Session,
    owner_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Item]:
    stmt = select(Item)
    if owner_id is not None:
        stmt = stmt.where(Item.owner_id == owner_id)
    stmt = stmt.order_by(Item.created_at.desc()).offset(skip).limit(limit)
    return list(session.execute(stmt).scalars().all())


def get_items_count(session: Session, owner_id: Optional[int] = None) -> int:
    stmt = select(func.count()).select_from(Item)
    if owner_id is not None:
        stmt = stmt.where(Item.owner_id == owner_id)
    return session.execute(stmt).scalar_one()


def update_item(session: Session, db_item: Item, item_update: ItemUpdate) -> Item:
    for key, value in item_update.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
    db_item.updated_at = datetime.utcnow()
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def delete_item(session: Session, db_item: Item) -> None:
    session.delete(db_item)
    session.commit()
