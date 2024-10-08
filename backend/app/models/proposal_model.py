import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from datetime import datetime
from sqlalchemy.sql import func
from typing import Any
from pydantic import computed_field


# Shared properties
class ProposalBase(SQLModel):
    product_id: uuid.UUID | None = Field(default=None)
    quantity: int | None = Field(default=None)
    preferable_price_per_item: float | None = Field(default=None)
    comments: str | None = Field(default=None, max_length=255)
# Properties to receive on lead creation
class ProposalCreate(ProposalBase):
    lead_id: uuid.UUID
    product_id: uuid.UUID


# Properties to receive on lead update
class ProposalUpdate(ProposalBase):
    pass



# Database model, database table inferred from class name
class Proposal(ProposalBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    lead_id: uuid.UUID = Field(
        foreign_key="lead.id", nullable=False, ondelete="CASCADE"
    )
    product_id: uuid.UUID = Field(
        foreign_key="product.id", nullable=False
    )
    product: "Product" = Relationship(back_populates="proposals")
    lead: "Lead" = Relationship(back_populates="proposals")
    
class ProductShow(SQLModel):
    title: str
    image: str
    
# Properties to return via API, id is always required
class ProposalPublic(ProposalBase):
    id: uuid.UUID
    lead_id: uuid.UUID
    product_id: uuid.UUID
    product: ProductShow
    @computed_field(description="sum of proposal")
    @property
    def sum_of_proposal(self) -> float:
        return self.quantity*self.preferable_price_per_item
    
    


class ProposalsPublic(SQLModel):
    data: list[ProposalPublic]
    count: int
