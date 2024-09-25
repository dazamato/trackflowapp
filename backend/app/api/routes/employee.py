from typing_extensions import Optional
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, check_if_user_is_associetes_with_business
from app.models.employee_model import Employee, EmployeeCreate, EmployeePublic, EmployeePublic, EmployeeUpdate, EmployeesPublic, NewInvite
from app.models.business_model import Business, BusinessPublicID
from app.models.base import Message
from app.crud.crud_employee import employee_crud
from app.crud.crud_user import user_crud
from app.crud.crud_business import business_crud
from app.utils import generate_invite_token, verify_invite_token, generate_invite_to_business_email, send_email

router = APIRouter()

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
    associated, associated_employee = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
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
    associated, associated_employee = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
    if not current_user.is_superuser and (not associated):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return employee


@router.post("/", response_model=EmployeePublic)
def create_admin_employee_with_business(
    session: SessionDep, current_user: CurrentUser, employee_in: EmployeeCreate
) -> Any:
    """
    # TODO Register as new employee using invitation hash.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    employee = employee_crud.create_employee(session,
        employee_in=employee_in,
        user_id=current_user.id,
        business_id=employee_in.business_id)
    return employee

@router.post("/invite_employee/{email}/{business_id}")
def invite_employee(email: str, business_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Message:
    """
    Invite employee to Business
    """
    associated_auth, associated_employee_auth = check_if_user_is_associetes_with_business(session, current_user.id, business_id)
    user = user_crud.get_user_by_email(session=session, email=email)
    business = business_crud.get(session, business_id)
    # Checks
    if not business:
        raise HTTPException(
            status_code=404,
            detail="The Company with this id not founded",
        )
    if user:
        associated, associated_employee = check_if_user_is_associetes_with_business(session, user.id, business_id)
        if associated:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already registered in your Company",
            )
        else:
            pass
    else:
        pass
    invite_token = generate_invite_token(email=email, business_id=business_id)
    email_data = generate_invite_to_business_email(
        email_to=email, email=email, token=invite_token, business_name=business.name
    )
    send_email(
        email_to=email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message=f"Invitation email sent with token {invite_token}")

# invite_register/?token={token}

@router.post("/register-by-invitation/")
def register_new_user_employee(session: SessionDep, body: NewInvite) -> Message:
    """
    Register new user and employee using invitation
    """
    # verify invitation
    invite = verify_invite_token(token=body.token)
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid token")
    # verify if user exists if not create one
    user = user_crud.get_user_by_email(session=session, email=invite.email)
    if not user:
        user = user_crud.create_user(session=session, user_create=body.new_user)
    else:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
    # create employee for user
    employee = employee_crud.create_employee(session=session, employee_in=body.new_employee, user_id=user.id, business_id=invite.business_id)
    return Message(message="You registered as member of team successfully. Please signin to system")

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
