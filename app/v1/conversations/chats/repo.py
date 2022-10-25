from uuid import UUID

from sqlalchemy import func
from sqlalchemy import literal_column
from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import aliased
from sqlalchemy.orm import contains_eager
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import noload
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm import with_expression
from sqlalchemy.orm import with_loader_criteria

from app.db.crud.base import BaseCRUD
from app.db.decorators import orm_error_handler
from app.db.models import Chat
from app.db.models import Conversation
from app.db.models import ConversationUser
from app.db.models import User


class ChatRepository:
    def __init__(self, db_session: sessionmaker):
        self.db_session = db_session
        self.model = Conversation

        self.base = BaseCRUD(db_session=db_session, model=self.model)

    @orm_error_handler
    async def get_all_from_user_uuid(self, uuid: UUID) -> list[Conversation]:
        async with self.base.transaction_v2() as transaction:
            UserConversationAlias = aliased(ConversationUser, name="uc2")

            companion_expression = (
                select(
                    User
                )
                .join(
                    UserConversationAlias,
                    UserConversationAlias.user_id == User.uuid,
                )
                .filter(
                    UserConversationAlias.conversation_id == Conversation.uuid,
                    Conversation.type_id == 1,
                    User.uuid != uuid,
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
                    isouter=True
                )
                .join(target=Chat, onclause=Chat.uuid == Conversation.chat_id, isouter=True)
                .options(
                    with_expression(
                        key=Conversation.companion,
                        expression=jsonb_meta_companion.scalar_subquery()
                    ),
                    joinedload(Conversation.chat),
                    joinedload(Conversation.chat_type),
                )
                .options(noload("*"))
                .filter(ConversationUser.user_id == uuid)
            )
            print(
                stmt.compile(dialect=postgresql.dialect(), compile_kwargs={'literal_binds': True})
                )
            cursor = await transaction.execute(stmt)
            return cursor.scalars().all()
