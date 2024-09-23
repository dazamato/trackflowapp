import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from datetime import datetime
from sqlalchemy.sql import func
from app.models.business_model import Business
from app.models.sale_model import Sale

# Shared properties
class LeadBase(SQLModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_phone: str = Field(min_length=1, max_length=255)
    customer_email: str | None = Field(default=None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    customer_id: uuid.UUID | None = Field(default=None)
    lead_product: uuid.UUID | None = Field(default=None)
    lead_quantity: int | None = Field(default=None)
    lead_preferable_price_per_item: float | None = Field(default=None)
    lead_comments: str | None = Field(default=None, max_length=255)
    lead_supporter_id: uuid.UUID | None = Field(default=None)
    lead_business_stage_id: uuid.UUID | None = Field(default=None)
# Properties to receive on lead creation
class LeadCreate(LeadBase):
    pass


# Properties to receive on lead update
class LeadUpdate(LeadBase):
    customer_name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Lead(LeadBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_name: str = Field(max_length=255)
    business_id: uuid.UUID = Field(
        foreign_key="business.id", nullable=False, ondelete="CASCADE"
    )
    business: Business | None = Relationship(back_populates="leads")
    sale_id: uuid.UUID | None = Field(default=None)
    sale: Sale | None = Relationship(back_populates="leads")


# Properties to return via API, id is always required
class LeadPublic(LeadBase):
    id: uuid.UUID
    business_id: uuid.UUID


class LeadsPublic(SQLModel):
    data: list[LeadPublic]
    count: int
