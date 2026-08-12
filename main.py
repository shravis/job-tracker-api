from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

import schemas
import models

from database import SessionLocal

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Welcome to Job Tracker API"}

@app.get("/about")
def about():
    return {"developer": "Shravya"}

@app.get("/jobs")
def get_jobs(
    company: str = None,
    status: str = None,
    sort: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
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

    jobs = query.all()

    return jobs
    
@app.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if job is None:
        return {"error": "Job not found"}

    return job
   

    return {"error": "Job not found"}

@app.post("/jobs")
def create_job(
    job: schemas.JobCreate,
    db: Session = Depends(get_db)
):
    new_job = models.Job(
        company=job.company,
        position=job.position,
        status=job.status
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return {
        "message": "Job added successfully!",
        "job": new_job
    }

@app.put("/jobs/{job_id}")
def update_job(
    job_id: int,
    updated_job: schemas.JobCreate,
    db: Session = Depends(get_db)
):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if job is None:
        return {"error": "Job not found"}

    job.company = updated_job.company
    job.position = updated_job.position
    job.status = updated_job.status

    db.commit()
    db.refresh(job)

    return {
        "message": "Job updated successfully!",
        "job": job
    }

@app.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    if job is None:
        return {"error": "Job not found"}

    db.delete(job)
    db.commit()

    return {
        "message": "Job deleted successfully!"
    }