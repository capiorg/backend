import logging
from logging.config import dictConfig

from fastapi import Depends
from fastapi import FastAPI
from opencensus.trace.samplers import AlwaysOnSampler
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette_exporter import PrometheusMiddleware
from starlette_exporter import handle_metrics

from app.i18n.tr import get_locale
from app.utils.logging.middlewares import LoggingMiddleware
from app.utils.logging.middlewares import OpenCensusFastAPIMiddleware
from app.v1.binding import own_router_v1
from app.v1.users.dependencies import UsersDependencyMarker
from app.v1.users.services import UserService
from config import BaseSettingsMarker
from config import HTTPAuthSettings
from config import HTTPAuthSettingsMarker
from config import Settings
from config import settings_app
from config import settings_sensus_app
from misc import async_session

dictConfig(settings_sensus_app.log_config)
logger = logging.getLogger(__name__)


def get_application_v1() -> FastAPI:
    application = FastAPI(
        debug=False,
        docs_url=None,
        openapi_url="/api/v1/openapi.json",
        title="CapiMessanger Microservice",
        version="1.2.15",
        root_path="/api/v1",
        dependencies=[Depends(get_locale)],
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    application.add_middleware(
        PrometheusMiddleware,
        app_name="v1",
        skip_paths=["/api/v1/docs", "/api/v1/__metrics"],
    )

    if settings_app.LOGGING:
        application.middleware("http")(LoggingMiddleware())
        if settings_sensus_app.ENABLE_TELEMETRY:
            application.middleware("http")(
                OpenCensusFastAPIMiddleware(application, sampler=AlwaysOnSampler())
            )

    application.dependency_overrides.update(
        {
            UsersDependencyMarker: lambda: UserService(db_session=async_session),
            HTTPAuthSettingsMarker: lambda: HTTPAuthSettings(),
            BaseSettingsMarker: lambda: Settings(),
        }
    )
    application.include_router(own_router_v1)
    # application = setup_exception_handlers(app=application)
    return application


def get_parent_app() -> FastAPI:
    tags_metadata = [
        {
            "name": "v1",
            "description": "Версия API - v1. Нажмите справа для перехода в документацию",
            "externalDocs": {
                "description": "дополнительная документация",
                "url": f"https://{settings_app.BASE_DOMAIN}/api/v1/docs",
            },
        },
    ]

    application = FastAPI(
        openapi_tags=tags_metadata,
    )

    application.mount("/api/v1", get_application_v1())
    application.add_route("/__metrics", handle_metrics)

    return application


app = get_parent_app()
