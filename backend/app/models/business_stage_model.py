import uuid
from typing import Optional, List
from app.models.base import SQLModel, Field, Relationship
from app.models.user_model import User
from app.models.employee_model import Employee
from app.models.stage_model import Stage
from app.models.business_model import Business
from datetime import datetime
from sqlalchemy.sql import func


class BusinessStageBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
    status: str = Field(default="received")
    comments: str | None = Field(default=None, max_length=255)


# Properties to receive on business stage creation
class BusinessStageCreate(BusinessStageBase):
    pass


# Properties to receive on business stage update
class BusinessStageUpdate(BusinessStageBase):
    status: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class BusinessStage(BusinessStageBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    business_id: uuid.UUID = Field(
        foreign_key="business.id", nullable=False, ondelete="CASCADE"
    )
    private_id: uuid.UUID = Field(
        foreign_key="private.id", nullable=False, ondelete="CASCADE"
    )
    stage_id: uuid.UUID = Field(
        foreign_key="stage.id", nullable=False, ondelete="CASCADE"
    )
    business: Business | None = Relationship(back_populates="business_stages")
    employee: Employee | None = Relationship(back_populates="business_stages")
    stage: Stage | None = Relationship(back_populates="business_stages")


# Properties to return via API, id is always required
class BusinessStagePublic(BusinessStageBase):
    id: uuid.UUID
    business_id: uuid.UUID


class BusinessStagesPublic(SQLModel):
    data: list[BusinessStagePublic]
    count: int
