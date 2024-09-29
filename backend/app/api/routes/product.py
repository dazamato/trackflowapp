from typing_extensions import Optional
import uuid
from typing import Any
from app.models.product_group_model import ProductGroup
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, check_if_user_is_associetes_with_business, retrieve_businesses_by_user_id
from app.models.product_model import Product, ProductCreate, ProductPublic, ProductPublic, ProductUpdate, ProductsPublic
from app.models.business_model import Business, BusinessPublicID
from app.models.base import Message
from app.models.item_model import Item
from app.models.product_tag_link_model import ProductTagLink
from app.models.product_tag_model import ProductTag
from app.crud.crud_product import product_crud
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/my/", response_model=ProductsPublic)
def read_my_products(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve products created by me.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Product)
        count = session.exec(count_statement).one()
        statement = select(Product).offset(skip).limit(limit)
        products = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Product)
            .where(Product.creator_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Product)
            .where(Product.creator_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        products = session.exec(statement).all()

    return ProductsPublic(data=products, count=count)

@router.get("/by_product_group/", response_model=ProductsPublic)
def read_products_group(
    session: SessionDep, current_user: CurrentUser, product_group_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve products.
    """
    # Get product_group
    product_group = session.get(ProductGroup, product_group_id)
    if not product_group:
        raise HTTPException(status_code=404, detail="Product group not found")

    # check if current_user has employee
    businesses = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not businesses.count==0):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Get all products of the business which has items
    count_statement = (
        select(func.count())
        .select_from(Product)
        .where(Product.product_group_id == product_group.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Product)
        .where(Product.product_group_id == product_group.id)
        .offset(skip)
        .limit(limit)
    )
    products = session.exec(statement).all()
    return ProductsPublic(data=products, count=count)


@router.get("/by_business/", response_model=ProductsPublic)
def read_by_business(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve products.
    """
    # check if current_user has employee
    businesses = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not businesses.count==0):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Get items of the business
    items_statement = (
        select(Item)
        .where(Item.business_id.in_([business.id for business in businesses]))
    )
    items = session.exec(items_statement).all()

    # Get all products of the business which has items
    count_statement = (
        select(func.count())
        .select_from(Product)
        .where(Product.id.in_([item.product_id for item in items]))
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Product)
        .where(Product.id.in_([item.product_id for item in items]))
        .offset(skip)
        .limit(limit)
    )
    products = session.exec(statement).all()

    # Get all products of the business which has items
    # count_statement = (
    #     select(func.count())
    #     .select_from(Product)
    #     .where(Product.product_group_id == product_group.id)
    # )
    # count = session.exec(count_statement).one()
    # statement = (
    #     select(Product)
    #     .where(Product.product_group_id == product_group.id)
    #     .offset(skip)
    #     .limit(limit)
    # )
    # products = session.exec(statement).all()
    return ProductsPublic(data=products, count=count)


@router.get("/{id}", response_model=ProductPublic)
def read_product(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get product by ID.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    businesses = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not businesses.count==0):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return product


@router.post("/", response_model=ProductPublic)
def create_product_with_group(
    *, session: SessionDep, current_user: CurrentUser, product_in: ProductCreate
) -> Any:
    """
    Create new product.
    """
    businesses = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not businesses.count==0):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = product_crud.create_product(session=session, product_in=product_in, creator_id=current_user.id, product_group_id=product_in.product_group_id)
    return product

@router.put("/taglink/", response_model=ProductPublic)
def add_product_tag_link_to_product(
    *, session: SessionDep, current_user: CurrentUser, product_tag_link: ProductTagLink
) -> Any:
    """
    Create new product_tag_link.
    """
    product = session.get(Product, product_tag_link.product_id)
    logger.info(f"product!!! {product}")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and (product.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product_tag = session.get(ProductTag, product_tag_link.product_tag_id)
    if not product_tag:
        raise HTTPException(status_code=404, detail="ProductTag not found")
    logger.info(f"product_tag: {product_tag}")
    tags = product.tags + [product_tag]
    logger.info(f"tags: {tags}")
    product_in = ProductUpdate(
        tags = product.tags + [product_tag]
    )
    logger.info(f"product_in: {product_in}")
    update_dict = product_in.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_dict)
    session.add(product)
    session.add(product_tag_link)
    session.commit()
    session.refresh(product)
    return product

@router.put("/{id}", response_model=ProductPublic)
def update_product(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    product_in: ProductUpdate,
) -> Any:
    """
    Update an product.
    """
    product = session.get(Product, id)
    logger.info(f"product!!! {product}")
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and (product.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_dict = product_in.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_dict)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{id}")
def delete_product(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an product.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if not current_user.is_superuser and (product.creator_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")
