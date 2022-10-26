from typing import List
from typing import Optional
from uuid import UUID

from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import with_expression

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import ConversationUser
from app.db.models import Message
from app.db.models import User


class MessageRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = Message

        self.base = BaseCRUD(db_session=db_session, model=self.model)
        self.base_conversation = BaseCRUD(
            db_session=db_session, model=ConversationUser
        )

    @orm_error_handler
    async def create(
        self,
        conversation_id: UUID,
        author_id: UUID,
        text: str,
        reply_uuid: Optional[UUID] = None,
    ) -> Message:
        async with self.base.transaction_v2() as transaction:
            if not await self.base_conversation.exists(
                ConversationUser.user_id == author_id,
                ConversationUser.conversation_id == conversation_id,
            ):
                user_conversation = ConversationUser(
                    conversation_id=conversation_id,
                    user_id=author_id,
                )
                transaction.add(user_conversation)
                await transaction.flush()

            created_message = await self.base.insert(
                conversation_id=conversation_id,
                author_id=author_id,
                parent_id=reply_uuid,
                text=text,
            )
            await transaction.commit()
            return created_message

    @orm_error_handler
    async def get_all(
        self,
        user_id: UUID,
        chat_id: UUID,
        message_id: Optional[UUID] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Message]:
        MessageAlias = aliased(Message, name="m2")

        is_me_case = case(
            [(self.model.author_id == user_id, True)], else_=False
        ).label("is_me")

        count_thread_messages = select(func.count()).select_from(
            select(MessageAlias)
            .where(MessageAlias.parent_id == self.model.uuid)
            .correlate(self.model)
            .subquery()
        )
        stmt = select(self.model)
        stmt = stmt.filter(self.model.conversation_id == chat_id)

        if message_id:
            stmt = stmt.filter(self.model.parent_id == message_id)
        else:
            stmt = stmt.filter(self.model.parent_id.is_(None))

        stmt = (
            stmt.options(
                joinedload(self.model.author).with_expression(
                    User.is_me, is_me_case
                ),
                with_expression(
                    self.model.thread_count, count_thread_messages
                ),
            )
            .limit(limit)
            .offset(offset)
            .order_by(self.model.uuid)
        )

        async with self.base.transaction_v2() as transaction:
            curr = await transaction.execute(stmt)
            return curr.scalars().all()
