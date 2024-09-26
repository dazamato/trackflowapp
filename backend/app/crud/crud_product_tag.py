# For a new basic set of CRUD operations you could just do
import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.crud.crud_product_tag_link import create_product_tag_link
from app.models.product_tag_model import ProductTag, ProductTagCreate, ProductTagUpdate
from app.models.product_tag_link_model import ProductTagLink
from app.backend_pre_start import logger


class CRUDProductTag(CRUDBase[ProductTag, ProductTagCreate, ProductTagUpdate]):
    def create_product_tag(self, session: Session, product_tag_in: ProductTagCreate, creator_id: uuid.UUID) -> ProductTag:
        db_item = ProductTag.model_validate(product_tag_in, update={"creator_id": creator_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
product_tag_crud = CRUDProductTag(ProductTag)
