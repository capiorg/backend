import datetime
from typing import Optional
from uuid import UUID

from app.db.models import Message
from app.services.redis.queue.client import RedisSocketQueue
from app.v1.conversations.messages.repo import MessageRepository
from app.v1.conversations.messages.schemas import MessageDeleteSocketModel
from app.v1.conversations.messages.schemas import MessageGetModel
from app.v1.users.schemas import GetCurrentUserModel
from app.utils.encoders import jsonable_encoder
from app.v1.users.schemas import GetUserModel


class MessageService:
    def __init__(
        self,
        repo: MessageRepository,
        redis: RedisSocketQueue,
    ):
        self.repo = repo
        self.redis = redis

    async def create(
        self,
        conversation_id: UUID,
        author: GetCurrentUserModel,
        text: str,
        files: list[UUID],
        reply_uuid: Optional[UUID] = None,
    ) -> Message:
        created_message = await self.repo.create(
            conversation_id=conversation_id,
            author_id=author.uuid,
            reply_uuid=reply_uuid,
            text=text,
            files=files,
        )
        get_created_message = await self.repo.get_one(
            message_uuid=created_message.uuid, user_id=author.uuid
        )
        if reply_uuid:
            reply_message = await self.repo.get_one(
                message_uuid=reply_uuid,
                user_id=author.uuid,
            )
            data_for_socket = MessageGetModel.from_orm(reply_message)
            await self.redis.emit(
                "updateMessageResponse",
                jsonable_encoder(data_for_socket.dict(by_alias=True)),
                namespace="/v1",
            )

        data_for_socket = MessageGetModel.from_orm(get_created_message)
        await self.redis.emit(
            "newMessageResponse",
            jsonable_encoder(data_for_socket.dict(by_alias=True)),
            namespace="/v1",
        )

        return get_created_message

    async def get_all(
        self,
        user_id: UUID,
        chat_id: UUID,
        message_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Message]:
        return await self.repo.get_all(
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            limit=limit,
            offset=offset,
        )

    async def delete(
        self,
        conversation_id: UUID,
        message_id: UUID,
        author: GetCurrentUserModel,
    ) -> UUID:
        message = await self.repo.get_one(
            message_uuid=message_id,
            user_id=author.uuid,
        )

        await self.repo.delete(
            chat_id=conversation_id,
            message_uuid=message_id,
        )

        data_for_socket = MessageDeleteSocketModel(
            uuid=message_id,
            conversation_id=conversation_id,
            reply_uuid=message.parent_id,
            author=GetUserModel(
                first_name=author.first_name,
                last_name=author.last_name,
                uuid=author.uuid,
                login=author.login,
                avatar=author.avatar,
                is_online=author.is_online,
                last_activity=author.last_activity,
                role=author.role,
            ),
        )
        await self.redis.emit(
            "deleteMessageResponse",
            jsonable_encoder(data_for_socket.dict()),
            namespace="/v1",
        )

        if message.parent_id:
            reply_message = await self.repo.get_one(
                message_uuid=message.parent_id,
                user_id=author.uuid,
            )
            data_for_socket = MessageGetModel.from_orm(reply_message)
            await self.redis.emit(
                "updateMessageResponse",
                jsonable_encoder(data_for_socket.dict(by_alias=True)),
                namespace="/v1",
            )

        return message_id

    async def update(
        self,
        conversation_id: UUID,
        message_id: UUID,
        author: GetCurrentUserModel,
        text: str,
    ) -> Message:

        await self.repo.update(
            chat_id=conversation_id,
            message_uuid=message_id,
            text=text,
        )
        updated_message = await self.repo.get_one(
            message_uuid=message_id,
            user_id=author.uuid,
        )
        data_for_socket = MessageGetModel.from_orm(updated_message)
        await self.redis.emit(
            "updateMessageResponse",
            jsonable_encoder(data_for_socket.dict()),
            namespace="/v1",
        )

        return updated_message
