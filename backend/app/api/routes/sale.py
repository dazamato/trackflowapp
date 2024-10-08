import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id
from app.models.sale_model import Sale, SaleCreate, SalePublic, SalesPublic, SaleUpdate
from app.models.product_model import Product
from app.models.item_model import Item, ItemUpdate
from app.models.base import Message
from app.models.lead_model import Lead
from app.crud.crud_sale import sale_crud


router = APIRouter()


@router.get("/{lead_id}", response_model=SalesPublic)
def read_sales_of_lead(
    session: SessionDep, current_user: CurrentUser, lead_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve sales of business.
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
            .select_from(Sale)
            .where(Sale.lead_id == lead.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Sale)
            .where(Sale.lead_id == lead.id)
            .offset(skip)
            .limit(limit)
        )
        sales = session.exec(statement).all()
        return SalesPublic(data=sales, count=count)
    else:
        raise HTTPException(
            status_code=404,
            detail="lead not founded!",
        )


@router.get("/by/{id}", response_model=SalePublic)
def read_sale(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get sale by ID.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        statement = (
            select(Sale)
            .join(Lead)
            .where(Lead.business_id==business.id and Sale.id == sale.id)
        )
        sale_exist = session.exec(statement).first()
        if not current_user.is_superuser and not sale_exist:
            raise HTTPException(status_code=400, detail="Not enough permissions")
    return sale


@router.post("/", response_model=SalePublic)
def create_sale(
    *, session: SessionDep, current_user: CurrentUser, sale_in: SaleCreate
) -> Any:
    """
    Create new sale.
    """
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        lead = session.get(Lead, sale_in.lead_id)
        if lead:
            if business.id != lead.business_id:
                raise HTTPException(
                    status_code=400,
                    detail="Premission denied",
                )
            else:
                item = session.get(Item, sale_in.item_id)
                if not item:
                    raise HTTPException(
                        status_code=404,
                        detail="Item specified not founded, please select existing one",
                    )
                
                # reduce items quantity
                q = item.quantity - sale_in.quantity_of_items
                if q < 0:
                    raise HTTPException(
                        status_code=404,
                        detail="Items not enough to sale",
                    )
                sale = sale_crud.create_sale(session, sale_in)    
                upd = ItemUpdate(quantity=q)
                update_dict = upd.model_dump(exclude_unset=True)
                item.sqlmodel_update(update_dict)
                session.add(item)
                session.commit()
                session.refresh(item)
                return sale
        else:
            raise HTTPException(
                    status_code=404,
                    detail="Lead not founded",
                )


@router.put("/{id}", response_model=SalePublic)
def update_sale(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    sale_in: SaleUpdate,
) -> Any:
    """
    Update an sale.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, sale.lead_id)
    if not current_user.is_superuser and business.id != lead.business_id:
        raise HTTPException(
            status_code=400,
            detail="Premission denied",
        )
    update_dict = sale_in.model_dump(exclude_unset=True)
    sale.sqlmodel_update(update_dict)
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale


@router.delete("/{id}")
def delete_sale(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an sale.
    """
    sale = session.get(Sale, id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    lead = session.get(Lead, sale.lead_id)
    if not current_user.is_superuser and business.id != lead.business_id:
        raise HTTPException(
            status_code=400,
            detail="Premission denied",
        )
    session.delete(sale)
    session.commit()
    return Message(message="Sale deleted successfully")
