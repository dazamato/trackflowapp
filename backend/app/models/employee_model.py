import uuid
from typing import Optional, List
from app.models.base import Field, Relationship, SQLModel
from app.models.business_model import Business
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from pydantic import EmailStr

# Shared properties
class EmployeeBase(SQLModel):
    name: str = Field(index=True, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, max_length=100)
    avatar: Optional[uuid.UUID] = Field(default=None, max_length=255)

# Properties to receive on employee creation
class EmployeeCreate(EmployeeBase):
    business_id: uuid.UUID
    
class EmployeeCreateAdmin(EmployeeBase):
    business_id: uuid.UUID
    user_id: uuid.UUID

# Properties to receive on employee update
class EmployeeUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, max_length=100)
    avatar: Optional[uuid.UUID] = Field(default=None, max_length=255)
    is_active: Optional[bool] = Field(default=True)
    business_id: Optional[uuid.UUID] = None

class UserShow(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    
# Database model, database table inferred from class name
class Employee(EmployeeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    is_active: bool = Field(default=True)
    avatar: Optional[uuid.UUID] = Field(default=None, max_length=255)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    business_id: uuid.UUID | None = Field(
        foreign_key="business.id", nullable=True, ondelete="CASCADE"
    )
    business: Business | None = Relationship(back_populates="employees")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)




# Properties to return via API, id is always required
class EmployeePublic(EmployeeBase):
    id: uuid.UUID
    user_id: uuid.UUID
    avatar: Optional[uuid.UUID]
    business: Business | None
    created_at: datetime
    updated_at: datetime

class EmployeesPublic(SQLModel):
    data: List[EmployeePublic]
    count: int
