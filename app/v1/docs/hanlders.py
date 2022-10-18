from fastapi import APIRouter
from fastapi import Depends
from fastapi.openapi.utils import get_openapi

from starlette.requests import Request

from app.swagger.render import custom_swagger_ui_html
from app.v1.security.http_base import get_username_http_auth
from config import BaseSettingsMarker
from config import Settings

docs_router = APIRouter()


@docs_router.get("/docs", include_in_schema=False)
async def docs_handler(request: Request, _: str = Depends(get_username_http_auth)):
    root_path = f'{request.scope.get("root_path", "")}/openapi.json'
    return custom_swagger_ui_html(openapi_url=root_path, title="Документация v2")


@docs_router.get("/openapi.json", include_in_schema=False)
async def docs_handler(
    request: Request,
    _: str = Depends(get_username_http_auth),
    settings_base: Settings = Depends(BaseSettingsMarker),
):
    return get_openapi(
        title="CapiMessanger Microservice",
        version=settings_base.APP_VERSION,
        routes=request.app.routes,
        servers=[{"url": "/api/v2"}],
    )
