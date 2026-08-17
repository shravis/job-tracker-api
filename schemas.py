from enum import Enum
from pydantic import BaseModel, Field


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


class JobResponse(JobCreate):
    id: int

    class Config:
        from_attributes = True


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