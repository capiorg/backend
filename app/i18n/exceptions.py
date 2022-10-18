from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.i18n.tr import translate_pydantic
from config import settings_app


async def validation_exception_handler(
    request: Request, exc: ValidationError | RequestValidationError
):
    current_locale = request.query_params.get("locale", settings_app.DEFAULT_LOCALE)
    ignore_keys = ["body"]

    errors = translate_pydantic.translate(exc.errors(), current_locale)
    human_message = ""
    for error in errors:
        codes = error.get("loc")
        code_and_message = [
            f"Поле: {code}."
            for code in codes
            if code not in ignore_keys
        ]
        human_message += (
            f'{", ".join(code_and_message)}\n Ошибка: {error.get("msg")}\n\n'
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "details": errors,
                "detail": human_message,
            }
        ),
    )
