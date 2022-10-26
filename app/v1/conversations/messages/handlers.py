from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from pyfa_converter import BodyDepends

from app.utils.decorators import standardize_response
from app.v1.conversations.messages.dependencies import MessageDependencyMarker
from app.v1.conversations.messages.schemas import MessageGetModel
from app.v1.conversations.messages.schemas import MessageSendModel
from app.v1.conversations.messages.services import MessageService
from app.v1.schemas.responses import BaseResponse
from app.v1.security.auth import GetCurrentUser
from app.v1.statuses.enums import StatusEnum
from app.v1.users.schemas import GetCurrentUserModel

message_router = APIRouter()


@message_router.get(
    "/chats/{chat_id}/messages",
    response_model=BaseResponse[list[MessageGetModel]],
    summary="Получить все сообщения чата",
)
@standardize_response(status_code=200)
async def get_messages_from_chat(
    chat_id: UUID,
    chat_repo: MessageService = Depends(MessageDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Получить активные чаты пользователя
    """
    return await chat_repo.get_all(user_id=current_user.uuid, chat_id=chat_id)


@message_router.get(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=BaseResponse[list[MessageGetModel]],
    summary="Получить все сообщения треда",
)
@standardize_response(status_code=200)
async def get_messages_from_chat_and_message(
    chat_id: UUID,
    message_id: UUID,
    chat_repo: MessageService = Depends(MessageDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Получить активные чаты пользователя
    """
    return await chat_repo.get_all(user_id=current_user.uuid, chat_id=chat_id, message_id=message_id)


@message_router.post(
    "/chats/{chat_id}/messages",
    response_model=BaseResponse,
    summary="Отправить сообщение в чат",
)
@standardize_response(status_code=200)
async def send_message_to_chat(
    chat_id: UUID,
    data: MessageSendModel,
    chat_repo: MessageService = Depends(MessageDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Отправить сообщение в чат
    """
    await chat_repo.create(
        conversation_id=chat_id,
        author_id=current_user.uuid,
        reply_uuid=data.reply_uuid,
        text=data.text,
    )
    return None


@message_router.post(
    "/chats/{chat_id}/photos",
    response_model=BaseResponse,
    summary="Отправить фото в чат",
    deprecated=True,
)
@standardize_response(status_code=200)
async def send_photo_to_chat(
    chat_id: UUID,
    file: list[UploadFile],
    data: MessageSendModel = BodyDepends(MessageSendModel),
    chat_repo: MessageService = Depends(MessageDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Отправить фотографию/фотографии в чат
    """
    await chat_repo.create(
        conversation_id=chat_id,
        author_id=current_user.uuid,
        reply_uuid=data.reply_uuid,
        text=data.text,
    )
    return None
