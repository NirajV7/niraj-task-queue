# In app/services/job_service.py

from sqlalchemy.orm import Session
from typing import Optional, List
from .. import models, schemas
import uuid
from fastapi import HTTPException

def create_job(db: Session, job_in: schemas.JobCreate) -> models.Job:
    """Creates a new job in the database, handling idempotency."""

    # --- NEW IDEMPOTENCY CHECK ---
    if job_in.idempotency_key:
        existing_job = db.query(models.Job).filter(
            models.Job.idempotency_key == job_in.idempotency_key
        ).first()
        if existing_job:
            print(f"SERVICE: Idempotency key '{job_in.idempotency_key}' already used. Returning existing job {existing_job.job_id}.")
            return existing_job
    # -----------------------------

    job_data = job_in.model_dump()
    depends_on_ids = job_data.pop("depends_on", None)

    db_job = models.Job(
        job_id=f"job_{uuid.uuid4().hex[:12]}",
        **job_data
    )

    if depends_on_ids:
        dependencies = db.query(models.Job).filter(models.Job.job_id.in_(depends_on_ids)).all()
        if len(dependencies) != len(depends_on_ids):
            raise HTTPException(status_code=400, detail="One or more dependencies not found")
        db_job.dependencies.extend(dependencies)

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: str) -> Optional[models.Job]:
    return db.query(models.Job).filter(models.Job.job_id == job_id).first()

def get_candidate_jobs(db: Session, limit: int = 10) -> List[models.Job]:
    return db.query(models.Job).filter(
        models.Job.status == models.JobStatus.PENDING
    ).order_by(
        models.Job.priority.desc(), models.Job.created_at.asc()
    ).limit(limit).all()

def are_dependencies_met(job: models.Job) -> bool:
    """Check if all dependencies for a job are met."""
    for dep in job.dependencies:
        if dep.status != models.JobStatus.SUCCESS:
            print(f"WORKER: Job {job.job_id} is waiting for dependency {dep.job_id} (status: {dep.status.value})")
            return False
    return True