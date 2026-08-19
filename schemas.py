from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class JobStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    WITHDRAWN = "Withdrawn"


class JobCreate(BaseModel):
    company: str
    position: str
    status: JobStatus


class JobUpdate(BaseModel):
    company: str | None = None
    position: str | None = None
    status: JobStatus | None = None


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


class Token(BaseModel):
    access_token: str
    token_type: str