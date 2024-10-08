import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.sale_model import Sale, SaleCreate, SaleUpdate
from app.backend_pre_start import logger


class CRUDSale(CRUDBase[Sale, SaleCreate, SaleUpdate]):
    def create_sale(self, session: Session, sale_in: SaleCreate) -> Sale:
        db_item = Sale.model_validate(sale_in)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
sale_crud = CRUDSale(Sale)