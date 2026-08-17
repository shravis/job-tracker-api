from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import auth
import models
import schemas

from database import get_db
from security import get_current_user

app = FastAPI(
    title="Job Tracker API",
    description="A secure REST API for tracking job applications using FastAPI, PostgreSQL, SQLAlchemy, and JWT Authentication.",
    version="1.0.0"
)

app.include_router(auth.router)


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
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    query = db.query(models.Job).filter(
        models.Job.user_id == current_user.id
    )

    if company:
        query = query.filter(
            models.Job.company.ilike(f"%{company}%")
        )

    if status:
        query = query.filter(
            models.Job.status.ilike(f"%{status}%")
        )

    if sort == "company":
        query = query.order_by(models.Job.company)

    elif sort == "status":
        query = query.order_by(models.Job.status)

    elif sort == "id":
        query = query.order_by(models.Job.id)

    else:
        # Default ordering for stable pagination
        query = query.order_by(models.Job.id)

    query = query.offset(skip).limit(limit)

    return query.all()


# Get a single job
@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.user_id == current_user.id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


# Create a new job
@app.post(
    "/jobs",
    response_model=schemas.JobResponse,
    status_code=status.HTTP_201_CREATED
)
def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_job = models.Job(
        company=job.company,
        position=job.position,
        status=job.status,
        user_id=current_user.id
    )

    db.add(new_job)

    try:
        db.commit()
        db.refresh(new_job)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create job."
        )

    return new_job


# Update a job
@app.put("/jobs/{job_id}", response_model=schemas.JobResponse)
def update_job(
    job_id: int,
    updated_job: schemas.JobCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.user_id == current_user.id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job.company = updated_job.company
    job.position = updated_job.position
    job.status = updated_job.status

    try:
        db.commit()
        db.refresh(job)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to update job."
        )

    return job


# Delete a job
@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    job = db.query(models.Job).filter(
        models.Job.id == job_id,
        models.Job.user_id == current_user.id
    ).first()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)

    try:
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete job."
        )

    return {"message": "Job deleted successfully"}