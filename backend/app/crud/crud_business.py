import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.business_model import Business, BusinessCreate, BusinessUpdate
from app.backend_pre_start import logger


class CRUDBusiness(CRUDBase[Business, BusinessCreate, BusinessUpdate]):
    def create_business(self, session: Session, business_in: BusinessCreate, account_creator_id: uuid.UUID, business_industry_id: Optional[uuid.UUID]) -> Business:
        if business_industry_id:
            db_item = Business.model_validate(business_in, update={"account_creator_id": account_creator_id, "business_industry_id": business_industry_id})
        else:
            db_item = Business.model_validate(business_in, update={"account_creator_id": account_creator_id, "business_industry_id": None})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
business_crud = CRUDBusiness(Business)
