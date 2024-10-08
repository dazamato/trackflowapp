import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.lead_model import Lead, LeadCreate, LeadUpdate
from app.backend_pre_start import logger


class CRUDLead(CRUDBase[Lead, LeadCreate, LeadUpdate]):
    def create_lead(self, session: Session, lead_in: LeadCreate) -> Lead:
        db_item = Lead.model_validate(lead_in)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
lead_crud = CRUDLead(Lead)
