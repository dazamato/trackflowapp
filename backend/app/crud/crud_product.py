import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.product_model import Product, ProductCreate, ProductUpdate
from app.backend_pre_start import logger


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def create_product(self, session: Session, product_in: ProductCreate, creator_id: uuid.UUID, product_group: uuid.UUID) -> Product:
        db_item = Product.model_validate(product_in, update={"creator_id": creator_id, "product_group": product_group})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
product_crud = CRUDProduct(Product)
