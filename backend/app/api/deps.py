from collections.abc import Generator
from typing import Annotated, Any
import uuid
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, func, select
from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models.base import TokenPayload
from app.models.user_model import User
from app.models.employee_model import Employee
from app.models.business_model import Business, BusinessesPublic
from app.models.product_model import Product, ProductsPublic
from app.models.item_model import Item


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

def check_if_user_is_associetes_with_business(session: SessionDep, user_id: uuid.UUID, business_id: uuid.UUID) -> Any:
    statement = select(Employee).where(Employee.user_id == user_id).where(Employee.business_id == business_id)
    employee = session.exec(statement).first()
    return employee is not None, employee

def retrieve_businesses_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Business:
    statement = (
        select(Business)
        .join(Employee)
        .where(Employee.user_id == user_id)
    )
    business = session.exec(statement).first()
    return business


def retrieve_products_by_business_id(session: SessionDep, business_id: uuid.UUID, product_group_id: uuid.UUID|None = None) -> ProductsPublic:
    if product_group_id:
        items_statement = (
            select(Item)
            .where(Item.business_id == business_id)
        )
        items = session.exec(items_statement).all()

        # Get all products of the business which has items
        if len(items)==0:
            raise HTTPException(status_code=400, detail="Your business has no items")
        
        count_statement = (
            select(func.count())
            .select_from(Product)
            .where(Product.id.in_([item.product_id for item in items]))
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Product)
            .where(Product.id.in_([item.product_id for item in items]))
        )
        products = session.exec(statement).all()
    else:
        items_statement = (
            select(Item)
            .where(Item.business_id == business_id)
        )
        items = session.exec(items_statement).all()

        # Get all products of the business which has items
        if len(items)==0:
            raise HTTPException(status_code=400, detail="Your business has no items")
        count_statement = (
            select(func.count())
            .select_from(Product)
            .where(Product.id.in_([item.product_id for item in items]) & Product.product_group_id==product_group_id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Product)
            .where(Product.id.in_([item.product_id for item in items]) & Product.product_group_id==product_group_id)
        )
        products = session.exec(statement).all()
        
    
    return ProductsPublic(data=products, count=count)