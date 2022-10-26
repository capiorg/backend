from typing import Any
from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from pydantic import validator

from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.phone import Phone
from app.v1.statuses.schemas import StatusGetMixinV3


class GetUserModel(BaseModelORM):
    uuid: UUID
    login: str
    first_name: str
    last_name: str
    login_at: Optional[str] = None
    is_me: Optional[bool] = True

    @validator("login_at", always=True, check_fields=False)
    def validate_login(cls, _: str, values: dict[Any, Any]):
        login = values.get("login")
        return f"@{login}"


class GetUserWithPhoneEmail(GetUserModel):
    phone: str
    email: Optional[EmailStr] = None


class GetCurrentUserModel(GetUserWithPhoneEmail):
    session_id: Optional[UUID] = None


class GetUserWithStatus(GetUserModel, StatusGetMixinV3):
    pass


class CreateUserModel(BaseModelORM):
    login: str
    phone: Phone
    password: str
    first_name: str
    last_name: str
