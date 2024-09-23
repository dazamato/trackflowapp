from typing_extensions import Optional
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.employee_model import Employee, EmployeeCreate, EmployeePublic, EmployeePublic, EmployeeUpdate, EmployeesPublic
from app.models.business_model import Business, BusinessPublicID
from app.models.base import Message
from app.crud.crud_employee import employee_crud

router = APIRouter()

def check_if_user_is_associetes_with_business(session: SessionDep, user_id: uuid.UUID, business_id: uuid.UUID) -> bool:
    statement = select(Employee).where(Employee.user_id == user_id).where(Employee.business_id == business_id)
    employee = session.exec(statement).first()
    return employee is not None

@router.get("/", response_model=EmployeesPublic)
def read_my_employees(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve employees.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Employee)
        count = session.exec(count_statement).one()
        statement = select(Employee).offset(skip).limit(limit)
        employees = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Employee)
            .where(Employee.user_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Employee)
            .where(Employee.user_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        employees = session.exec(statement).all()

    return EmployeesPublic(data=employees, count=count)

@router.get("/", response_model=EmployeesPublic)
def read_business_employees(
    session: SessionDep, current_user: CurrentUser, business_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve employees.
    """
    # Get business
    business = session.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    # Get employees of the business
    associated = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
    # statement_employess = (
    #     select(Employee)
    #     .where(Employee.business_id == business.id)
    #     .offset(skip)
    #     .limit(limit)
    # )
    # auth_employees = session.exec(statement_employess).all()
    # # Check if the user is associated with the any of the employees
    # associated = any(employee.user_id == current_user.id for employee in auth_employees)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Get all employees of the business
    count_statement = (
        select(func.count())
        .select_from(Employee)
        .where(Employee.business_id == business.id)
    )
    count = session.exec(count_statement).one()
    statement = (
        select(Employee)
        .where(Employee.business_id == business.id)
        .offset(skip)
        .limit(limit)
    )
    employees = session.exec(statement).all()
    return EmployeesPublic(data=employees, count=count)


@router.get("/{id}&{business_id}", response_model=EmployeePublic)
def read_employee(session: SessionDep, current_user: CurrentUser, id: uuid.UUID, business_id: uuid.UUID) -> Any:
    """
    Get employee by ID.
    """
    employee = session.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    associated = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return employee


@router.post("/", response_model=EmployeePublic)
def create_employee_with_business(
    *, session: SessionDep, current_user: CurrentUser, employee_in: EmployeeCreate, business: BusinessPublicID
) -> Any:
    """
    Create new employee.
    """
    associated = check_if_user_is_associetes_with_business(session, current_user.id, business.id)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    employee = employee_crud.create_employee(session,
        employee_in=employee_in,
        user_id=current_user.id,
        business_id=business.id)
    return employee

@router.put("/{id}", response_model=EmployeePublic)
def update_employee(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    employee_in: EmployeeUpdate,
) -> Any:
    """
    Update an employee.
    """
    employee = session.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")


    if not current_user.is_superuser and (employee.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_dict = employee_in.model_dump(exclude_unset=True)
    employee.sqlmodel_update(update_dict)
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.delete("/{id}")
def delete_employee(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an employee.
    """
    employee = session.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if not current_user.is_superuser and (employee.user_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(employee)
    session.commit()
    return Message(message="Employee deleted successfully")
