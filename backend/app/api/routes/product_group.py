import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.product_group_model import ProductGroup, ProductGroupCreate, ProductGroupPublic, ProductGroupUpdate, ProductGroupsPublic
from app.models.base import Message
from app.crud.crud_product_group import product_group_crud

router = APIRouter()

@router.get("/", response_model=ProductGroupsPublic)
def read_product_groups(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve product_groups.
    """
    count_statement = select(func.count()).select_from(ProductGroup)
    count = session.exec(count_statement).one()
    statement = select(ProductGroup).offset(skip).limit(limit)
    product_groups = session.exec(statement).all()
    return ProductGroupsPublic(data=product_groups, count=count)

@router.get("/self/", response_model=ProductGroupsPublic)
def read_product_groups_self(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve product_groups.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(ProductGroup)
        count = session.exec(count_statement).one()
        statement = select(ProductGroup).offset(skip).limit(limit)
        product_groups = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(ProductGroup)
            .where(ProductGroup.creator_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(ProductGroup)
            .where(ProductGroup.creator_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        product_groups = session.exec(statement).all()

    return ProductGroupsPublic(data=product_groups, count=count)

@router.get("/{id}", response_model=ProductGroupPublic)
def read_product_group(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get product_group by ID.
    """
    product_group = session.get(ProductGroup, id)
    if not product_group:
        raise HTTPException(status_code=404, detail="ProductGroup not found")
    # if not current_user.is_superuser and (product_group.creator_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    return product_group


@router.post("/", response_model=ProductGroupPublic)
def create_product_group(
    *, session: SessionDep, current_user: CurrentUser, product_group_in: ProductGroupCreate
) -> Any:
    """
    Create new product_group.
    """
    product_group = product_group_crud.create_product_group(session, product_group_in, current_user.id)
    return product_group


@router.put("/{id}", response_model=ProductGroupPublic)
def update_product_group(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    product_group_in: ProductGroupUpdate,
) -> Any:
    """
    Update an product_group.
    """
    product_group = session.get(ProductGroup, id)
    if not product_group:
        raise HTTPException(status_code=404, detail="ProductGroup not found")
    if not current_user.is_superuser and (product_group.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = product_group_in.model_dump(exclude_unset=True)
    product_group.sqlmodel_update(update_dict)
    session.add(product_group)
    session.commit()
    session.refresh(product_group)
    return product_group


@router.delete("/{id}")
def delete_product_group(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an product_group.
    """
    product_group = session.get(ProductGroup, id)
    if not product_group:
        raise HTTPException(status_code=404, detail="ProductGroup not found")
    if not current_user.is_superuser and (product_group.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(product_group)
    session.commit()
    return Message(message="ProductGroup deleted successfully")
