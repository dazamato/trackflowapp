# For a new basic set of CRUD operations you could just do
import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.business_industry_model import BusinessIndustry, BusinessIndustryCreate, BusinessIndustryUpdate
from app.backend_pre_start import logger


class CRUDBusinessIndustry(CRUDBase[BusinessIndustry, BusinessIndustryCreate, BusinessIndustryUpdate]):
    def create_business_industry(self, session: Session, business_industry_in: BusinessIndustryCreate, creator_id: uuid.UUID) -> BusinessIndustry:
        db_item = BusinessIndustry.model_validate(business_industry_in, update={"creator_id": creator_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
business_industry_crud = CRUDBusinessIndustry(BusinessIndustry)
