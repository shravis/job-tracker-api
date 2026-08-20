from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


class JobStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


def _strip_required(value: str) -> str:
    if isinstance(value, str):
        return value.strip()
    return value


def _strip_optional(value: str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    return value


class JobCreate(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    position: str = Field(min_length=1, max_length=200)
    status: JobStatus

    @field_validator("company", "position", mode="before")
    @classmethod
    def strip_job_text(cls, value: str) -> str:
        return _strip_required(value)


class JobUpdate(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=200)
    position: str | None = Field(default=None, min_length=1, max_length=200)
    status: JobStatus | None = None

    @field_validator("company", "position", mode="before")
    @classmethod
    def strip_optional_job_text(cls, value: str | None) -> str | None:
        return _strip_optional(value)


class JobResponse(JobCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50
    )

    password: str = Field(
        min_length=8,
        max_length=72
    )

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: str) -> str:
        return _strip_required(value)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt_bytes(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError(
                "Password cannot exceed 72 bytes when encoded as UTF-8"
            )
        return value


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    refresh_token: str
