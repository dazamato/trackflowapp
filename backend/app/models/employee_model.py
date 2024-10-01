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
    is_active: Optional[bool] = Field(default=True)
    business_id: Optional[int] = None

class UserShow(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    
# Database model, database table inferred from class name
class Employee(EmployeeBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    is_active: bool = Field(default=True)
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
    business: Business | None
    created_at: datetime
    updated_at: datetime

class EmployeesPublic(SQLModel):
    data: List[EmployeePublic]
    count: int



# These are placeholder type hints. You should replace them with actual imports.
# class User_model(SQLModel):
#     pass

# class Business_model(SQLModel):
#     pass

# This structure follows a similar pattern to the Item model you provided, with the following key components:

# 1. `PrivateBase`: Contains shared properties.
# 2. `PrivateCreate`: For creating new Private instances.
# 3. `PrivateUpdate`: For updating existing Private instances.
# 4. `Private`: The main database model.
# 5. `PrivatePublic`: For returning Private data via API.
# 6. `PrivatesPublic`: For returning multiple Private instances.

# Note that I've made some assumptions:
# - The `id` field uses UUID, similar to the Item model.
# - I've kept the field names and types as you specified.
# - I've added length constraints to string fields where appropriate.
# - The `User_model` and `Business_model` are placeholder classes. You should replace these with your actual user and business model imports.

# You may need to adjust some details based on your specific requirements and how your User and Business models are defined.
