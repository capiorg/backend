from sqlalchemy.dialects.postgresql.asyncpg import (
    AsyncAdapt_asyncpg_connection,
)
from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_dbapi


def _handle_exception(self, error):
    if self._connection.is_closed():
        self._transaction = None
        self._started = False

    if not isinstance(error, AsyncAdapt_asyncpg_dbapi.Error):
        exception_mapping = self.dbapi._asyncpg_error_translate  # noqa
        for super_ in type(error).__mro__:
            if super_ in exception_mapping:
                translated_error = exception_mapping[super_](
                    "%s: %s" % (type(error), error)
                )
                translated_error.pgcode = translated_error.sqlstate = getattr(
                    error, "sqlstate", None
                )

                translated_error.detail = getattr(error, "detail", None)
                translated_error.message = getattr(error, "message", None)
                translated_error.obj = error

                raise translated_error from error
        else:
            raise error
    else:
        raise error


AsyncAdapt_asyncpg_connection._handle_exception = _handle_exception  # noqa
