from fastapi import FastAPI

from app.exceptions.db.handlers import sql_exception_handler
from app.exceptions.db.models import ExceptionSQL

from app.exceptions.routes.handlers import incorrect_auth_code_handler
from app.exceptions.routes.models import IncorrectAuthCodeError
from app.exceptions.routes.models import RepeatedAuthCodeError


def setup_exception_handlers(app: FastAPI) -> FastAPI:
    app.add_exception_handler(ExceptionSQL, sql_exception_handler)
    app.add_exception_handler(IncorrectAuthCodeError, incorrect_auth_code_handler)
    app.add_exception_handler(RepeatedAuthCodeError, incorrect_auth_code_handler)

    return app
