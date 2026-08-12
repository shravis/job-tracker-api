from pydantic import BaseModel


class JobCreate(BaseModel):
    company: str
    position: str
    status: str


class JobResponse(JobCreate):
    id: int

    class Config:
        from_attributes = True