from fastapi import APIRouter
from fastapi import Depends

from app.utils.decorators import standardize_response
from app.v1.schemas.responses import BaseResponse
from app.v1.users.dependencies import UsersDependencyMarker
from app.v1.users.schemas import CreateUserModel
from app.v1.users.schemas import GetUserWithPhoneEmail
from app.v1.users.services import UserService

user_router = APIRouter()


@user_router.post(
    "/auth/register",
    summary="Создание пользователя",
    response_model=BaseResponse[GetUserWithPhoneEmail],
    status_code=200,
)
@standardize_response(status_code=200)
async def create_user(
    data: CreateUserModel,
    user_service: UserService = Depends(UsersDependencyMarker),
):
    user = await user_service.create(
        phone=data.phone,
        first_name=data.first_name,
        last_name=data.last_name,
        login=data.login,
        password=data.password,
        status_id=3,
    )
    return user
