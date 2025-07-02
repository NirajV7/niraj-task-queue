# In app/routes/jobs.py

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

# Create a new router object. This helps organize endpoints.
router = APIRouter(
    prefix="/jobs",  # All routes in this file will start with /jobs
    tags=["Jobs"],   # Group these routes under "Jobs" in the API docs
)

@router.post("/", response_model=schemas.JobResponse, status_code=201)
def submit_job(job_in: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    Submit a new job to the queue.
    """
    # Create a new Job database object from the input schema
    db_job = models.Job(
        job_id=f"job_{uuid.uuid4().hex[:12]}",
        type=job_in.type,
        priority=job_in.priority,
        payload=job_in.payload,
        resource_requirements=job_in.resource_requirements,
        retry_config=job_in.retry_config,
        timeout_seconds=job_in.timeout_seconds,
        status=models.JobStatus.PENDING # All new jobs start as pending
    )
    
    # Add the new job to the database session
    db.add(db_job)
    # Commit the transaction to save it to the database
    db.commit()
    # Refresh the object to get the newly created data from the DB
    db.refresh(db_job)
    
    return db_job

@router.get("/{job_id}", response_model=schemas.JobResponse)
def get_job_details(job_id: str, db: Session = Depends(get_db)):
    """
    Get the status and details of a specific job.
    """
    # Query the database for the first job matching the provided job_id
    db_job = db.query(models.Job).filter(models.Job.job_id == job_id).first()

    # If no job is found with that ID, return a 404 error
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return db_job