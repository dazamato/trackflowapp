from app.models.base import Field, Relationship, SQLModel
from app.models.user_model import UserCreate
from app.models.employee_model import EmployeeBase

class NewInvite(SQLModel):
    token: str
    new_user: UserCreate
    new_employee: EmployeeBase