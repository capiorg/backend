from typing import Optional
from uuid import UUID

from pydantic import EmailStr
from pydantic import validator

from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.phone import Phone


class GetUserModel(BaseModelORM):
    uuid: UUID
    login: str
    first_name: str
    last_name: str
    login_at: Optional[str] = None

    @validator("login_at")
    def validate_login(cls, v: str):
        return f"@{v}"


class GetUserWithPhoneEmail(GetUserModel):
    phone: Phone
    email: EmailStr
