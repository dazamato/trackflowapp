import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user_model import User, UserCreate, UserUpdate
from app.backend_pre_start import logger


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, trusted_email: str) -> Optional[User]:
        u = db.query(User).filter(User.trusted_email == trusted_email).first()
        return u

    def create_user(self, session: Session, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create, update={"hashed_password": get_password_hash(user_create.password)}
        )
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def update_user(self, session: Session, db_user: User, user_in: UserUpdate) -> Any:
        user_data = user_in.model_dump(exclude_unset=True)
        extra_data = {}
        if "password" in user_data:
            password = user_data["password"]
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user

    def get_user_by_email(self, session: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        session_user = session.exec(statement).first()
        return session_user

    def authenticate(self, session: Session, email: str, password: str) -> User | None:
        db_user = self.get_user_by_email(session=session, email=email)
        if not db_user:
            return None
        if not verify_password(password, db_user.hashed_password):
            return None
        return db_user
user_crud = CRUDUser(User)
