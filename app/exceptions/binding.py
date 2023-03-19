from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.exceptions.db.handlers import sql_exception_handler
from app.exceptions.db.models import ExceptionSQL

from app.exceptions.routes.handlers import incorrect_auth_code_handler
from app.exceptions.routes.models import IncorrectAuthCodeError
from app.exceptions.routes.models import RepeatedAuthCodeError
from app.i18n.exceptions import validation_exception_handler


def setup_exception_handlers(app: FastAPI) -> FastAPI:
    app.add_exception_handler(ExceptionSQL, sql_exception_handler)
    app.add_exception_handler(
        IncorrectAuthCodeError, incorrect_auth_code_handler
    )
    app.add_exception_handler(
        RepeatedAuthCodeError, incorrect_auth_code_handler
    )
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(
        RequestValidationError, validation_exception_handler
    )

    return app
