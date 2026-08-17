from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    company: str
    position: str
    status: str


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