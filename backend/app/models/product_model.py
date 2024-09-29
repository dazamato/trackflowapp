
import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel

from app.models.product_group_model import ProductGroup
from app.models.product_tag_model import ProductTag
# from app.models.item_model import Item
from datetime import datetime
from sqlalchemy.sql import func
from app.models.product_tag_link_model import ProductTagLink

class ProductBase(SQLModel):
    title: str | None = Field(min_length=1, max_length=255)
    description: str | None = Field(min_length=1, max_length=255)
    sku: str | None = Field(min_length=1, max_length=255)
    image: str | None = Field(default=None, max_length=255)

# Properties to receive on product creation
class ProductCreate(ProductBase):
    product_group_id: uuid.UUID


# Properties to receive on product update
class ProductUpdate(ProductBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)   # type: ignore
    description: str | None = Field(default=None, max_length=255)
    sku: str | None = Field(default=None, min_length=1, max_length=255)
    product_group_id: uuid.UUID | None = Field(default=None)
    moderated: bool| None = Field(default=None, min_length=1, max_length=255)
    tags: list[ProductTag] | None = Field(default=[])

# Database model, database table inferred from class name
class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    moderated: bool = False
    product_group_id: uuid.UUID = Field(
        foreign_key="productgroup.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    group: ProductGroup | None = Relationship(back_populates="products")
    items: list["Item"] | None = Relationship(back_populates="product")
    tags: list[ProductTag] = Relationship(back_populates="products", link_model=ProductTagLink)



# Properties to return via API, id is always required
class ProductPublic(ProductBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    product_group_id: uuid.UUID
    image: str | None
    tags: list[ProductTag]
    group: ProductGroup


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int
