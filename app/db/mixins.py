from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.sql.functions import current_timestamp

from misc import Base


class TimestampMixin(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=current_timestamp())
    updated_at = Column(DateTime, onupdate=current_timestamp())
