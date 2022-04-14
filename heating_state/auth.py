import secrets
from fastapi import HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import BASIC_AUTH_USERS


def validate_credentials(credentials: HTTPBasicCredentials):
    """Validate given auth credentials."""
    password = BASIC_AUTH_USERS.get(credentials.username)

    if password is None:
        correct_password = False
    else:
        correct_password = secrets.compare_digest(credentials.password, password)

    if not correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Basic"},
        )
