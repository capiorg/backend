from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.base import BaseTimeStampMixin
from app.v1.users.schemas import GetUserModel


class MessageTypeEnum(str, Enum):
    MESSAGE = "message"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"


class MessageGetModel(BaseTimeStampMixin):
    uuid: UUID
    author_id: UUID
    conversation_id: UUID
    text: str
    thread_count: int = 0
    author: GetUserModel


class MessageSendModel(BaseModelORM):
    reply_uuid: Optional[UUID] = None
    text: str


class MessageSendResultModel(BaseModelORM):
    uuid: UUID
    conversation_id: UUID
    author_id: UUID
