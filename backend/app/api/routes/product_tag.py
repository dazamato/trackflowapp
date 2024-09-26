import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.product_tag_model import ProductTag, ProductTagCreate, ProductTagPublic, ProductTagUpdate, ProductTagsPublic
from app.models.base import Message
from app.models.product_model import Product
from app.models.product_tag_link_model import ProductTagLink
from app.crud.crud_product_tag import product_tag_crud

router = APIRouter()

@router.get("/", response_model=ProductTagsPublic)
def read_product_tags(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve product_tags.
    """
    count_statement = select(func.count()).select_from(ProductTag)
    count = session.exec(count_statement).one()
    statement = select(ProductTag).offset(skip).limit(limit)
    product_tags = session.exec(statement).all()
    return ProductTagsPublic(data=product_tags, count=count)

@router.get("/self/", response_model=ProductTagsPublic)
def read_product_tags_self(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve product_tags.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(ProductTag)
        count = session.exec(count_statement).one()
        statement = select(ProductTag).offset(skip).limit(limit)
        product_tags = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(ProductTag)
            .where(ProductTag.creator_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(ProductTag)
            .where(ProductTag.creator_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        product_tags = session.exec(statement).all()

    return ProductTagsPublic(data=product_tags, count=count)

@router.get("/ofproduct/", response_model=ProductTagsPublic)
def read_product_tags_of_product(
    session: SessionDep, current_user: CurrentUser, product_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve product_tags.
    """
    count_statement = (
        select(func.count())
        .select_from(
            select(ProductTag).distinct()
            .join(ProductTagLink)
            .where(ProductTagLink.product_id == product_id)
        )
    )
    count = session.exec(count_statement).one()
    statement = (
        select(ProductTag)
        .join(ProductTagLink)
        .where(ProductTagLink.product_id == product_id)
        .offset(skip)
        .limit(limit)
    )
    product_tags = session.exec(statement).all()
    return ProductTagsPublic(data=product_tags, count=count)

@router.get("/{id}", response_model=ProductTagPublic)
def read_product_tag(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get product_tag by ID.
    """
    product_tag = session.get(ProductTag, id)
    if not product_tag:
        raise HTTPException(status_code=404, detail="ProductTag not found")
    # if not current_user.is_superuser and (product_tag.creator_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")
    return product_tag


@router.post("/", response_model=ProductTagPublic)
def create_product_tag(
    *, session: SessionDep, current_user: CurrentUser, product_tag_in: ProductTagCreate
) -> Any:
    """
    Create new product_tag.
    """
    tags_existing = session.exec(select(ProductTag).where(ProductTag.title == product_tag_in.title)).all()
    if len(tags_existing)>0:
        raise HTTPException(status_code=400, detail="ProductTag already exists")
    product_tag = product_tag_crud.create_product_tag(session, product_tag_in, current_user.id)
    return product_tag


@router.put("/{id}", response_model=ProductTagPublic)
def update_product_tag(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    product_tag_in: ProductTagUpdate,
) -> Any:
    """
    Update an product_tag.
    """
    product_tag = session.get(ProductTag, id)
    if not product_tag:
        raise HTTPException(status_code=404, detail="ProductTag not found")
    if not current_user.is_superuser and (product_tag.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = product_tag_in.model_dump(exclude_unset=True)
    product_tag.sqlmodel_update(update_dict)
    session.add(product_tag)
    session.commit()
    session.refresh(product_tag)
    return product_tag


@router.delete("/{id}")
def delete_product_tag(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an product_tag.
    """
    product_tag = session.get(ProductTag, id)
    if not product_tag:
        raise HTTPException(status_code=404, detail="ProductTag not found")
    if not current_user.is_superuser and (product_tag.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(product_tag)
    session.commit()
    return Message(message="ProductTag deleted successfully")
