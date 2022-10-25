from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic.generics import GenericModel

from app.v1.schemas.base import BaseModelORM

ChildT = TypeVar("ChildT")


class BaseExceptionError(BaseModelORM):
    exception: str
    detail: Optional[str] = None
    message: Optional[str] = None


class BaseError(BaseModelORM):
    code: str
    message: str
    exception: Optional[BaseExceptionError]


class BaseResponse(GenericModel, BaseModelORM, Generic[ChildT]):
    status: bool = True
    code: int = 200
    error: Optional[BaseError]
    result: Optional[ChildT] = None
