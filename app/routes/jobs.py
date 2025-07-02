# In app/routes/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..services import job_service # Import the new service
from ..database import get_db
from typing import List, Optional

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=schemas.JobResponse, status_code=201)
def submit_job(job_in: schemas.JobCreate, db: Session = Depends(get_db)):
    """Submit a new job to the queue."""
    return job_service.create_job(db=db, job_in=job_in)

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    """Get the status and details of a specific job."""
    db_job = job_service.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.get("/", response_model=List[schemas.JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    status: Optional[models.JobStatus] = None,
    job_type: Optional[str] = None,
    limit: int = 100
):
    """
    List jobs with optional filtering by status and/or job type.
    """
    query = db.query(models.Job)

    if status:
        query = query.filter(models.Job.status == status)

    if job_type:
        query = query.filter(models.Job.type == job_type)

    return query.order_by(models.Job.created_at.desc()).limit(limit).all()

@router.patch("/{job_id}/cancel", response_model=schemas.JobResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """
    Cancel a job if it is in a pending state.
    """
    db_job = job_service.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # You can only cancel a pending job
    if db_job.status != models.JobStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{db_job.status.value}'. Only pending jobs can be canceled."
        )

    db_job.status = models.JobStatus.CANCELLED
    db.commit()
    db.refresh(db_job)

    return db_job