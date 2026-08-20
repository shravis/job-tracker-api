from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
import schemas

from database import get_db
from rate_limiter import (
    is_rate_limited,
    record_failed_attempt,
    reset_attempts,
    MAX_REGISTER_ATTEMPTS
)
from security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    AUTH_HEADERS,
    get_current_user
)

router = APIRouter()

# Dummy bcrypt hash used to mitigate username timing attacks
DUMMY_PASSWORD_HASH = hash_password("DummyPassword123!")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    is_rate_limited(
        request,
        action="register",
        max_attempts=MAX_REGISTER_ATTEMPTS,
        detail="Too many registration attempts. Please try again in one minute."
    )
    record_failed_attempt(request, action="register")

    username = user.username.lower()

    existing_user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    new_user = models.User(
        username=username,
        password=hash_password(user.password)
    )

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    return {
        "message": "User registered successfully"
    }


@router.post("/login", response_model=schemas.Token)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    is_rate_limited(request)

    username = form_data.username.lower()

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user:
        verify_password(
            form_data.password,
            DUMMY_PASSWORD_HASH
        )
        record_failed_attempt(request)
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(form_data.password, user.password):
        record_failed_attempt(request)
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    reset_attempts(request)
    token_version = getattr(user, "token_version", 0) or 0

    return {
        "access_token": create_access_token(
            {"sub": user.username},
            token_version
        ),
        "refresh_token": create_refresh_token(
            {"sub": user.username},
            token_version
        ),
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_tokens(
    body: schemas.RefreshRequest,
    db: Session = Depends(get_db)
):
    payload = decode_token(body.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers=AUTH_HEADERS
        )

    username = payload.get("sub")
    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers=AUTH_HEADERS
        )

    token_version = getattr(user, "token_version", 0) or 0
    if payload.get("ver", 0) != token_version:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked",
            headers=AUTH_HEADERS
        )

    return {
        "access_token": create_access_token(
            {"sub": user.username},
            token_version
        ),
        "refresh_token": create_refresh_token(
            {"sub": user.username},
            token_version
        ),
        "token_type": "bearer"
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.token_version = (current_user.token_version or 0) + 1
    db.commit()
    return None
