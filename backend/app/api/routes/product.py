from typing_extensions import Optional
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, check_if_user_is_associetes_with_business
from app.models.product_model import Product, ProductCreate, ProductPublic, ProductPublic, ProductUpdate, ProductsPublic
from app.models.business_model import Business, BusinessPublicID
from app.models.base import Message
from app.crud.crud_product import product_crud

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
            .where(Product.user_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Product)
            .where(Product.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        products = session.exec(statement).all()

    return ProductsPublic(data=products, count=count)

@router.get("/my_business/", response_model=ProductsPublic)
def read_business_products(
    session: SessionDep, current_user: CurrentUser, business_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve products.
    """
    # Get business
    business = session.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    # Get products of the business
    associated, associated_employee = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
    # statement_employess = (
    #     select(Product)
    #     .where(Product.business_id == business.id)
    #     .offset(skip)
    #     .limit(limit)
    # )
    # auth_products = session.exec(statement_employess).all()
    # # Check if the user is associated with the any of the products
    # associated = any(product.user_id == current_user.id for product in auth_products)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Get all products of the business
    count_statement = (
        select(func.count())
        .select_from(Product)
        .where(Product.business_id == business.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Product)
        .where(Product.business_id == business.id)
        .offset(skip)
        .limit(limit)
    )
    products = session.exec(statement).all()
    return ProductsPublic(data=products, count=count)


@router.get("/{id}&{business_id}", response_model=ProductPublic)
def read_product(session: SessionDep, current_user: CurrentUser, id: uuid.UUID, business_id: uuid.UUID) -> Any:
    """
    Get product by ID.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    associated, associated_employee = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return product


@router.post("/", response_model=ProductPublic)
def create_product_with_business(
    *, session: SessionDep, current_user: CurrentUser, product_in: ProductCreate
) -> Any:
    """
    Create new product.
    """
    associated, associated_employee = check_if_user_is_associetes_with_business(session, current_user.id, product_in.business_id)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = product_crud.create_product(session,
        product_in=product_in,
        user_id=current_user.id,
        business_id=product_in.business_id)
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
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")


    if not current_user.is_superuser and (product.user_id != current_user.id):
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
    if not current_user.is_superuser and (product.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")
