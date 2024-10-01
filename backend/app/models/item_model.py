from typing_extensions import Optional
import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from app.models.product_model import Product
from app.models.business_model import Business
from datetime import datetime
from sqlalchemy.sql import func

# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    price: Optional[float] = None
    cost_price: Optional[float] = None
    quantity: Optional[int] = None
    supplier: str | None = Field(default=None, max_length=255)
    img: str | None = Field(default=None, max_length=255)



# Properties to receive on item creation
class ItemCreate(ItemBase):
    product_id: uuid.UUID | None = None


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore
    product_id: uuid.UUID | None = None

# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    business_id: uuid.UUID = Field(
        foreign_key="business.id", nullable=False, ondelete="CASCADE"
    )
    business: Business | None = Relationship(back_populates="items")
    product_id: uuid.UUID = Field(
        foreign_key="product.id", nullable=False
    )
    product: Product | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    business_id: uuid.UUID
    product_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int
