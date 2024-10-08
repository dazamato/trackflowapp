import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.proposal_model import Proposal, ProposalCreate, ProposalUpdate
from app.backend_pre_start import logger


class CRUDProposal(CRUDBase[Proposal, ProposalCreate, ProposalUpdate]):
    def create_proposal(self, session: Session, proposal_in: ProposalCreate) -> Proposal:
        db_item = Proposal.model_validate(proposal_in)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
proposal_crud = CRUDProposal(Proposal)