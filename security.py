from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, UTC
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import bcrypt
import os

import models
from database import get_db

load_dotenv()

AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}


def get_env_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(
            f"Missing required environment variable: {name}"
        )

    return value


SECRET_KEY = get_env_variable("SECRET_KEY")
ALGORITHM = get_env_variable("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES")
)
REFRESH_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "10080")
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def _unauthorized(detail: str = "Invalid authentication credentials"):
    raise HTTPException(
        status_code=401,
        detail=detail,
        headers=AUTH_HEADERS
    )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(data: dict, token_version: int = 0) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp": expire,
        "type": "access",
        "ver": token_version
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, token_version: int = 0) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(
        minutes=REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "ver": token_version
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        _unauthorized()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_token(token)

    if payload.get("type") not in (None, "access"):
        _unauthorized("Invalid authentication credentials")

    username = payload.get("sub")

    if username is None:
        _unauthorized("Invalid authentication credentials")

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if user is None:
        _unauthorized("User not found")

    token_version = getattr(user, "token_version", 0) or 0
    if payload.get("ver", 0) != token_version:
        _unauthorized("Token has been revoked")

    return user
