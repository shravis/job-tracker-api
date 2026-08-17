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
    reset_attempts
)
from security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()

# Dummy bcrypt hash used to mitigate username timing attacks
DUMMY_PASSWORD_HASH = hash_password("DummyPassword123!")


# Register a new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
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


# Login and generate JWT token
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
        # Always perform a bcrypt verification to reduce timing differences
        verify_password(
            form_data.password,
            DUMMY_PASSWORD_HASH
        )

        record_failed_attempt(request)

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        record_failed_attempt(request)

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    reset_attempts(request)

    access_token = create_access_token(
        data={"sub": user.username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }