from sqlalchemy.sql.operators import is_associative
from typing_extensions import Optional
import uuid
from typing import Any
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select
from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id
from app.models.business_model import (Business, BusinessCreate, BusinessPublic, BusinessPublic
    , BusinessUpdate, BusinessesPublic, BusinessCreateSolo)
from app.models.employee_model import EmployeeCreate, Employee
from app.models.business_industry_model import BusinessIndustryPublicId
from app.models.base import Message
from app.crud.crud_business import business_crud
from app.crud.crud_employee import employee_crud
import logging
from fastapi.encoders import jsonable_encoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()



@router.get("/", response_model=BusinessPublic)
def read_my_business(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve businesses by user.
    """
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(status_code=404, detail="User not registered as employee in any Business")
    return business


@router.get("/by_id/{id}", response_model=BusinessPublic)
def read_business(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get business by ID.
    """
    business = session.get(Business, id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.get("/all/", response_model=BusinessesPublic)
def read_all_businesses(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve businesses.
    """
    count_statement = select(func.count()).select_from(Business)
    count = session.exec(count_statement).one()
    statement = select(Business).offset(skip).limit(limit)
    businesses = session.exec(statement).all()
    return BusinessesPublic(data=businesses, count=count)


@router.post("/", response_model=BusinessPublic)
def create_business_with_industry_employee(
    *, session: SessionDep, current_user: CurrentUser, business_in: BusinessCreate
) -> Any:
    """
    Create new business.
    """
    if current_user.is_superuser:
        business = business_crud.create_business(session, business_in=business_in, business_industry_id=business_in.business_industry_id)
    else:
        business_existing = retrieve_businesses_by_user_id(session, current_user.id)
        if business_existing:
            raise HTTPException(status_code=400, detail="User is already registered in a business")
        business = business_crud.create_business(session, business_in=business_in, business_industry_id=business_in.business_industry_id)
        obj_in_data = jsonable_encoder(business_in.employee_in)
        obj_in_data["business_id"] = business.id
        employee_in = EmployeeCreate(**obj_in_data)
        employee_crud.create_employee(session, employee_in=employee_in, business_id=business.id, user_id=current_user.id)
    return business

@router.post("/without_industry/", response_model=BusinessPublic)
def create_business_without_industry(
    *, session: SessionDep, current_user: CurrentUser, business_in: BusinessCreateSolo
) -> Any:
    """
    Create new business.
    """
    business = business_crud.create_business(session, business_in=business_in, business_industry_id=None)
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
    business_accessed = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not current_user.is_superuser and (business.id != business_accessed.id):
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
    business_accessed = retrieve_businesses_by_user_id(session, current_user.id)
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if not current_user.is_superuser and (business.id != business_accessed.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(business)
    session.commit()
    return Message(message="Business deleted successfully")
