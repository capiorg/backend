from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BaseModelORM(BaseModel):
    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class BaseTimeStampMixin(BaseModelORM):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
