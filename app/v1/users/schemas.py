from typing import Any
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import EmailStr
from pydantic import Field
from pydantic import validator

from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.phone import Phone
from app.v1.statuses.schemas import StatusGetMixinV3


class RoleDTO(BaseModelORM):
    id: int
    title: str


class AvatarDTO(BaseModelORM):
    document_id: UUID
    url: Optional[str] = None

    @validator("url", always=True, check_fields=False)
    def validate_avatar(cls, _: str, values: dict[Any, Any]):
        avatar_id = values.get("document_id")
        return f"https://document.capi.shitposting.team/v1/documents/{avatar_id}/file"


class GetUserModel(BaseModelORM):
    uuid: UUID
    login: str
    first_name: str
    last_name: str
    login_at: Optional[str] = None

    avatar: AvatarDTO = Field(...)
    role: RoleDTO = Field(...)

    is_me: bool = False

    is_online: bool
    last_activity: datetime

    @validator("login_at", always=True, check_fields=False)
    def validate_login(cls, _: str, values: dict[Any, Any]):
        login = values.get("login")
        return f"@{login}"


class GetMeUserModel(GetUserModel):
    is_me: Optional[bool] = True


class GetUserWithPhoneEmail(GetMeUserModel):
    phone: str
    email: Optional[EmailStr] = None


class GetCurrentUserModel(GetUserWithPhoneEmail):
    session_id: Optional[UUID] = None


class GetUserWithStatus(GetMeUserModel, StatusGetMixinV3):
    pass


class CreateUserModel(BaseModelORM):
    login: str
    phone: Phone
    password: str
    first_name: str
    last_name: str
