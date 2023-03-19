import datetime
from enum import Enum
from typing import Any
from typing import Optional
from uuid import UUID

from pydantic import root_validator

from app.v1.schemas.base import BaseModelORM
from app.v1.schemas.base import BaseTimeStampMixin
from app.v1.statuses.schemas import StatusGetMixinV3
from app.v1.users.schemas import GetUserModel


class ChatTypeEnum(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class CompanionDTO(BaseModelORM):
    uuid: UUID


class ChatDTO(BaseModelORM):
    title: str


class CreateChatModel(BaseModelORM):
    type: ChatTypeEnum
    companion: Optional[CompanionDTO]
    chat: Optional[ChatDTO]

    @root_validator
    def validate_params(cls, values: dict[Any, Any]) -> dict[Any, Any]:
        type_ = values.get("type")
        companion = values.get("companion")
        chat = values.get("chat")

        if type_ == ChatTypeEnum.PUBLIC and not chat:
            raise ValueError("При создании публичного чата необходимо передать название чата.")

        if type_ == ChatTypeEnum.PRIVATE and not companion:
            raise ValueError("При создании приватного чата необходимо передать собеседника.")

        return values


class ChatType(BaseModelORM):
    id: int
    name: str


class ChatItemDTO(BaseTimeStampMixin, StatusGetMixinV3):
    uuid: UUID
    document_id: Optional[UUID] = None
    title: str
    status_id: int
    document: Any
    # conversation: list[Any]


class GetChatDTO(BaseTimeStampMixin):
    uuid: UUID
    type_id: int
    companion: Optional[GetUserModel] = None
    chat_id: Optional[UUID]
    chat_type: ChatType
    chat: Optional[ChatItemDTO]
