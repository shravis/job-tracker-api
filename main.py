import logging
import os

from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi import status as http_status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

import auth
import models
import schemas

from database import get_db
from security import get_current_user

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger("jobtracker")

app = FastAPI(
    title="Job Tracker API",
    description="A secure REST API for tracking job applications using FastAPI, PostgreSQL, SQLAlchemy, and JWT Authentication.",
    version="1.0.0"
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


def _commit_or_500(db: Session, action: str):
    try:
        db.commit()
    except SQLAlchemyError:
        logger.exception("Database error during %s", action)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to {action}."
        )


@app.get("/")
def home():
    return {"message": "Welcome to Job Tracker API"}


@app.get("/about")
def about():
    return {
        "name": "Job Tracker API",
        "version": app.version,
        "author": "Shravya"
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception:
        logger.exception("Health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable"
        )


@app.get("/jobs", response_model=list[schemas.JobResponse])
def get_jobs(
    company: str | None = None,
    status: str | None = None,
    sort: str | None = None,
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

    valid_sort_fields = {
        "id": models.Job.id,
        "company": models.Job.company,
        "position": models.Job.position,
        "status": models.Job.status
    }

    if sort:
        if sort not in valid_sort_fields:
            raise HTTPException(
                status_code=400,
                detail="Invalid sort field"
            )
        query = query.order_by(valid_sort_fields[sort])
    else:
        query = query.order_by(models.Job.id)

    return query.offset(skip).limit(limit).all()


@app.get(
    "/jobs/{job_id}",
    response_model=schemas.JobResponse
)
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


@app.post(
    "/jobs",
    response_model=schemas.JobResponse,
    status_code=http_status.HTTP_201_CREATED
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
    _commit_or_500(db, "create job")
    db.refresh(new_job)
    return new_job


@app.put(
    "/jobs/{job_id}",
    response_model=schemas.JobResponse
)
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

    _commit_or_500(db, "update job")
    db.refresh(job)
    return job


@app.patch(
    "/jobs/{job_id}",
    response_model=schemas.JobResponse
)
def patch_job(
    job_id: int,
    updated_job: schemas.JobUpdate,
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

    update_data = updated_job.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )

    for key, value in update_data.items():
        setattr(job, key, value)

    _commit_or_500(db, "update job")
    db.refresh(job)
    return job


@app.delete(
    "/jobs/{job_id}",
    status_code=http_status.HTTP_204_NO_CONTENT
)
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
    _commit_or_500(db, "delete job")

    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
