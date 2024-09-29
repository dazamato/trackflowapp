# import uuid
# from typing import Optional, List
# from app.models.base import SQLModel, Field, Relationship
# from app.models.user_model import User
# # from app.models.employee_model import Employee
# from app.models.business_model import Business
# from datetime import datetime
# from sqlalchemy.sql import func

# # Shared properties
# class StageBase(SQLModel):
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow},)
#     is_active: bool = Field(default=True)
#     order_priority: int = Field(default=0)
#     is_required: bool = Field(default=True)
#     display_name: str = Field(max_length=255)
#     display_description: str | None = Field(default=None, max_length=255)


# # Properties to receive on stage creation
# class StageCreate(StageBase):
#     pass


# # Properties to receive on stage update
# class StageUpdate(StageBase):
#     display_name: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# # Database model, database table inferred from class name
# class Stage(StageBase, table=True):
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     business_id: uuid.UUID = Field(
#         foreign_key="business.id", nullable=False, ondelete="CASCADE"
#     )
#     business: Business | None = Relationship(back_populates="stages")
#     business_stages: List["BusinessStage"] | None = Relationship(back_populates="stage")


# # Properties to return via API, id is always required
# class StagePublic(StageBase):
#     id: uuid.UUID
#     business_id: uuid.UUID


# class StagesPublic(SQLModel):
#     data: List[StagePublic]
#     count: int
