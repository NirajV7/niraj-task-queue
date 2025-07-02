import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from sqlalchemy import text
# Create a new router object
router = APIRouter(
    prefix="/jobs",  # All routes in this file will have the /jobs prefix
    tags=["Jobs"],   # Group these routes under "Jobs" in the API docs
)

# Add this new function to the file
@router.get("/__dbcheck__", tags=["Diagnostics"])
def db_check(db: Session = Depends(get_db)):
    """
    A simple health check to verify the database connection and see if the
    alembic_version table is accessible.
    """
    try:
        # Try to execute a simple query against the alembic_version table
        db.execute(text("SELECT * FROM alembic_version"))
        return {"status": "OK", "message": "Database connection is live and alembic_version table is accessible."}
    except Exception as e:
        # If it fails, we know there's a problem, and we'll see the error.
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed or alembic_version table not found: {e}"
        )


@router.post("/", response_model=schemas.JobResponse, status_code=201)
def submit_job(job_in: schemas.JobCreate, db: Session = Depends(get_db)):
    """
    Submit a new job to the queue.
    """
    # In a real system, you would have a dedicated service function for this logic.
    # For now, we'll keep it here for simplicity.
    
    db_job = models.Job(
        job_id=f"job_{uuid.uuid4().hex[:12]}",  # Create a unique, shorter job ID
        type=job_in.type,
        priority=job_in.priority,
        payload=job_in.payload,
        resource_requirements=job_in.resource_requirements,
        retry_config=job_in.retry_config,
        timeout_seconds=job_in.timeout_seconds,
        status=models.JobStatus.PENDING # Initially, all jobs are pending
    )
    
    # Here you would add logic to handle dependencies ('depends_on')
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    return db_job