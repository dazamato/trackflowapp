import uuid
from typing import Optional, List
from app.models.base import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func

class SaleBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    item_id: uuid.UUID
    quantity_of_items: int = Field(default=1)
    discount: float = Field(default=0.0)
    total_price: float = Field(default=0.0)
    billing_address: str = Field(max_length=255)
    billing_city: str = Field(max_length=255)
    billing_state: str | None = Field(default=None, max_length=255)
    billing_country: str = Field(max_length=255)
    billing_zip: str | None = Field(default=None, max_length=255)
    shipping_address: str = Field(max_length=255)
    shipping_city: str = Field(max_length=255)
    shipping_state: str | None = Field(default=None, max_length=255)
    shipping_country: str = Field(max_length=255)
    shipping_zip: str | None = Field(default=None, max_length=255)
    receiver_name: str | None = Field(default=None, max_length=255)
    receiver_phone: str | None = Field(default=None, max_length=255)
    receiver_email: str | None = Field(default=None, max_length=255)


# Properties to receive on sale creation
class SaleCreate(SaleBase):
    pass


# Properties to receive on sale update
class SaleUpdate(SaleBase):
    total_price: float | None = Field(default=None)  # type: ignore


# Database model, database table inferred from class name
class Sale(SaleBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lead_id: uuid.UUID = Field(
        foreign_key="lead.id", nullable=False, ondelete="CASCADE"
    )


# Properties to return via API, id is always required
class SalePublic(SaleBase):
    id: uuid.UUID
    lead_id: uuid.UUID


class SalesPublic(SQLModel):
    data: list[SalePublic]
    count: int
