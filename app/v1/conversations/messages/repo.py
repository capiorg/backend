from typing import List
from typing import Optional
from typing import Sequence
from typing import Type
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy import case
from sqlalchemy import desc
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm import with_expression

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import ConversationUser
from app.db.models import Document
from app.db.models import Message
from app.db.models import MessageDocument
from app.db.models import User
from app.dto.documents import SystemFileDTO


class MessageRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = Message

        self.base = BaseCRUD(db_session=db_session, model=self.model)
        self.base_conversation = BaseCRUD(
            db_session=db_session, model=ConversationUser
        )

    def create_many_files_messages_stmt(self, data: list[dict[str, str]]):
        return (
            insert(MessageDocument)
            .values(data)
            .on_conflict_do_nothing()
            .returning(MessageDocument.uuid)
        )

    def create_many_files_stmt(self, data: list[dict[str, UUID]]):
        return (
            insert(Document)
            .values(data)
            .on_conflict_do_nothing()
            .returning(Document.uuid)
        )

    @orm_error_handler
    async def create(
        self,
        conversation_id: UUID,
        author_id: UUID,
        text: str,
        files: list[UUID],
        reply_uuid: Optional[UUID] = None,
    ) -> Message:
        async with self.base.transaction_v2() as transaction:
            if not await self.base_conversation.exists(
                ConversationUser.user_id == author_id,
                ConversationUser.conversation_id == conversation_id,
                transaction=transaction,
            ):
                user_conversation = ConversationUser(
                    conversation_id=conversation_id,
                    user_id=author_id,
                )
                transaction.add(user_conversation)
                await transaction.flush()

            created_message = Message(
                conversation_id=conversation_id,
                author_id=author_id,
                parent_id=reply_uuid,
                text=text,
            )
            transaction.add(created_message)
            await transaction.flush()

            if files:
                files_data = [
                    dict(
                        document_id=element,
                    )
                    for element in files
                ]

                stmt_files = self.create_many_files_stmt(
                    data=files_data
                )

                curr = await transaction.execute(stmt_files)
                result = curr.scalars().all()

                files_messages_data = [
                    dict(
                        message_id=created_message.uuid,
                        document_id=element,
                    )
                    for element in result
                ]

                stmt_files = self.create_many_files_messages_stmt(
                    data=files_messages_data
                )
                await transaction.execute(stmt_files)

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
        message_alias_table = aliased(Message, name="m2")

        is_me_case = self.__is_me_expression(user_id=user_id)
        count_thread_messages = self.__count_thread_messages__expression(
            alias_t=message_alias_table
        ).scalar_subquery()

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
                ).options(joinedload(User.avatar), joinedload(User.role)),
                with_expression(
                    self.model.thread_count, count_thread_messages
                ),
                subqueryload(self.model.documents),
            )
            .limit(limit)
            .offset(offset)
            .order_by(desc(self.model.created_at))
        )

        async with self.base.transaction_v2() as transaction:
            curr = await transaction.execute(stmt)
            return curr.scalars().all()

    @orm_error_handler
    async def get_one(self, message_uuid: UUID, user_id: UUID) -> Message:
        message_alias_table = aliased(Message, name="m2")
        is_me_case = self.__is_me_expression(user_id=user_id)
        count_thread_messages = self.__count_thread_messages__expression(
            alias_t=message_alias_table
        )

        stmt = (
            select(self.model)
            .filter(self.model.uuid == message_uuid)
            .options(
                joinedload(self.model.author).with_expression(
                    User.is_me, is_me_case
                ).options(joinedload(User.avatar), joinedload(User.role)),
                with_expression(
                    self.model.thread_count,
                    count_thread_messages.scalar_subquery(),
                ),
                subqueryload(self.model.documents)
            )
        )

        async with self.base.transaction_v2() as transaction:
            curr = await transaction.execute(stmt)
            return curr.scalar_one()

    @orm_error_handler
    async def delete(self, chat_id: UUID, message_uuid: UUID) -> UUID:
        async with self.base.transaction_v2() as transaction:
            return await self.base.delete_one(
                self.model.conversation_id == chat_id,
                self.model.uuid == message_uuid,
                transaction=transaction,
            )

    @orm_error_handler
    async def update(
        self,
        chat_id: UUID,
        message_uuid: UUID,
        text: str,
    ) -> Message:
        async with self.base.transaction_v2() as transaction:
            return await self.base.update(
                self.model.conversation_id == chat_id,
                self.model.uuid == message_uuid,
                text=text,
                transaction=transaction,
            )

    def __is_me_expression(self, user_id: UUID):
        return case(
            [(self.model.author_id == user_id, True)], else_=False
        ).label("is_me")

    def __count_thread_messages__expression(self, alias_t: Type[Message]):
        return select(func.count()).select_from(
            select(alias_t)
            .where(alias_t.parent_id == self.model.uuid)
            .correlate(self.model)
            .subquery()
        )
