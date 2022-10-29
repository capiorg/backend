import logging
from typing import Any
from typing import Callable
from typing import ParamSpec
from typing import TypeVar
from typing import cast

from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import NoResultFound

from app.exceptions.db.exceptions import handle_db_api_error
from app.exceptions.db.exceptions import handle_foreign_key_error
from app.exceptions.db.exceptions import handle_not_found_error
from app.exceptions.db.exceptions import handle_unique_error

logger = logging.getLogger(__name__)


P = ParamSpec("P")
T = TypeVar("T")
FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def orm_error_handler(fn: FuncT) -> FuncT:
    async def decorator(*args: P.args, **kwargs: P.kwargs) -> T:

        try:
            return await fn(*args, **kwargs)

        except IntegrityError as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)
            sql_detail = str(exc.orig.obj.detail)
            handle_unique_error(exc=exc, sql_detail=sql_detail)
            handle_foreign_key_error(exc=exc)

        except NoResultFound as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)
            handle_not_found_error(exc=exc)

        except DBAPIError as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)

            sql_detail = str(exc.orig.obj.detail)
            handle_db_api_error(exc=exc, sql_detail=sql_detail)

        except Exception as exc:
            logger.warning(msg="error orm_error_handler", exc_info=exc)

    return cast(FuncT, decorator)
