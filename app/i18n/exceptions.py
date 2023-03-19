from typing import Optional

from fastapi.exceptions import RequestValidationError
from pydantic import Field
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.i18n.tr import translate_pydantic
from app.v1.schemas.responses import BaseError
from app.v1.schemas.responses import BaseExceptionError
from app.v1.schemas.responses import BaseResponse
from app.v1.schemas.responses import DetailError
from config import settings_app


class CustomBaseErrorValidation(BaseError):
    code: str = Field(..., example="422")
    message: Optional[str] = Field(
        None, example="Поле: chat_id Ошибка: обязательное поле"
    )


class CustomValidationError(BaseResponse):
    status: bool = False
    code: int = 422
    error: CustomBaseErrorValidation


async def validation_exception_handler(
    request: Request, exc: ValidationError | RequestValidationError
):
    current_locale = request.query_params.get(
        "locale", settings_app.DEFAULT_LOCALE
    )
    ignore_keys = ["body"]

    errors = translate_pydantic.translate(exc.errors(), current_locale)

    errors_obj = []
    for error in errors:
        codes = error.get("loc")

        codes_and_messages = [
            f"{code}" for code in codes if code not in ignore_keys
        ]

        errors_obj.append(
            DetailError(
                loc=error.get("loc"),
                code=", ".join(codes_and_messages),
                msg=error.get("msg"),
                type=error.get("type"),
            )
        )

    return JSONResponse(
        status_code=422,
        content=BaseResponse(
            status=False,
            code=422,
            error=BaseError(
                code="422",
                message="Отправленные поля содержат ошибки",
                exception=BaseExceptionError(
                    exception=str(type(exc)),
                    details=errors_obj,
                    message="Validation Error",
                ),
            ),
        ).dict(),
    )
