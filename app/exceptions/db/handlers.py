from starlette.requests import Request
from starlette.responses import JSONResponse

from app.exceptions.db.models import ExceptionSQL
from app.v1.schemas.responses import BaseError
from app.v1.schemas.responses import BaseExceptionError
from app.v1.schemas.responses import BaseResponse


def sql_exception_handler(_: Request, exc: ExceptionSQL):
    return JSONResponse(
        status_code=exc.code,
        content=BaseResponse(
            status=False,
            code=exc.code,
            error=BaseError(
                code=str(exc.code),
                message=exc.detail,
                exception=BaseExceptionError(
                    exception=str(type(exc.original_exception)),
                    detail=exc.original_detail(),
                    message=exc.original_message(),
                ),
            ),
        ).dict(),
    )
