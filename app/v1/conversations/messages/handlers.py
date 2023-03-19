from uuid import UUID
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import UploadFile
from pyfa_converter import BodyDepends
from pyfa_converter import PyFaDepends

from app.utils.decorators import standardize_response
from app.v1.conversations.messages.dependencies import MessageDependencyMarker
from app.v1.conversations.messages.dependencies import (
    MessageServiceDependencyMarker,
)
from app.v1.conversations.messages.schemas import MessageDeleteModel
from app.v1.conversations.messages.schemas import MessageGetModel
from app.v1.conversations.messages.schemas import MessageSendModel
from app.v1.conversations.messages.schemas import QueryMessageModel
from app.v1.conversations.messages.schemas import UpdateMessageModel
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
    filters: QueryMessageModel = PyFaDepends(QueryMessageModel, _type=Query),
    chat_repo: MessageService = Depends(MessageDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Получить активные чаты пользователя
    """
    return await chat_repo.get_all(
        user_id=current_user.uuid,
        chat_id=chat_id,
        limit=filters.limit,
        offset=filters.offset,
    )


@message_router.get(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=BaseResponse[list[MessageGetModel]],
    summary="Получить все сообщения треда",
)
@standardize_response(status_code=200)
async def get_messages_from_chat_and_message(
    chat_id: UUID,
    message_id: UUID,
    chat_service: MessageService = Depends(MessageDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Получить активные чаты пользователя
    """
    return await chat_service.get_all(
        user_id=current_user.uuid, chat_id=chat_id, message_id=message_id
    )


@message_router.post(
    "/chats/{chat_id}/messages",
    response_model=BaseResponse,
    summary="Отправить сообщение в чат",
)
@standardize_response(status_code=200)
async def send_message_to_chat(
    chat_id: UUID,
    data: MessageSendModel,
    chat_service: MessageService = Depends(MessageServiceDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Отправить сообщение в чат
    """
    await chat_service.create(
        conversation_id=chat_id,
        author=current_user,
        reply_uuid=data.reply_uuid,
        text=data.text,
        files=data.documents,
    )
    return None


@message_router.delete(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=BaseResponse[MessageDeleteModel],
    summary="Удалить сообщение из чата",
)
@standardize_response(status_code=200)
async def delete_message_from_chat(
    chat_id: UUID,
    message_id: UUID,
    chat_service: MessageService = Depends(MessageServiceDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Отправить сообщение в чат
    """
    result = await chat_service.delete(
        message_id=message_id,
        conversation_id=chat_id,
        author=current_user,
    )
    return MessageDeleteModel(uuid=result)


@message_router.patch(
    "/chats/{chat_id}/messages/{message_id}",
    response_model=BaseResponse[MessageGetModel],
    summary="Обновить сообщение из чата",
)
@standardize_response(status_code=200)
async def update_message_in_chat(
    chat_id: UUID,
    message_id: UUID,
    data: UpdateMessageModel,
    chat_service: MessageService = Depends(MessageServiceDependencyMarker),
    current_user: GetCurrentUserModel = Depends(
        dependency=GetCurrentUser(status=[StatusEnum.ACTIVE])
    ),
):
    """
    Обновить сообщение в чате
    """
    result = await chat_service.update(
        message_id=message_id,
        conversation_id=chat_id,
        author=current_user,
        text=data.text,
    )
    return result
