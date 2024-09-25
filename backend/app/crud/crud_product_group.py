# For a new basic set of CRUD operations you could just do
import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.product_group_model import ProductGroup, ProductGroupCreate, ProductGroupUpdate
from app.backend_pre_start import logger


class CRUDProductGroup(CRUDBase[ProductGroup, ProductGroupCreate, ProductGroupUpdate]):
    def create_product_group(self, session: Session, product_group_in: ProductGroupCreate, creator_id: uuid.UUID) -> ProductGroup:
        db_item = ProductGroup.model_validate(product_group_in, update={"creator_id": creator_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
product_group_crud = CRUDProductGroup(ProductGroup)
