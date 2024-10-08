import uuid
from pydantic import EmailStr
from app.models.base import Field, Relationship, SQLModel
from datetime import datetime
from sqlalchemy.sql import func
from typing import Any
from pydantic import computed_field


# Shared properties
class AddressBase(SQLModel):
    address_type: str = Field(max_length=255)
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
# Properties to receive on lead creation
class AddressCreate(AddressBase):
    lead_id: uuid.UUID


# Properties to receive on lead update
class AddressUpdate(AddressBase):
    address_type: str | None = Field(max_length=255)
    billing_address: str | None = Field(max_length=255)
    billing_city: str | None = Field(max_length=255)


# Database model, database table inferred from class name
class Address(AddressBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    lead_id: uuid.UUID = Field(
        foreign_key="lead.id", nullable=False, ondelete="CASCADE"
    )
    lead: "Lead" = Relationship(back_populates="addresses") # type: ignore
    

# Properties to return via API, id is always required
class AddressPublic(AddressBase):
    id: uuid.UUID
    lead_id: uuid.UUID
    
    


class AddressesPublic(SQLModel):
    data: list[AddressPublic]
    count: int
