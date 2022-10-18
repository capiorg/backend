from typing import Generic
from typing import Optional
from typing import TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

ChildT = TypeVar("ChildT")


class BaseError(BaseModel):
    code: str
    message: str


class BaseResponse(GenericModel, BaseModel, Generic[ChildT]):
    status: bool
    code: int
    error: Optional[BaseError]
    result: ChildT
