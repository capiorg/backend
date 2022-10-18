import os

from fastapi import Header
from pydantic_i18n import BabelLoader
from pydantic_i18n import PydanticI18n

from config import settings_app


def get_loader() -> BabelLoader:
    current_path = os.path.dirname(os.path.realpath(__file__))
    return BabelLoader(f"{current_path}/translations")


translate_pydantic = PydanticI18n(source=get_loader())


def get_locale(
    locale: str = Header(
        default=settings_app.DEFAULT_LOCALE,
        description="Язык пользователя в заголовках запроса",
    )
) -> str:
    return locale
