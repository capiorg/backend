import json
from typing import Literal
from typing import Optional, Dict, Any

from fastapi.encoders import jsonable_encoder
from starlette.responses import HTMLResponse


def get_swagger_ui_html(
    *,
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css",
    swagger_custom_theme_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-themes@3.0.1/"
    "themes/3.x/theme-newspaper.css",
    swagger_favicon_url: str = "https://fastapi.tiangolo.com/img/favicon.png",
    oauth2_redirect_url: Optional[str] = None,
    init_oauth: Optional[Dict[str, Any]] = None,
    hide_default_schemas: Optional[bool] = False,
    display_request_duration: Optional[bool] = True,
    syntax_highlight: Optional[bool] = True,
    enable_filter: Optional[bool] = True,
    show_common_extensions: Optional[bool] = True,
    persist_authorization: Optional[bool] = True,
    doc_expansion: Literal["full", "none", "list"] = "list",
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
    <link rel="shortcut icon" href="{swagger_favicon_url}">
    <link rel="stylesheet" href="{swagger_custom_theme_url}"/>
    <title>{title}</title>
    </head>
    <body>
    <div id="swagger-ui">
    </div>
    <script src="{swagger_js_url}"></script>
    <!-- `SwaggerUIBundle` is now available on the page -->
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',

    """

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    if display_request_duration:
        html += '"displayRequestDuration": true,'

    if syntax_highlight:
        html += "syntaxHighlight: true,"

    if hide_default_schemas:
        html += "defaultModelsExpandDepth: -1,"

    if enable_filter:
        html += "filter: true,"

    if show_common_extensions:
        html += "showCommonExtensions: true,"

    if persist_authorization:
        html += "persistAuthorization: true,"

    html += f"docExpansion: '{doc_expansion}',"

    html += """
        dom_id: '#swagger-ui',
        presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        deepLinking: true,
        showExtensions: true,
    })"""

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(jsonable_encoder(init_oauth))})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
