import uuid
from typing import Optional, List
from app.models.base import SQLModel, Field, Relationship
from datetime import datetime
from sqlalchemy.sql import func
from pydantic import computed_field
from app.models.item_model import Item

class SaleBase(SQLModel):
    quantity_of_items: int = Field(default=1)
    discount: float = Field(default=0.0)
    price_per_item: float = Field(default=0.0)


# Properties to receive on sale creation
class SaleCreate(SaleBase):
    lead_id: uuid.UUID
    item_id: uuid.UUID


# Properties to receive on sale update
class SaleUpdate(SaleBase):
    total_price: float | None = Field(default=None)  # type: ignore


# Database model, database table inferred from class name
class Sale(SaleBase, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    lead_id: uuid.UUID = Field(
        foreign_key="lead.id", nullable=False, ondelete="CASCADE"
    )
    item_id: uuid.UUID = Field(
        foreign_key="item.id", nullable=False, ondelete="CASCADE"
    )
    item: Item = Relationship(back_populates="sales")
    @computed_field(description="sum of sale")
    @property
    def sum_of_sale(self) -> float:
        return self.quantity_of_items*self.price_per_item*(1-self.discount)
    


# Properties to return via API, id is always required
class SalePublic(SaleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    lead_id: uuid.UUID
    item: Item
    sum_of_sale: float


class SalesPublic(SQLModel):
    data: list[SalePublic]
    count: int
