from uuid import UUID

from app.v1.schemas.base import BaseModelORM


class GetAccessTokenModel(BaseModelORM):
    access_token: str
    token_type: str
    user_uuid: UUID
