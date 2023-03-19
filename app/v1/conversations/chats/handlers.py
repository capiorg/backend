from typing import Any
from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from app.utils.decorators import standardize_response
from app.v1.conversations.chats.dependencies import ChatDependencyMarker
from app.v1.conversations.chats.models import CreateChatModel
from app.v1.conversations.chats.models import GetChatDTO
from app.v1.conversations.chats.repo import ChatRepository
from app.v1.schemas.responses import BaseResponse
from app.v1.security.auth import GetCurrentUser
from app.v1.statuses.enums import StatusEnum
from app.v1.users.schemas import GetCurrentUserModel

chat_router = APIRouter()


@chat_router.get(
    "/chats",
    response_model=BaseResponse[list[GetChatDTO]],
    summary="Получить все чаты пользователя",
)
@standardize_response(status_code=200)
async def get_chats(
    chat_repo: ChatRepository = Depends(ChatDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Получить активные чаты пользователя
    """
    return await chat_repo.get_all_from_user_uuid(uuid=current_user.uuid)


@chat_router.post(
    "/chats",
    response_model=BaseResponse[GetChatDTO],
    summary="Создать чат",
)
@standardize_response(status_code=200)
async def create_public_chat(
    data: CreateChatModel,
    chat_repo: ChatRepository = Depends(ChatDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Создать чат
    """
    conversation = await chat_repo.create_chat(
        user_id=current_user.uuid,
        type_=data.type,
        chat=data.chat,
        companion=data.companion,
    )
    return await chat_repo.get_one_from_conversation_uuid(
        user_uuid=current_user.uuid,
        chat_uuid=conversation.uuid
    )


@chat_router.get(
    "/chats/{uuid}",
    response_model=BaseResponse[GetChatDTO],
    summary="Получить чат",
)
@standardize_response(status_code=200)
async def create_public_chat(
    uuid: UUID,
    chat_repo: ChatRepository = Depends(ChatDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Получить чат
    """
    return await chat_repo.get_one_from_conversation_uuid(
        user_uuid=current_user.uuid,
        chat_uuid=uuid
    )
