# In app/routes/jobs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..services import job_service # Import the new service
from ..database import get_db

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