from typing_extensions import Optional
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.business_model import Business, BusinessCreate, BusinessPublic, BusinessPublic, BusinessUpdate, BusinessesPublic
from app.models.business_industry_model import BusinessIndustryPublicId
from app.models.base import Message
from app.crud.crud_business import business_crud

router = APIRouter()


@router.get("/", response_model=BusinessesPublic)
def read_my_businesses(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve businesses.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Business)
        count = session.exec(count_statement).one()
        statement = select(Business).offset(skip).limit(limit)
        businesses = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Business)
            .where(Business.account_creator_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Business)
            .where(Business.account_creator_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        businesses = session.exec(statement).all()

    return BusinessesPublic(data=businesses, count=count)


@router.get("/{id}", response_model=BusinessPublic)
def read_business(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get business by ID.
    """
    business = session.get(Business, id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not current_user.is_superuser and (business.account_creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return business


@router.post("/", response_model=BusinessPublic)
def create_business_with_industry(
    *, session: SessionDep, current_user: CurrentUser, business_in: BusinessCreate, business_industry_id: BusinessIndustryPublicId
) -> Any:
    """
    Create new business.
    """
    print(business_industry_id)
    business = business_crud.create_business(session, business_in=business_in, account_creator_id=current_user.id
        , business_industry_id=business_industry_id.id)
    return business

@router.post("/without_industry/", response_model=BusinessPublic)
def create_business_without_industry(
    *, session: SessionDep, current_user: CurrentUser, business_in: BusinessCreate
) -> Any:
    """
    Create new business.
    """
    business = business_crud.create_business(session, business_in=business_in, account_creator_id=current_user.id, business_industry_id=None)
    return business


@router.put("/{id}", response_model=BusinessPublic)
def update_business(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    business_in: BusinessUpdate,
) -> Any:
    """
    Update an business.
    """
    business = session.get(Business, id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not current_user.is_superuser and (business.account_creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = business_in.model_dump(exclude_unset=True)
    business.sqlmodel_update(update_dict)
    session.add(business)
    session.commit()
    session.refresh(business)
    return business


@router.delete("/{id}")
def delete_business(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an business.
    """
    business = session.get(Business, id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not current_user.is_superuser and (business.account_creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(business)
    session.commit()
    return Message(message="Business deleted successfully")
