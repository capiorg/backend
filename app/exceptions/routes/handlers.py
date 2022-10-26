from starlette.requests import Request
from starlette.responses import JSONResponse

from app.exceptions.routes.models import IncorrectAuthCodeError
from app.v1.schemas.responses import BaseError
from app.v1.schemas.responses import BaseExceptionError
from app.v1.schemas.responses import BaseResponse


def incorrect_auth_code_handler(_: Request, exc: IncorrectAuthCodeError):
    return JSONResponse(
        status_code=exc.code,
        content=BaseResponse(
            status=False,
            code=exc.code,
            error=BaseError(
                code=str(exc.code),
                message=exc.detail,
                exception=BaseExceptionError(
                    exception=str(type(exc)),
                ),
            ),
        ).dict(),
    )
