from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

import auth
import models
import schemas

from database import SessionLocal
from security import get_current_user

app = FastAPI(
    title="Job Tracker API",
    description="A secure REST API for tracking job applications using FastAPI, PostgreSQL, SQLAlchemy, and JWT Authentication.",
    version="1.0.0"
)

app.include_router(auth.router)


# Create a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Home endpoint
@app.get("/")
def home():
    return {"message": "Welcome to Job Tracker API"}


# About endpoint
@app.get("/about")
def about():
    return {"developer": "Shravya"}


# Get all jobs
@app.get("/jobs", response_model=list[schemas.JobResponse])
def get_jobs(
    company: str = None,
    status: str = None,
    sort: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(models.Job)

    if company:
        query = query.filter(models.Job.company == company)

    if status:
        query = query.filter(models.Job.status == status)

    if sort == "company":
        query = query.order_by(models.Job.company)

    elif sort == "status":
        query = query.order_by(models.Job.status)

    elif sort == "id":
        query = query.order_by(models.Job.id)

    query = query.offset(skip).limit(limit)

    return query.all()


# Get a single job
@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


# Create a new job
@app.post("/jobs", status_code=status.HTTP_201_CREATED)
def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    new_job = models.Job(
        company=job.company,
        position=job.position,
        status=job.status
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# Update a job
@app.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    updated_job: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job.company = updated_job.company
    job.position = updated_job.position
    job.status = updated_job.status

    db.commit()
    db.refresh(job)

    return job


# Delete a job
@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}