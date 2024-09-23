import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.employee_model import Employee, EmployeeCreate, EmployeeUpdate
from app.backend_pre_start import logger


class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    def create_employee(self, session: Session, employee_in: EmployeeCreate, user_id: uuid.UUID, business_id: uuid.UUID) -> Employee:
        db_item = Employee.model_validate(employee_in, update={"user_id": user_id, "business_id": business_id})
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
employee_crud = CRUDEmployee(Employee)
