from typing import List

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from pyfa_converter import PyFaDepends
from starlette.requests import Request

from app.db.models import SessionTypeEnum
from app.exceptions.routes.models import IncorrectAuthCodeError
from app.exceptions.routes.models import RepeatedAuthCodeError
from app.utils.decorators import standardize_response
from app.v1.schemas.responses import BaseResponse
from app.v1.security.auth import GetCurrentUser
from app.v1.security.auth import authenticate
from app.v1.security.auth import create_access_token
from app.v1.security.dependencies import UserSessionDependencyMarker
from app.v1.security.schemas import GetAccessTokenModel
from app.v1.security.schemas import GetSession
from app.v1.security.schemas import OAuth2PhonePasswordRequestForm
from app.v1.security.schemas import OAuth2SessionCode
from app.v1.security.schemas import SessionModel
from app.v1.security.services import UserSessionService
from app.v1.statuses.enums import StatusEnum
from app.v1.users.dependencies import UsersDependencyMarker
from app.v1.users.schemas import GetCurrentUserModel
from app.v1.users.services import UserService

security_router = APIRouter()


@security_router.post(
    "/auth/login",
    summary="Предварительная авторизация пользователя с последующим FlashCAll",
    response_model=BaseResponse[GetSession],
)
@standardize_response(status_code=200)
async def login(
    request: Request,
    user_service: UserService = Depends(UsersDependencyMarker),
    user_session_service: UserSessionService = Depends(UserSessionDependencyMarker),
    form_data: OAuth2PhonePasswordRequestForm = PyFaDepends(
        OAuth2PhonePasswordRequestForm, _type=Form
        ),
):
    user = await authenticate(
        phone=form_data.phone,
        password=form_data.password,
        user_service=user_service,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    current_ip = request.headers.get("cf-connecting-ip")
    user_agent = request.headers.get("user-agent")

    session_type = (
        SessionTypeEnum.REGISTER if user.status_id == StatusEnum.NOT_ACTIVE
        else SessionTypeEnum.AUTH
    )

    session = await user_session_service.create(
        user=user,
        ip_address=current_ip,
        user_agent=user_agent,
        session_type=session_type
    )

    return {"session": session.uuid}


@security_router.post(
    "/auth/login/verify",
    summary="Авторизовать пользователя по Session и FlashCall code",
    response_model=GetAccessTokenModel,
)
async def login(
    user_service: UserService = Depends(UsersDependencyMarker),
    user_session_service: UserSessionService = Depends(UserSessionDependencyMarker),
    form_data: OAuth2SessionCode = PyFaDepends(
        OAuth2SessionCode, _type=Form
        ),
):
    """
    Авторизация пользователя в сервисе<br><br>

    username, password - обязательные поля<br>
    grant_type, scope, client_id, client_secret - Опциональные поля<br><br>

    В случае успешной авторизации отправляется access_token
    """
    session = await user_session_service.get(uuid=form_data.session_id)
    if session.code == form_data.code:
        if session.status_id == 3:
            await user_session_service.activate_code(uuid=form_data.session_id)
            user = await user_service.get_one_from_uuid(uuid=session.user_id)
            await user_service.activate(uuid=user.uuid)

            access_token = create_access_token(user=user, session=session.uuid)

            result = {
                "access_token": access_token,
                "token_type": "bearer",
                "user_uuid": user.uuid,
            }
            return result
        else:
            raise RepeatedAuthCodeError(
                detail="Re-authentication detected. "
                       "You have already entered this verification code on this device."
            )
    else:
        raise IncorrectAuthCodeError(detail="The verification code was entered incorrectly.")


@security_router.get(
    "/auth/me",
    response_model=BaseResponse[GetCurrentUserModel],
    summary="Получить сущность текущего пользователя",
)
@standardize_response(status_code=200)
async def read_users_me(
    current_user: GetCurrentUserModel = Depends(
        GetCurrentUser(
            status=[StatusEnum.ACTIVE, StatusEnum.NOT_ACTIVE]
        )
    ),
):
    """
    Получить сущность текущего авторизованного пользователя
    """
    return current_user


@security_router.get(
    "/auth/sessions",
    response_model=BaseResponse[List[SessionModel]],
    summary="Получить все сессии",
)
@standardize_response(status_code=200)
async def get_auth_sessions(
    user_session_service: UserSessionService = Depends(UserSessionDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        GetCurrentUser(
            status=[StatusEnum.ACTIVE]
        )
    ),
):
    """
    Получить сущность текущего авторизованного пользователя
    """
    return await user_session_service.repo.get_all(uuid=current_user.uuid)
