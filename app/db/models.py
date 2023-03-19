import enum

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import query_expression
from sqlalchemy.orm import relationship
from sqlalchemy.sql.functions import current_timestamp
from uuid_extensions import uuid7

from app.db.mixins import TimestampMixin
from misc import Base


class SessionTypeEnum(str, enum.Enum):
    REGISTER = "REGISTER"
    AUTH = "AUTH"


class Statuses(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)


class StatusMixin(Base):
    __abstract__ = True

    @declared_attr
    def status_id(cls):
        return Column(
            Integer, ForeignKey(column=Statuses.id), default=1, nullable=True
        )

    @declared_attr
    def status(cls):
        return relationship(argument="Statuses", viewonly=True, lazy="joined")


class Document(
    TimestampMixin,
    Base,
):
    __tablename__ = "documents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    document_id = Column(UUID(as_uuid=True))
    filename = Column(Text, nullable=True)
    size_bytes = Column(Numeric, nullable=True)
    mime_type = Column(String(255), nullable=True)


class User(TimestampMixin, StatusMixin, Base):
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    phone = Column(String(20), index=True, nullable=False, unique=True)
    email = Column(String, unique=True, nullable=True)
    login = Column(String, nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password = Column(String)

    is_online = Column(Boolean, default=False)
    last_activity = Column(DateTime, default=current_timestamp())

    avatar_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.uuid")
    )
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    is_me = query_expression()

    conversations = relationship(
        "Conversation", secondary="users_conversations"
    )
    avatar = relationship(
        "Document",
    )
    role = relationship(
        "Role",
    )


class ChatType(Base):
    __tablename__ = "chats_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Chat(TimestampMixin, StatusMixin, Base):
    __tablename__ = "chats"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    title = Column(
        String, nullable=True, comment="Если type group - название чата"
    )
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.uuid"), nullable=True
    )

    document = relationship("Document", viewonly=True, lazy="joined")
    conversation = relationship("Conversation", back_populates="chat")


class ConversationUser(TimestampMixin, Base):
    __tablename__ = "users_conversations"

    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.uuid"), primary_key=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True
    )


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    type_id = Column(Integer, ForeignKey("chats_types.id"))
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.uuid"))

    chat = relationship("Chat", viewonly=True, uselist=False)
    chat_type = relationship("ChatType", viewonly=True, lazy="joined")
    type = association_proxy("chat_type", attr="name")

    companion = query_expression()

    # @declared_attr
    # def companion(self):
    #     return self.user_relationship(use_list=False)
    #
    # @declared_attr
    # def users(self):
    #     return relationship(
    #         "User",
    #         uselist=True,
    #         viewonly=True,
    #         secondary="join(ConversationUser, User, ConversationUser.user_id == User.uuid)",
    #         primaryjoin=lambda: and_(
    #             Conversation.uuid == ConversationUser.conversation_id,
    #             Conversation.type_id == 1
    #         ),
    #         secondaryjoin="User.uuid == ConversationUser.user_id",
    #     )
    #
    # @classmethod
    # def user_relationship(cls, use_list: bool):
    #     return relationship(
    #         "User",
    #         uselist=False,
    #         viewonly=True,
    #         secondary=lambda: join(
    #             ConversationUser,
    #             User,
    #             ConversationUser.user_id == User.uuid)
    #         ,
    #         primaryjoin=lambda: and_(Conversation.uuid == ConversationUser.conversation_id),
    #         secondaryjoin="User.uuid == ConversationUser.user_id",
    #     )


class SessionDevice(Base):
    __tablename__ = "sessions_devices"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)

    device_type = Column(String, nullable=True)
    device_brand = Column(String, nullable=True)
    device_family = Column(String, nullable=True)

    os_family = Column(String, nullable=True)
    os_version = Column(String, nullable=True)

    browser_family = Column(String, nullable=True)
    browser_version = Column(String, nullable=True)

    ip = Column(String)
    country = Column(String)
    city = Column(String)


class UserSession(StatusMixin, Base):
    __tablename__ = "users_sessions"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True
    )
    device_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions_devices.uuid"),
        primary_key=True,
    )
    code = Column(String(length=4))
    session_type = Column(Enum(SessionTypeEnum), nullable=False)
    status_id = Column(Integer, ForeignKey(column=Statuses.id), default=3)

    device = relationship("SessionDevice")


class MessageDocument(Base):
    __tablename__ = "messages_documents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)

    message_id = Column(
        UUID(as_uuid=True), ForeignKey("messages.uuid"), primary_key=True
    )
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("documents.uuid"), primary_key=True
    )

    message = relationship("Message")
    document = relationship("Document")


class Message(TimestampMixin, Base):
    __tablename__ = "messages"
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.uuid"), primary_key=True
    )
    author_id = Column(
        UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True
    )
    text = Column(String(length=2048))

    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("messages.uuid", ondelete="CASCADE"),
        # primary_key=True,
        nullable=True,
    )

    documents = relationship("Document", secondary="messages_documents", uselist=True)

    parent = relationship("Message", remote_side=[uuid])
    author = relationship("User")

    thread_count = query_expression()
