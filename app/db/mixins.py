from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.sql.functions import current_timestamp

from app.db.types.date_time import TZDateTime
from misc import Base


class TimestampMixin(Base):
    __abstract__ = True
    created_at = Column(TZDateTime)
    updated_at = Column(TZDateTime, onupdate=current_timestamp())
