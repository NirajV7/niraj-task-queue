from sqlalchemy.orm import Session
from .. import models, schemas
import uuid
from typing import Optional, List # <-- IMPORT OPTIONAL
from fastapi import HTTPException
def create_job(db: Session, job_in: schemas.JobCreate) -> models.Job:
    """Creates a new job in the database."""

    # Separate the dependency information from the rest of the data
    job_data = job_in.model_dump()
    depends_on_ids = job_data.pop("depends_on", None)

    # Create the Job object without the 'depends_on' keyword
    db_job = models.Job(
        job_id=f"job_{uuid.uuid4().hex[:12]}",
        **job_data
    )

    # Now, handle the dependencies if they exist
    if depends_on_ids:
        # Find the actual Job objects for the dependency IDs
        dependencies = db.query(models.Job).filter(
            models.Job.job_id.in_(depends_on_ids)
        ).all()

        # Check if all specified dependencies were found
        if len(dependencies) != len(depends_on_ids):
            raise HTTPException(status_code=400, detail="One or more dependencies not found")

        # Add the found dependencies to the job's dependency list
        db_job.dependencies.extend(dependencies)

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: str) -> Optional[models.Job]: # <-- USE OPTIONAL HERE
    """Retrieves a single job by its ID."""
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()

def get_candidate_jobs(db: Session, limit: int = 10) -> List[models.Job]:
    """
    Finds a list of the highest priority, pending jobs that are ready to run.
    """
    return db.query(models.Job).filter(
        models.Job.status == models.JobStatus.PENDING
    ).order_by(
        models.Job.priority.desc(),
        models.Job.created_at.asc()
    ).limit(limit).all()