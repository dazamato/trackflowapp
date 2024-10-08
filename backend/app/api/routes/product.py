from typing_extensions import Optional
import uuid
from typing import Any
from app.models.product_group_model import ProductGroup
from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id, retrieve_products_by_business_id
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

@router.get("/", response_model=ProductsPublic)
def read_products_all_public_by_group(
    session: SessionDep, current_user: CurrentUser, product_group_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve products og product_group.
    """
    # Get product_group
    product_group = session.get(ProductGroup, product_group_id)
    if not product_group:
        raise HTTPException(status_code=404, detail="Product group not found")

    # check if current_user has employee
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    # TODO add moderation functionality
    products_all = session.exec(select(Product).where((Product.product_group_id == product_group_id)
                                                    #   & (Product.moderated == True)
                                                      )).all()
    count = len(products_all)
    products = ProductsPublic(data=products_all, count=count)
    return products

@router.get("/by_product_group_with_created_items/", response_model=ProductsPublic)
def read_products_group(
    session: SessionDep, current_user: CurrentUser, product_group_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve products of product_group with created items.
    """
    # Get product_group
    product_group = session.get(ProductGroup, product_group_id)
    if not product_group:
        raise HTTPException(status_code=404, detail="Product group not found")

    # check if current_user has employee
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    if not current_user.is_superuser:
        products = retrieve_products_by_business_id(session=session, business_id=business.id, product_group_id=product_group_id)
    else:
        products_all = session.exec(select(Product).where(Product.product_group_id == product_group_id)).all()
        count = len(products_all)
        products = ProductsPublic(data=products_all, count=count)

    return products


@router.get("/by_business/", response_model=ProductsPublic)
def read_by_business(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve products.
    """
    # check if current_user has employee
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    
    # Get products of the business
    products = retrieve_products_by_business_id(session=session, business_id=business.id, product_group_id=None)
    return products


@router.get("/{id}", response_model=ProductPublic)
def read_product(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get product by ID.
    """
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    existing_products = retrieve_products_by_business_id(session=session, business_id=business.id)
    # check if product is in existing_products
    filtered_existing_products = [e for e in existing_products.data if e.id == id]
    if len(filtered_existing_products) == 0:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return product


@router.post("/", response_model=ProductPublic)
def create_product_with_group(
    *, session: SessionDep, current_user: CurrentUser, product_in: ProductCreate
) -> Any:
    """
    Create new product.
    """
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = product_crud.create_product(session=session, product_in=product_in, product_group_id=product_in.product_group_id)
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
    
    # Check if current_user has permission to add tag to product
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions, you not in any")
    
    existing_products = retrieve_products_by_business_id(session=session, business_id=business.id)
    # TODO retrieve products by business takes only that products that have items associated to business in which user is employee. There is product is not in that list, then user does not have permission to add tag to that product
    # NEED to fix that
    # check if product is in existing_products
    logger.info(f"existing_products: {existing_products}")
    filtered_existing_products = [e for e in existing_products.data if e.id == product_tag_link.product_id]
    # if len(filtered_existing_products) > 0:
    #     raise HTTPException(status_code=400, detail="Product already has this tag")
    
    product_tag = session.get(ProductTag, product_tag_link.product_tag_id)
    if not product_tag:
        raise HTTPException(status_code=404, detail="ProductTag not found")
    
    if product_tag.id in [t.id for t in product.tags]:
        raise HTTPException(status_code=400, detail="Product already has this tag")
    
    # Saving product_tag_link and updating product
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
    
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    existing_products = retrieve_products_by_business_id(session=session, business_id=business.id)
    # check if product is in existing_products
    filtered_existing_products = [e for e in existing_products.data if e.id == id]
    if len(filtered_existing_products) == 0:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    #Update

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
    
    business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (not business):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    existing_products = retrieve_products_by_business_id(session=session, business_id=business.id)
    # check if product is in existing_products
    filtered_existing_products = [e for e in existing_products.data if e.id == id]
    if len(filtered_existing_products) == 0:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")
