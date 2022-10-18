from app.swagger.html import get_swagger_ui_html

swagger_js_url_static = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.51.0/swagger-ui-bundle.js"
)
swagger_css_url_static = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css"
swagger_custom_theme_url = (
    "https://cdn.jsdelivr.net/npm/swagger-ui-themes@3.0.1/themes/3.x/theme-material.css"
)


def custom_swagger_ui_html(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url=swagger_js_url_static,
        swagger_css_url=swagger_css_url_static,
        swagger_custom_theme_url=swagger_custom_theme_url,
        hide_default_schemas=True
    )
