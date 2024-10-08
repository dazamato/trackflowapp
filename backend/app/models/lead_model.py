import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from datetime import datetime
from sqlalchemy.sql import func
from app.models.business_model import Business
from app.models.proposal_model import Proposal
from app.models.address_model import Address

# Shared properties
class LeadBase(SQLModel):
    customer_name: str | None = Field(min_length=1, max_length=255)
    lead_source: str | None = Field(default=None, max_length=255)
    customer_phone: str | None = Field(min_length=1, max_length=255)
    customer_email: str | None = Field(default=None, max_length=255)
    lead_status: str | None = Field(default=None, max_length=255)
    
# Properties to receive on lead creation
class LeadCreate(LeadBase):
    business_id: uuid.UUID



# Properties to receive on lead update
class LeadUpdate(LeadBase):
    sale_id: uuid.UUID | None = Field(default=None)



# Database model, database table inferred from class name
class Lead(LeadBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    customer_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    business_id: uuid.UUID = Field(
        foreign_key="business.id", nullable=False, ondelete="CASCADE"
    )
    business: Business | None = Relationship()
    sale_id: uuid.UUID | None = Field(default=None)
    proposals: list[Proposal] = Relationship(back_populates="lead")
    addresses: list[Address] = Relationship(back_populates="lead")


# Properties to return via API, id is always required
class LeadPublic(LeadBase):
    id: uuid.UUID
    business_id: uuid.UUID


class LeadsPublic(SQLModel):
    data: list[LeadPublic]
    count: int
