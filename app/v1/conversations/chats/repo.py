from uuid import UUID

from sqlalchemy import func
from sqlalchemy import literal_column
from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import noload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import with_expression

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import Chat
from app.db.models import ChatType
from app.db.models import Conversation
from app.db.models import ConversationUser
from app.db.models import Document
from app.db.models import Role
from app.db.models import User
from app.v1.conversations.chats.models import ChatDTO
from app.v1.conversations.chats.models import ChatTypeEnum
from app.v1.conversations.chats.models import CompanionDTO


class ChatRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = Conversation

        self.base = BaseCRUD(db_session=db_session, model=self.model)

    @orm_error_handler
    async def get_all_from_user_uuid(self, uuid: UUID) -> list[Conversation]:
        async with self.base.transaction_v2() as transaction:
            UserConversationAlias = aliased(ConversationUser, name="uc2")
            UserAlias = aliased(User, name="u1")

            avatar_expression = (
                select(Document)
                .filter(Document.uuid == UserAlias.avatar_id)
                .correlate(UserAlias)
            ).alias("meta_avatar")

            jsonb_meta_avatar = select(
                func.to_jsonb(literal_column("meta_avatar"))
            ).select_from(avatar_expression)

            role_expression = (
                select(Role)
                .filter(Role.id == UserAlias.role_id)
                .correlate(UserAlias)
            ).alias("meta_role")

            jsonb_meta_role = select(
                func.to_jsonb(literal_column("meta_role"))
            ).select_from(role_expression)


            companion_expression = (
                select(
                    UserAlias,
                    jsonb_meta_avatar.label("avatar"),
                    jsonb_meta_role.label("role"),
                )
                .join(
                    UserConversationAlias,
                    UserConversationAlias.user_id == UserAlias.uuid,
                )
                .filter(
                    UserConversationAlias.conversation_id == Conversation.uuid,
                    Conversation.type_id == 1,
                    UserAlias.uuid != uuid,
                )
                .correlate(Conversation)
            ).alias("meta_json")

            jsonb_meta_companion = select(
                func.to_jsonb(literal_column("meta_json"))
            ).select_from(companion_expression)

            stmt = (
                select(Conversation)
                .join(
                    target=ConversationUser,
                    onclause=ConversationUser.conversation_id
                             == Conversation.uuid,
                    isouter=True,
                )
                .join(
                    target=Chat,
                    onclause=Chat.uuid == Conversation.chat_id,
                    isouter=True,
                )
                .join(
                    target=ChatType,
                    onclause=ChatType.id == Conversation.type_id,
                    isouter=True,
                )
                .options(
                    with_expression(
                        key=Conversation.companion,
                        expression=jsonb_meta_companion.scalar_subquery(),
                    ),
                    contains_eager(Conversation.chat),
                    contains_eager(Conversation.chat_type),
                )
                .options(noload("*"))
                .filter(
                    or_(
                        ConversationUser.user_id == uuid,
                        Conversation.type_id == 3,
                    )
                )
                .group_by(Conversation.uuid, Chat.uuid, ChatType.id)
            )

            cursor = await transaction.execute(stmt)
            return cursor.scalars().all()

    @orm_error_handler
    async def get_one_from_conversation_uuid(
        self,
        user_uuid: UUID,
        chat_uuid: UUID
    ) -> Conversation:
        async with self.base.transaction_v2() as transaction:
            UserConversationAlias = aliased(ConversationUser, name="uc2")
            UserAlias = aliased(User, name="u1")

            avatar_expression = (
                select(Document)
                .filter(Document.uuid == UserAlias.avatar_id)
                .correlate(UserAlias)
            ).alias("meta_avatar")

            jsonb_meta_avatar = select(
                func.to_jsonb(literal_column("meta_avatar"))
            ).select_from(avatar_expression)

            role_expression = (
                select(Role)
                .filter(Role.id == UserAlias.role_id)
                .correlate(UserAlias)
            ).alias("meta_role")

            jsonb_meta_role = select(
                func.to_jsonb(literal_column("meta_role"))
            ).select_from(role_expression)

            companion_expression = (
                select(
                    UserAlias,
                    jsonb_meta_avatar.label("avatar"),
                    jsonb_meta_role.label("role")
                )
                .join(
                    UserConversationAlias,
                    UserConversationAlias.user_id == UserAlias.uuid,
                )
                .filter(
                    UserConversationAlias.conversation_id == Conversation.uuid,
                    Conversation.type_id == 1,
                    UserAlias.uuid != user_uuid,
                )
                .correlate(Conversation)
            ).alias("meta_json")

            jsonb_meta_companion = select(
                func.to_jsonb(literal_column("meta_json"))
            ).select_from(companion_expression)

            stmt = (
                select(Conversation)
                .join(
                    target=ConversationUser,
                    onclause=ConversationUser.conversation_id == Conversation.uuid,
                    isouter=True,
                )
                .join(
                    target=Chat,
                    onclause=Chat.uuid == Conversation.chat_id,
                    isouter=True,
                )
                .join(
                    target=ChatType,
                    onclause=ChatType.id == Conversation.type_id,
                    isouter=True,
                )
                .options(
                    with_expression(
                        key=Conversation.companion,
                        expression=jsonb_meta_companion.scalar_subquery(),
                    ),
                    contains_eager(Conversation.chat),
                    contains_eager(Conversation.chat_type),
                )
                .options(noload("*"))
                .filter(
                    ConversationUser.user_id == user_uuid,
                )
                .filter(Conversation.uuid == chat_uuid)
                .group_by(Conversation.uuid, Chat.uuid, ChatType.id)
            )
            cursor = await transaction.execute(stmt)
            return cursor.scalar_one()

    @orm_error_handler
    async def get_private_chat_from_users(self, user_1: UUID, user_2: UUID) -> Conversation:

        sub = (
            select(ConversationUser.conversation_id)
            .select_from(ConversationUser)
            .filter(
                ConversationUser.conversation_id == Conversation.uuid,
                ConversationUser.user_id == user_2
            )
            .correlate(Conversation)
        )

        stmt_own = (
            select(Conversation)
            .select_from(Conversation)
            .join(
                ConversationUser,
                ConversationUser.conversation_id == Conversation.uuid
            )
            .filter(Conversation.type_id == 1)
            .filter(ConversationUser.user_id == user_1)
            .filter(
                Conversation.uuid.in_(
                    sub
                )
            )
        )
        curr = await self.base.execute(stmt_own)
        return curr.scalar_one_or_none()

    @orm_error_handler
    async def create_chat(
        self,
        user_id: UUID,
        type_: ChatTypeEnum,
        chat: ChatDTO,
        companion: CompanionDTO,
    ) -> Conversation:
        async with self.base.transaction_v2() as transaction:

            if type_ == ChatTypeEnum.PUBLIC:
                chat = Chat(title=chat.title)
                transaction.add(chat)
                await transaction.flush()
                conversation = Conversation(chat_id=chat.uuid, type_id=3)
                transaction.add(conversation)
                await transaction.flush()

                user_conversation = ConversationUser(
                    conversation_id=conversation.uuid,
                    user_id=user_id,
                )
                transaction.add(user_conversation)

            if type_ == ChatTypeEnum.PRIVATE:
                created_chat = await self.get_private_chat_from_users(
                    user_1=user_id,
                    user_2=companion.uuid,
                )
                if created_chat:
                    return created_chat
                else:

                    conversation = Conversation(type_id=1)
                    transaction.add(conversation)
                    await transaction.flush()

                    author_conversation = ConversationUser(
                        conversation_id=conversation.uuid,
                        user_id=user_id,
                    )
                    transaction.add(author_conversation)

                    companion_conversation = ConversationUser(
                        conversation_id=conversation.uuid,
                        user_id=companion.uuid,
                    )
                    transaction.add(companion_conversation)

            await transaction.commit()
            return conversation
