from typing import Optional

from asyncpg import ForeignKeyViolationError
from asyncpg import UniqueViolationError
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import DatabaseError
from sqlalchemy.exc import NoResultFound

from app.exceptions.db.models import ExceptionSQL


def handle_unique_error(exc: DatabaseError, sql_detail: Optional[str] = None):
    if exc.orig.sqlstate == UniqueViolationError.sqlstate:
        raise ExceptionSQL(
            code=400,
            detail=f"Запись уже существует в базе данных",
            sql_detail=sql_detail,
            exc=exc,
        )


def handle_foreign_key_error(exc: DatabaseError):
    if exc.orig.sqlstate == ForeignKeyViolationError.sqlstate:
        table_name = exc.orig.obj.__dict__.get("table_name")
        raise ExceptionSQL(
            code=400,
            detail=f"Произошла ошибка, с объектом связана таблица {table_name}",
            exc=exc,
        )


def handle_not_found_error(
    exc: Optional[NoResultFound] = None, __: Optional[str] = None
):
    raise ExceptionSQL(
        code=400,
        detail="Запись, которую вы ищите или удаляете, отсутствует в базе данных",
        exc=exc,
    )


def handle_db_api_error(
    exc: Optional[DBAPIError] = None, sql_detail: Optional[str] = None
):
    raise ExceptionSQL(
        code=400,
        detail="Произошла внутренняя ошибка базы данных при обработке запроса",
        sql_detail=str(exc),
        exc=exc,
    )
