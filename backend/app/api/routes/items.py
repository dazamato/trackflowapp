import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, retrieve_first_business_by_user_id
from app.models.item_model import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.models.base import Message
from app.crud.crude_item import item_crud

router = APIRouter()


@router.get("/", response_model=ItemsPublic)
def read_all_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    # get business in which user is registered as employee
    business = retrieve_first_business_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == business.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where(Item.owner_id == business.id)
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()

    return ItemsPublic(data=items, count=count)


@router.get("/by_product/", response_model=ItemsPublic)
def read_products_items(
    session: SessionDep, current_user: CurrentUser, product_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    # get business in which user is registered as employee
    business = retrieve_first_business_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Item)
        count = session.exec(count_statement).one()
        statement = select(Item).offset(skip).limit(limit)
        items = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Item)
            .where((Item.owner_id == business.id) & (Item.product_id == product_id))
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Item)
            .where((Item.owner_id == business.id) & (Item.product_id == product_id))
            .offset(skip)
            .limit(limit)
        )
        items = session.exec(statement).all()
    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    business = retrieve_first_business_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    else:
        if not current_user.is_superuser and (item.owner_id != business.id):
            raise HTTPException(status_code=400, detail="Not enough permissions")
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    business = retrieve_first_business_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    item = item_crud.create_item(session, item_in, business.id, item_in.product_id)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    business = retrieve_first_business_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    if not current_user.is_superuser and (item.owner_id != business.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = item_in.model_dump(exclude_unset=True)
    item.sqlmodel_update(update_dict)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    business = retrieve_first_business_by_user_id(session, current_user.id)
    if not business:
        raise HTTPException(
            status_code=404,
            detail="User is not registered in any business.",
        )
    if not current_user.is_superuser and (item.owner_id != business.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(item)
    session.commit()
    return Message(message="Item deleted successfully")
