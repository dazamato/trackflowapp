from sqlmodel import Session, create_engine, select

from app import crud_old as crud
from app.core.config import settings
from app.models.user_model import User, UserCreate
from app.models.base import SQLModel
from app.models.user_model import User
from app.models.employee_model import Employee
from app.models.business_model import Business
from app.models.business_industry_model import BusinessIndustry
from app.models.item_model import Item
from app.models.product_model import Product
from app.models.product_group_model import ProductGroup
from app.models.product_tag_model import ProductTag
from app.models.product_tag_link_model import ProductTagLink
from app.models.sale_model import Sale
from app.models.proposal_model import Proposal
from app.models.lead_model import Lead
from app.models.address_model import Address
from app.models.base import Message, Token, TokenPayload, NewPassword

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # from app.core.engine import engine
    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = crud.create_user(session=session, user_create=user_in)
