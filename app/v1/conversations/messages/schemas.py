from __future__ import annotations

from enum import Enum
from typing import Any
from typing import Any
from typing import Dict
from typing import Optional
from typing import Self
from typing import Type
from uuid import UUID

from pydantic import Field
from pydantic import root_validator
from pydantic import validator

from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.base import BaseTimeStampMixin
from app.v1.users.schemas import GetMeUserModel
from app.v1.users.schemas import GetUserModel
from config import settings_app


class MessageTypeEnum(str, Enum):
    MESSAGE = "message"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    VOICE = "voice"


class FileModelDTO(BaseModelORM):
    uuid: UUID
    document_id: UUID

    url: Optional[str] = None
    meta: Optional[str] = None

    @root_validator
    def validate_urls(cls: Type[Self], values: dict[str, Any]) -> dict[str, Any]:
        uuid = values.get("document_id")

        values["url"] = f"{settings_app.FILES_API_DOMAIN}/v1/documents/{uuid}/file"
        values["meta"] = f"{settings_app.FILES_API_DOMAIN}/v1/documents/{uuid}/stats"

        return values


class MessageGetModel(BaseTimeStampMixin):
    uuid: UUID
    author_id: UUID
    conversation_id: UUID
    parent_id: Optional[UUID] = Field(None, alias="reply_uuid")
    text: str
    thread_count: int = 0
    author: GetMeUserModel

    documents: list[FileModelDTO] = Field([])


class MessageSendModel(BaseModelORM):
    reply_uuid: Optional[UUID] = None
    text: str
    documents: list[UUID] = Field([])


class MessageSendResultModel(BaseModelORM):
    uuid: UUID
    conversation_id: UUID
    author_id: UUID


class MessageDeleteModel(BaseModelORM):
    uuid: UUID


class MessageDeleteSocketModel(BaseModelORM):
    uuid: UUID
    conversation_id: UUID
    reply_uuid: Optional[UUID] = None
    author: GetUserModel


class UpdateMessageModel(BaseModelORM):
    text: str


class QueryMessageModel(BaseModelORM):
    limit: int = Field(20)
    offset: int = Field("0")
