from typing import Optional
from uuid import UUID

from sqlalchemy.orm import sessionmaker

from app.db.models import Message
from app.v1.conversations.messages.repo import MessageRepository


class MessageService(MessageRepository):
    def __init__(self, db_session: sessionmaker):
        super().__init__(db_session=db_session)

    async def create(
        self,
        conversation_id: UUID,
        author_id: UUID,
        text: str,
        reply_uuid: Optional[UUID] = None,
    ) -> Message:
        return await super(MessageService, self).create(
            conversation_id=conversation_id,
            author_id=author_id,
            reply_uuid=reply_uuid,
            text=text,
        )

    async def get_all(
        self,
        user_id: UUID,
        chat_id: UUID,
        message_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Message]:
        return await super(MessageService, self).get_all(
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            limit=limit,
            offset=offset,
        )
