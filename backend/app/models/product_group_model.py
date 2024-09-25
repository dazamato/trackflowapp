import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from app.models.user_model import User
from datetime import datetime
from sqlalchemy.sql import func

class ProductGroupBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    image: str | None = Field(default=None, max_length=255)


# Properties to receive on product group creation
class ProductGroupCreate(ProductGroupBase):
    pass


# Properties to receive on product group update
class ProductGroupUpdate(ProductGroupBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class ProductGroup(ProductGroupBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    creator_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    creator: User | None = Relationship(back_populates="product_groups")
    products: list['Product'] | None = Relationship(back_populates="group")


# Properties to return via API, id is always required
class ProductGroupPublic(ProductGroupBase):
    id: uuid.UUID
    creator_id: uuid.UUID


class ProductGroupsPublic(SQLModel):
    data: list[ProductGroupPublic]
    count: int
