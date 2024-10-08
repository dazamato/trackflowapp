import uuid
from typing import Any, Dict, Optional, Union
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.address_model import Address, AddressCreate, AddressUpdate
from app.backend_pre_start import logger


class CRUDAddress(CRUDBase[Address, AddressCreate, AddressUpdate]):
    def create_address(self, session: Session, address_in: AddressCreate) -> Address:
        db_item = Address.model_validate(address_in)
        session.add(db_item)
        session.commit()
        session.refresh(db_item)
        return db_item
address_crud = CRUDAddress(Address)