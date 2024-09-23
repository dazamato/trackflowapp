import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.business_industry_model import BusinessIndustry, BusinessIndustryCreate, BusinessIndustryPublic, BusinessIndustryUpdate, BusinessIndustriesPublic
from app.models.base import Message
from app.crud.crud_business_industry import business_industry_crud

router = APIRouter()


@router.get("/", response_model=BusinessIndustriesPublic)
def read_business_industrys_self(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve business_industrys.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(BusinessIndustry)
        count = session.exec(count_statement).one()
        statement = select(BusinessIndustry).offset(skip).limit(limit)
        business_industrys = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(BusinessIndustry)
            .where(BusinessIndustry.creator_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(BusinessIndustry)
            .where(BusinessIndustry.creator_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        business_industrys = session.exec(statement).all()

    return BusinessIndustriesPublic(data=business_industrys, count=count)


@router.get("/{id}", response_model=BusinessIndustryPublic)
def read_business_industry(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get business_industry by ID.
    """
    business_industry = session.get(BusinessIndustry, id)
    if not business_industry:
        raise HTTPException(status_code=404, detail="BusinessIndustry not found")
    if not current_user.is_superuser and (business_industry.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return business_industry


@router.post("/", response_model=BusinessIndustryPublic)
def create_business_industry(
    *, session: SessionDep, current_user: CurrentUser, business_industry_in: BusinessIndustryCreate
) -> Any:
    """
    Create new business_industry.
    """
    business_industry = business_industry_crud.create_business_industry(session, business_industry_in, current_user.id)
    # business_industry = BusinessIndustry.model_validate(business_industry_in, update={"creator_id": current_user.id})
    # session.add(business_industry)
    # session.commit()
    # session.refresh(business_industry)
    return business_industry


@router.put("/{id}", response_model=BusinessIndustryPublic)
def update_business_industry(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    business_industry_in: BusinessIndustryUpdate,
) -> Any:
    """
    Update an business_industry.
    """
    business_industry = session.get(BusinessIndustry, id)
    if not business_industry:
        raise HTTPException(status_code=404, detail="BusinessIndustry not found")
    if not current_user.is_superuser and (business_industry.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = business_industry_in.model_dump(exclude_unset=True)
    business_industry.sqlmodel_update(update_dict)
    session.add(business_industry)
    session.commit()
    session.refresh(business_industry)
    return business_industry


@router.delete("/{id}")
def delete_business_industry(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an business_industry.
    """
    business_industry = session.get(BusinessIndustry, id)
    if not business_industry:
        raise HTTPException(status_code=404, detail="BusinessIndustry not found")
    if not current_user.is_superuser and (business_industry.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(business_industry)
    session.commit()
    return Message(message="BusinessIndustry deleted successfully")
