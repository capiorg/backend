from typing import Optional

from sqlalchemy.exc import DatabaseError


class ExceptionSQL(Exception):
    def __init__(
        self,
        detail: str,
        code: int,
        sql_detail: Optional[str] = None,
        exc: Optional[DatabaseError] = None,
    ):
        self.code = code
        self.detail = detail
        self.sql_detail = sql_detail
        self._exc = exc

    @property
    def original_exception(self):
        if isinstance(self._exc, ExceptionSQL):
            return self._exc
        if hasattr(self._exc, "orig"):
            return self._exc.orig.__cause__
        return self._exc

    def original_message(self):
        return getattr(self.original_exception, "message", None) or str(self.original_exception)

    def original_detail(self):
        return getattr(self.original_exception, "detail", None) or str(self.original_exception)
