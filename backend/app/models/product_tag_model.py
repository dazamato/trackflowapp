import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from app.models.product_tag_link_model import ProductTagLink
from datetime import datetime
from sqlalchemy.sql import func



class ProductTagBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)


# Properties to receive on product tag creation
class ProductTagCreate(ProductTagBase):
    pass


# Properties to receive on product tag update
class ProductTagUpdate(ProductTagBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class ProductTag(ProductTagBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    products: list["Product"] = Relationship(back_populates="tags", link_model=ProductTagLink)


# Properties to return via API, id is always required
class ProductTagPublic(ProductTagBase):
    id: uuid.UUID
    creator_id: uuid.UUID


class ProductTagsPublic(SQLModel):
    data: list[ProductTagPublic]
    count: int
