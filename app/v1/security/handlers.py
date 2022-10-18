from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.v1.schemas.responses import BaseResponse
from app.v1.security.auth import authenticate
from app.v1.security.auth import create_access_token
from app.v1.security.auth import get_current_user
from app.v1.security.forms import OAuth2PhonePasswordRequestForm
from app.v1.security.schemas import GetAccessTokenModel
from app.v1.users.dependencies import UsersDependencyMarker
from app.v1.users.schemas import GetUserWithPhoneEmail
from app.v1.users.services import UserService

security_router = APIRouter()


@security_router.post(
    "/login",
    summary="Авторизовать пользователя",
    response_model=BaseResponse[GetAccessTokenModel]
)
async def login(
    user_service: UserService = Depends(UsersDependencyMarker),
    form_data: OAuth2PhonePasswordRequestForm = Depends(),
):
    """
    Авторизация пользователя в сервисе<br><br>

    username, password - обязательные поля<br>
    grant_type, scope, client_id, client_secret - Опциональные поля<br><br>

    В случае успешной авторизации отправляется access_token
    """
    user = await authenticate(
        phone=form_data.phone,
        password=form_data.password,
        user_service=user_service,
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    result = {
            "access_token": create_access_token(user=user),
            "token_type": "bearer",
            "user_uuid": user.uuid,
        }

    return {
        "result": result
    }


@security_router.get(
    "/me",
    response_model=BaseResponse[GetUserWithPhoneEmail],
    summary="Получить сущность текущего пользователя",
)
async def read_users_me(
    current_user: GetUserWithPhoneEmail = Depends(get_current_user),
):
    """
    Получить сущность текущего авторизованного пользователя
    """
    return {
        "result": current_user
    }
