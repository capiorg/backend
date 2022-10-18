from sqlalchemy import Numeric
from sqlalchemy.ext.associationproxy import association_proxy
from uuid_extensions import uuid7

from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from sqlalchemy.orm import relationship

from app.db.mixins import TimestampMixin
from misc import Base


class Statuses(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)


class StatusMixin(Base):
    __abstract__ = True

    @declared_attr
    def status_id(cls):
        return Column(Integer, ForeignKey(column=Statuses.id), default=1, nullable=True)

    @declared_attr
    def status(cls):
        return relationship(argument="Statuses", viewonly=True, lazy="joined")


class Document(
    StatusMixin,
    TimestampMixin,
    Base,
):
    __tablename__ = "documents"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    original_filename = Column(String(255))
    security_name = Column(String(255), nullable=True)
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

    conversations = relationship("Conversation", secondary="users_conversations")


class ChatType(Base):
    __tablename__ = "chats_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class Chat(TimestampMixin, StatusMixin, Base):
    __tablename__ = "chats"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    # type_id = Column(Integer, ForeignKey(ChatType.id))
    title = Column(String, nullable=True, comment="Если type group - название чата")
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.uuid"), nullable=True)

    # chat_type = relationship("ChatType", viewonly=True, lazy="joined")
    document = relationship("Document", viewonly=True, lazy="joined")

    # type = association_proxy(target_collection="chat_type", attr="name")


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    type_id = Column(Integer, ForeignKey("chats_types.id"))
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.uuid"))
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))

    chat_type = relationship("ChatType", viewonly=True, lazy="joined")
    chat = relationship("Chat", viewonly=True, lazy="joined")
    recipient = relationship("User", viewonly=True, lazy="joined")

    type = association_proxy(target_collection="chat_type", attr="name")


class ConversationUser(TimestampMixin, Base):
    __tablename__ = "users_conversations"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.uuid"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), primary_key=True)

    conversation = relationship("Conversation")
    user = relationship("User")

