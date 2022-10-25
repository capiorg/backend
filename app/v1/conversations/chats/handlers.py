from fastapi import APIRouter
from fastapi import Depends

from app.utils.decorators import standardize_response
from app.v1.conversations.chats.dependencies import ChatDependencyMarker
from app.v1.conversations.chats.repo import ChatRepository
from app.v1.schemas.responses import BaseResponse
from app.v1.security.auth import GetCurrentUser
from app.v1.statuses.enums import StatusEnum
from app.v1.users.schemas import GetCurrentUserModel

chat_router = APIRouter()


@chat_router.get(
    "/chats",
    # response_model=BaseResponse[GetCurrentUserModel],
    summary="Получить все чаты пользователя",
)
@standardize_response(status_code=200)
async def get_chats(
    chat_repo: ChatRepository = Depends(ChatDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        GetCurrentUser(
            status=[StatusEnum.ACTIVE]
        )
    ),
):
    """
    Получить активные чаты пользователя
    """
    return await chat_repo.get_all_from_user_uuid(uuid=current_user.uuid)
