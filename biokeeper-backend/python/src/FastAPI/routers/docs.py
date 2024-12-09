from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi


import secrets

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from config import PASSWORD_FOR_FASTAPI_DOCS

security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "docuser")
    correct_password = secrets.compare_digest(credentials.password, PASSWORD_FOR_FASTAPI_DOCS)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username