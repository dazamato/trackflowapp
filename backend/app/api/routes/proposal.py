import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id
from app.models.proposal_model import Proposal, ProposalCreate, ProposalPublic, ProposalsPublic, ProposalUpdate
from app.models.product_model import Product
from app.models.base import Message
from app.models.lead_model import Lead
from app.crud.crud_proposal import proposal_crud


router = APIRouter()


@router.get("/{lead_id}", response_model=ProposalsPublic)
def read_proposals_of_lead(
    session: SessionDep, current_user: CurrentUser, lead_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve proposals of business.
    """
    # get business in which user is registered as employee
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, lead_id)
    # check if lead belongs of users business
    if lead:
        if business.id != lead.business_id:
            raise HTTPException(
                status_code=400,
                detail="Permission denied",
            )
        count_statement = (
            select(func.count())
            .select_from(Proposal)
            .where(Proposal.lead_id == lead.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Proposal)
            .where(Proposal.lead_id == lead.id)
            .offset(skip)
            .limit(limit)
        )
        proposals = session.exec(statement).all()
        return ProposalsPublic(data=proposals, count=count)
    else:
        raise HTTPException(
            status_code=404,
            detail="lead not founded!",
        )


@router.get("/by/{id}", response_model=ProposalPublic)
def read_proposal(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get proposal by ID.
    """
    proposal = session.get(Proposal, id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        statement = (
            select(Proposal)
            .join(Lead)
            .where(Lead.business_id==business.id and Proposal.id == proposal.id)
        )
        proposal_exist = session.exec(statement).first()
        if not current_user.is_superuser and not proposal_exist:
            raise HTTPException(status_code=400, detail="Not enough permissions")
    return proposal


@router.post("/", response_model=ProposalPublic)
def create_proposal(
    *, session: SessionDep, current_user: CurrentUser, proposal_in: ProposalCreate
) -> Any:
    """
    Create new proposal.
    """
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        lead = session.get(Lead, proposal_in.lead_id)
        if lead:
            if business.id != lead.business_id:
                raise HTTPException(
                    status_code=400,
                    detail="Premission denied",
                )
            else:
                product = session.get(Product, proposal_in.product_id)
                if not product:
                    raise HTTPException(
                        status_code=404,
                        detail="Product specified not founded, please select existing one",
                    )
                proposal = proposal_crud.create_proposal(session, proposal_in)
                return proposal
        else:
            raise HTTPException(
                    status_code=404,
                    detail="Lead not founded",
                )


@router.put("/{id}", response_model=ProposalPublic)
def update_proposal(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    proposal_in: ProposalUpdate,
) -> Any:
    """
    Update an proposal.
    """
    proposal = session.get(Proposal, id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, proposal.lead_id)
    if not current_user.is_superuser and business.id != lead.business_id:
        raise HTTPException(
            status_code=400,
            detail="Premission denied",
        )
    update_dict = proposal_in.model_dump(exclude_unset=True)
    proposal.sqlmodel_update(update_dict)
    session.add(proposal)
    session.commit()
    session.refresh(proposal)
    return proposal


@router.delete("/{id}")
def delete_proposal(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an proposal.
    """
    proposal = session.get(Proposal, id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, proposal.lead_id)
    if not current_user.is_superuser and business.id != lead.business_id:
        raise HTTPException(
            status_code=400,
            detail="Premission denied",
        )
    session.delete(proposal)
    session.commit()
    return Message(message="Proposal deleted successfully")
