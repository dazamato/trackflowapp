import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id
from app.models.address_model import Address, AddressCreate, AddressPublic, AddressesPublic, AddressUpdate
from app.models.product_model import Product
from app.models.base import Message
from app.models.lead_model import Lead
from app.crud.crud_address import address_crud


router = APIRouter()


@router.get("/{lead_id}", response_model=AddressesPublic)
def read_addresses_of_lead(
    session: SessionDep, current_user: CurrentUser, lead_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve addresses of business.
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
            .select_from(Address)
            .where(Address.lead_id == lead.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Address)
            .where(Address.lead_id == lead.id)
            .offset(skip)
            .limit(limit)
        )
        addresses = session.exec(statement).all()
        return AddressesPublic(data=addresses, count=count)
    else:
        raise HTTPException(
            status_code=404,
            detail="lead not founded!",
        )


@router.get("/by/{id}", response_model=AddressPublic)
def read_address(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get address by ID.
    """
    address = session.get(Address, id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        statement = (
            select(Address)
            .join(Lead)
            .where(Lead.business_id==business.id and Address.id == address.id)
        )
        address_exist = session.exec(statement).first()
        if not current_user.is_superuser and not address_exist:
            raise HTTPException(status_code=400, detail="Not enough permissions")
    return address


@router.post("/", response_model=AddressPublic)
def create_address(
    *, session: SessionDep, current_user: CurrentUser, address_in: AddressCreate
) -> Any:
    """
    Create new address.
    """
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        lead = session.get(Lead, address_in.lead_id)
        if lead:
            if business.id != lead.business_id:
                raise HTTPException(
                    status_code=400,
                    detail="Premission denied",
                )
            else:
                address = address_crud.create_address(session, address_in)
                return address
        else:
            raise HTTPException(
                    status_code=404,
                    detail="Lead not founded",
                )


@router.put("/{id}", response_model=AddressPublic)
def update_address(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    address_in: AddressUpdate,
) -> Any:
    """
    Update an address.
    """
    address = session.get(Address, id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, address.lead_id)
    if not current_user.is_superuser and business.id != lead.business_id:
        raise HTTPException(
            status_code=400,
            detail="Premission denied",
        )
    update_dict = address_in.model_dump(exclude_unset=True)
    address.sqlmodel_update(update_dict)
    session.add(address)
    session.commit()
    session.refresh(address)
    return address


@router.delete("/{id}")
def delete_address(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an address.
    """
    address = session.get(Address, id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, address.lead_id)
    if not current_user.is_superuser and business.id != lead.business_id:
        raise HTTPException(
            status_code=400,
            detail="Premission denied",
        )
    session.delete(address)
    session.commit()
    return Message(message="Address deleted successfully")
