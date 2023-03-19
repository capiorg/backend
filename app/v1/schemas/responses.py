from typing import Generic
from typing import List
from typing import Optional
from typing import TypeVar

from pydantic.generics import GenericModel

from app.v1.schemas.base import BaseModelORM

ChildT = TypeVar("ChildT")
ChildErrorsT = TypeVar("ChildErrorsT")


class DetailError(BaseModelORM):
    loc: tuple[str, ...]
    code: str
    msg: str
    type: str


class BaseExceptionError(GenericModel, BaseModelORM, Generic[ChildErrorsT]):
    exception: str
    details: Optional[ChildErrorsT] = None
    message: Optional[str] = None


class BaseError(BaseModelORM):
    code: str
    message: str
    exception: Optional[BaseExceptionError[List[DetailError]]]


class BaseResponse(GenericModel, BaseModelORM, Generic[ChildT]):
    status: bool = True
    code: int = 200
    error: Optional[BaseError]
    result: Optional[ChildT] = None
