import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id
from app.models.lead_model import Lead, LeadCreate, LeadPublic, LeadsPublic, LeadUpdate
from app.models.base import Message
from app.crud.crud_lead import lead_crud

router = APIRouter()


@router.get("/", response_model=LeadsPublic)
def read_leads_of_business(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve leads of business.
    """
    # get business in which user is registered as employee
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )


    count_statement = (
        select(func.count())
        .select_from(Lead)
        .where(Lead.business_id == business.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Lead)
        .where(Lead.business_id == business.id)
        .offset(skip)
        .limit(limit)
    )
    leads = session.exec(statement).all()

    return LeadsPublic(data=leads, count=count)


@router.get("/{id}", response_model=LeadPublic)
def read_lead(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get lead by ID.
    """
    lead = session.get(Lead, id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        if not current_user.is_superuser and (lead.business_id != business.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
    return lead


@router.post("/", response_model=LeadPublic)
def create_lead(
    *, session: SessionDep, current_user: CurrentUser, lead_in: LeadCreate
) -> Any:
    """
    Create new lead.
    """
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = lead_crud.create_lead(session, lead_in)
    return lead


@router.put("/{id}", response_model=LeadPublic)
def update_lead(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    lead_in: LeadUpdate,
) -> Any:
    """
    Update an lead.
    """
    lead = session.get(Lead, id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    if not current_user.is_superuser and (lead.business_id != business.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = lead_in.model_dump(exclude_unset=True)
    lead.sqlmodel_update(update_dict)
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


@router.delete("/{id}")
def delete_lead(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an lead.
    """
    lead = session.get(Lead, id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    if not current_user.is_superuser and (lead.business_id != business.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(lead)
    session.commit()
    return Message(message="Lead deleted successfully")
