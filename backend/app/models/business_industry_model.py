import uuid
from typing import Optional, List
from app.models.base import SQLModel, Field, Relationship
# from app.models.user_model import User
from datetime import datetime
from sqlalchemy.sql import func

# Shared properties
class BusinessIndustryBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    market_value: float | None = Field(default=None)
    image: str | None = Field(default=None, max_length=255)


# Properties to receive on business industry creation
class BusinessIndustryCreate(BusinessIndustryBase):
    pass


# Properties to receive on business industry update
class BusinessIndustryUpdate(BusinessIndustryBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class BusinessIndustry(BusinessIndustryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    businesses: List['Business'] | None = Relationship(back_populates="business_industry")


# Properties to return via API, id is always required
class BusinessIndustryPublic(BusinessIndustryBase):
    id: uuid.UUID
    creator_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class BusinessIndustryPublicId(SQLModel):
    id: uuid.UUID

class BusinessIndustriesPublic(SQLModel):
    data: list[BusinessIndustryPublic]
    count: int
