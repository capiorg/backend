import secrets

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPBasic
from fastapi.security import HTTPBasicCredentials
from starlette import status

from config import HTTPAuthSettings
from config import HTTPAuthSettingsMarker

SECURITY_HTTP_AUTH = HTTPBasic()


def get_username_http_auth(
    credentials: HTTPBasicCredentials = Depends(SECURITY_HTTP_AUTH),
    settings_auth: HTTPAuthSettings = Depends(HTTPAuthSettingsMarker),
):
    correct_username = secrets.compare_digest(
        credentials.username, settings_auth.USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings_auth.PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
