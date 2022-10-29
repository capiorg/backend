from typing import Optional
from uuid import UUID

from app.db.models import Message
from app.services.redis.queue.client import RedisSocketQueue
from app.v1.conversations.messages.repo import MessageRepository
from app.v1.conversations.messages.schemas import MessageGetModel
from app.v1.users.schemas import GetCurrentUserModel
from app.utils.encoders import jsonable_encoder


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
        reply_uuid: Optional[UUID] = None,
    ) -> Message:
        created_message = await self.repo.create(
            conversation_id=conversation_id,
            author_id=author.uuid,
            reply_uuid=reply_uuid,
            text=text,
        )
        get_created_message = await self.repo.get_one(
            message_uuid=created_message.uuid, user_id=created_message.uuid
        )

        data_for_socket = MessageGetModel.from_orm(get_created_message)
        await self.redis.emit(
            "newMessageResponse",
            jsonable_encoder(data_for_socket.dict()),
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
