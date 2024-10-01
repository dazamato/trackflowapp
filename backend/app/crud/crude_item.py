import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.item_model import Item, ItemCreate, ItemUpdate
from app.backend_pre_start import logger


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    def create_item(self, session: Session, item_in: ItemCreate, business_id: uuid.UUID, product_id: uuid.UUID) -> Item:
        db_item = Item.model_validate(item_in, update={"business_id": business_id, "product_id": product_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
item_crud = CRUDItem(Item)
