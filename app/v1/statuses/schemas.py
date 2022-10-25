from typing import Optional

from app.v1.schemas.base import BaseModelORM


class Statuses(BaseModelORM):
    id: int
    title: str


class StatusGetMixinV3(BaseModelORM):
    status: Optional[Statuses] = None
