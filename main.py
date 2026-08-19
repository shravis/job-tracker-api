from fastapi import FastAPI, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import auth
import models
import schemas

from database import get_db
from security import get_current_user
from sqlalchemy import text

app = FastAPI(
    title="Job Tracker API",
    description="A secure REST API for tracking job applications using FastAPI, PostgreSQL, SQLAlchemy, and JWT Authentication.",
    version="1.0.0"
)

app.include_router(auth.router)


@app.get("/")
def home():
    return {"message": "Welcome to Job Tracker API"}


@app.get("/about")
def about():
    return {"developer": "Shravya"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=str(e)
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

        query = query.order_by(
            valid_sort_fields[sort]
        )

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

    update_data = updated_job.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(job, key, value)

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


@app.delete(
    "/jobs/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT
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

    try:
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to delete job."
        )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )