from typing_extensions import Optional
import uuid
from typing import Any
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
from sqlmodel import func, select
from app.api.deps import CurrentUser, SessionDep, retrieve_businesses_by_user_id
from app.models.employee_model import Employee, EmployeeCreate, EmployeeCreateAdmin, EmployeePublic, EmployeePublic, EmployeeUpdate, EmployeesPublic
from app.models.invite_model import NewInvite, NewRegInvite
from app.models.business_model import Business, BusinessPublicID
from app.models.base import Message
from app.crud.crud_employee import employee_crud
from app.crud.crud_user import user_crud
from app.crud.crud_business import business_crud
from app.utils import generate_invite_token, verify_invite_token, generate_invite_to_business_email, send_email
from fastapi.encoders import jsonable_encoder
import os
import logging


logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=EmployeePublic)
def read_employee_me(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Retrieve employees.
    """
    statement = (
        select(Employee)
        .where(Employee.user_id == current_user.id)
    )
    employee = session.exec(statement).first()
    if not employee:
        raise HTTPException(status_code=404, detail="User not registered as employee")
    return employee

@router.get("/business", response_model=EmployeesPublic)
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
    
    accessed_business = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (business.id != accessed_business.id):
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
    
    business = session.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    accessed_business = retrieve_businesses_by_user_id(session, current_user.id)
    
    if not current_user.is_superuser and (business.id != accessed_business.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return employee


@router.post("/first/", response_model=EmployeePublic)
def create_first_employee_with_business(
    session: SessionDep, current_user: CurrentUser, employee_in: EmployeeCreate
) -> Any:
    """
    # Register as new employee by admin.
    """
    # check user if it exists as employee
    statement_check_empl = (
        select(func.count())
        .select_from(Employee)
        .where(Employee.user_id == current_user.id)
    )
    employee_check_cnt = session.exec(statement_check_empl).one()
    count_statement = (
        select(func.count())
        .select_from(Employee)
        .where(Employee.business_id == employee_in.business_id)
    )
    count = session.exec(count_statement).one()
    if (count == 0) & (employee_check_cnt == 0):
        employee = employee_crud.create_employee(session,
            employee_in=employee_in,
            user_id=current_user.id,
            business_id=employee_in.business_id)
    else:
        raise HTTPException(status_code=400, detail="Not enough permissions or you are already registered as employee")
    return employee

@router.post("/admin/", response_model=EmployeePublic)
def create_admin_employee_with_business(
    session: SessionDep, current_user: CurrentUser, employee_in: EmployeeCreateAdmin
) -> Any:
    """
    # Register as new employee by admin.
    """
    # check user if it exists as employee
    statement_check_empl = (
        select(func.count())
        .select_from(Employee)
        .where(Employee.user_id == employee_in.user_id)
    )
    employee_check_cnt = session.exec(statement_check_empl).one()
    
    if employee_check_cnt > 0:
        raise HTTPException(status_code=400, detail="User is already registered as employee")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    employee = employee_crud.create_employee(session,
        employee_in=employee_in,
        user_id=employee_in.user_id,
        business_id=employee_in.business_id)
    return employee

@router.post("/invite_employee/{email}/{business_id}")
def invite_employee(email: str, business_id: uuid.UUID, session: SessionDep, current_user: CurrentUser) -> Message:
    """
    Invite employee to Business
    """
    # Get business
    business = session.get(Business, business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    # Get registered business
    accessed_business_current = retrieve_businesses_by_user_id(session, current_user.id)
    if not current_user.is_superuser and (business.id != accessed_business_current.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Get user to whom current user sending invite
    user = user_crud.get_user_by_email(session=session, email=email)
    if user:
        accessed_business_invit = retrieve_businesses_by_user_id(session, user.id)
        if accessed_business_invit:
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
    obj_in_data = jsonable_encoder(body.new_employee)
    obj_in_data["role"] = "undefined_employee"
    business = business_crud.get(session, id = invite.business_id)
    employee = employee_crud.create_employee(session=session, employee_in=obj_in_data, user_id=user.id, business_id=invite.business_id)
    return Message(message=f"Thank you, {user.full_name}! You has registered as {employee.name} of {business.name} team successfully. Please signin to system")

@router.post("/create-by-invitation/")
def register_employee_inv(session: SessionDep, current_user: CurrentUser, body: NewRegInvite) -> Message:
    """
    Register employee using invitation
    """
    # verify invitation
    invite = verify_invite_token(token=body.token)
    if not invite:
        raise HTTPException(status_code=400, detail="Invalid token")
    # verify if user exists if not create one
    
    if invite.email!=current_user.email:
        raise HTTPException(status_code=400, detail="Access denied")
    
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    # create employee for user
    employee = employee_crud.create_employee(session=session, employee_in=body.new_employee, user_id=current_user.id, business_id=invite.business_id)
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

@router.post("/update_avatar/", response_model=EmployeePublic)
async def create_upload_file(
    *,
    file: UploadFile,
    session: SessionDep,
    current_user: CurrentUser):
    
    statement = (
        select(Employee)
        .where(Employee.user_id == current_user.id)
    )
    
    employee = session.exec(statement).first()
    if not employee:
        raise HTTPException(status_code=404, detail="User not registered as employee")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    #  Ensure the directory exists
    os.makedirs("/app/app/static/avatars", exist_ok=True)

    # Save the avatar to the static files directory
    id = uuid.uuid4()
    logger.info(f"Saving avatar with id {id}")
    avatar_path = f"/app/app/static/avatars/{id}.png"
    logger.info(f"Saving avatar to {avatar_path}")
    
    # Delete the old avatar if it exists
    if employee.avatar:
        old_avatar_path = f"/app/app/static/avatars/{employee.avatar}.png"
        if os.path.exists(old_avatar_path):
            try:
                os.remove(old_avatar_path)
            except Exception as e:
                logger.error(f"Error deleting old avatar: {e}")
                raise HTTPException(status_code=400, detail="Error updating old avatar")
    
    try:
        with open(avatar_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        logger.error(f"Error saving avatar: {e}")
        raise HTTPException(status_code=400, detail="Error saving avatar")
    try:
        employee.avatar = id
    except Exception as e:
        logger.error(f"Error adding avatar: {e}")
        raise HTTPException(status_code=400, detail="Error adding avatar")
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee

@router.get("/get_avatar/{id}")
async def get_avatar(id: uuid.UUID):
    avatar_path = f"/app/app/static/avatars/{id}.png"
    image_path = Path(avatar_path)
    if not image_path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(image_path)

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
