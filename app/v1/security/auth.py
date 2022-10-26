from datetime import datetime
from datetime import timedelta
from typing import List
from typing import MutableMapping
from typing import Optional
from typing import Union
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from jose import jwt
from starlette import status as starlette_status

from app.db.models import User
from app.v1.security.context import verify_password
from app.v1.statuses.enums import StatusEnum
from app.v1.users.dependencies import UsersDependencyMarker
from app.v1.users.schemas import GetCurrentUserModel
from app.v1.users.schemas import GetUserWithPhoneEmail
from app.v1.users.services import UserService
from config import settings_app
from misc import cache

JWTPayloadMapping = MutableMapping[
    str, Union[datetime, bool, str, List[str], List[int]]
]

auth_scheme = HTTPBearer()


credentials_exception = HTTPException(
    status_code=starlette_status.HTTP_401_UNAUTHORIZED,
    detail="Введен неверный логин или пароль, либо учетная запись не существует.",
    headers={"WWW-Authenticate": "Bearer"},
)

account_disabled = HTTPException(
    status_code=starlette_status.HTTP_403_FORBIDDEN,
    detail="Ваша учетная запись деактивирована. Обратитесь к администратору веб-сайта.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def authenticate(
    *,
    phone: str,
    password: str,
    user_service: UserService = Depends(UsersDependencyMarker),
) -> Optional[User]:
    user = await user_service.get_one_from_phone(phone=phone)
    if user.status_id == StatusEnum.DELETED:
        raise account_disabled

    if not user:
        raise credentials_exception

    if not verify_password(password, user.password):
        raise credentials_exception
    return user


def create_access_token(*, user: User, session: UUID) -> str:
    return _create_token(
        token_type="access_token",
        lifetime=timedelta(
            minutes=settings_app.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        ),
        sub=str(user.uuid),
        session=str(session),
    )


def _create_token(
    token_type: str,
    lifetime: timedelta,
    sub: str,
    session: str,
) -> str:
    payload = {}
    expire = datetime.utcnow() + lifetime
    payload["type"] = token_type
    payload["exp"] = expire
    payload["iat"] = datetime.utcnow()
    payload["sub"] = str(sub)
    payload["session"] = session

    return jwt.encode(
        payload, settings_app.JWT_SECRET, algorithm=settings_app.JWT_ALGORITHM
    )


def remove_token_type_in_token(token: str):
    if token.lower().startswith("bearer"):
        token = token.replace("Bearer ", "")
    return token


async def decode_jwt(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
):
    reformat_token = remove_token_type_in_token(token.credentials)

    try:
        payload = jwt.decode(
            reformat_token,
            settings_app.JWT_SECRET,
            algorithms=[settings_app.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        sub = payload.get("sub", None)
        session = payload.get("session", None)

    except JWTError:
        raise credentials_exception

    if sub is None:
        raise credentials_exception

    return sub, session


class GetCurrentUser:
    def __init__(self, status: Optional[List[StatusEnum]] = None):
        self.status = status or [StatusEnum.ACTIVE]

    @cache.hit(
        ttl=timedelta(minutes=10),
        cache_hits=100,
        update_after=50,
        key="users:get_current:{token}",
        prefix="v1",
    )
    async def __call__(
        self,
        user_service: UserService = Depends(UsersDependencyMarker),
        token: HTTPAuthorizationCredentials = Depends(dependency=auth_scheme),
    ):
        jwt_user_uuid, jwt_session_id = await decode_jwt(token=token)
        user_db = await user_service.get_one_from_uuid(jwt_user_uuid)
        if user_db is None:
            raise credentials_exception

        if user_db.status_id not in self.status:
            raise account_disabled

        result = GetCurrentUserModel.from_orm(user_db)
        result.session_id = jwt_session_id

        return result
