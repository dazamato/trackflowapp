import uuid
from typing import Optional, List
from app.models.base import SQLModel, Field, Relationship
from app.models.business_industry_model import BusinessIndustry
# from backend.app.models.employee_model import Employee

class BusinessBase(SQLModel):
    name: str = Field(index=True)
    organizational_type: Optional[str] = Field(default=None)
    national_id: Optional[str] = Field(default=None)
    national_id_type: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    bank_account: Optional[str] = Field(default=None)
    logo: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)


# Properties to receive on business creation
class BusinessCreate(BusinessBase):
    pass


# Properties to receive on business update
class BusinessUpdate(BusinessBase):
    name: Optional[str] = Field(default=None)  # type: ignore



# Database model, database table inferred from class name
class Business(BusinessBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_industry_id: Optional[uuid.UUID] = Field(foreign_key="businessindustry.id", nullable=True)
    business_industry: BusinessIndustry | None = Relationship(back_populates="businesses")
    account_creator_id: uuid.UUID = Field(foreign_key="user.id")
    # employees: List["Employee"] = Relationship(back_populates="business")
    items: List["Item"] = Relationship(back_populates="owner")
    # leads: List["Lead"] = Relationship(back_populates="business")
    # sales: List["Sale"] = Relationship(back_populates="business")
    # stages: List["Stage"] = Relationship(back_populates="business")
    # business_stages: List["BusinessStage"] = Relationship(back_populates="business")


# Properties to return via API, id is always required
class BusinessPublic(BusinessBase):
    id: uuid.UUID
    business_industry_id: Optional[uuid.UUID]

class BusinessPublicID(SQLModel):
    id: uuid.UUID

class BusinessesPublic(SQLModel):
    data: list[BusinessPublic]
    count: int
