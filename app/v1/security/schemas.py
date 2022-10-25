from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from pydantic import Field
from pydantic import constr
from pydantic import validator

from phonenumbers import NumberParseException
from phonenumbers import is_valid_number
from phonenumbers import parse as parse_phone_number


from app.v1.schemas.base import BaseModelORM
from app.v1.statuses.schemas import StatusGetMixinV3


class GetAccessTokenModel(BaseModelORM):
    access_token: str
    token_type: str
    user_uuid: UUID


class OAuth2PhonePasswordRequestForm(BaseModelORM):
    grant_type: str = Field(default=None, regex="password")
    phone: str = Field(...)
    password: str

    @validator("phone", always=True)
    def validate_number(cls, v: str):
        try:
            n = parse_phone_number(number=v)
        except NumberParseException as e:
            raise ValueError('Please provide a valid mobile phone number') from e

        if not is_valid_number(n):
            raise ValueError('Please provide a valid mobile phone number')
        return f"{n.country_code}{n.national_number}"


class OAuth2SessionCode(BaseModelORM):
    session_id: UUID = Field(...)
    code: constr(max_length=4)


class DeviceModel(BaseModelORM):
    uuid: UUID
    device_family: Optional[str] = None
    os_version: Optional[str] = None
    browser_version: Optional[str] = None
    country: Optional[str] = None
    device_type: Optional[str] = None
    os_family: Optional[str] = None
    device_brand: Optional[str] = None
    browser_family: Optional[str] = None
    ip: Optional[str] = None
    city: Optional[str] = None


class SessionModel(StatusGetMixinV3):
    uuid: UUID
    device: DeviceModel


class GetSession(BaseModelORM):
    session: UUID
