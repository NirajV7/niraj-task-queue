# In app/workers/job_processor.py

import asyncio
import datetime
import traceback
import sys
import os

# This is still needed to ensure the 'app' module is on the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services import job_service
from app.services.resource_manager import resource_manager
from app import models

# --- NEW: Function to handle job failures and retries ---
def handle_job_failure(job: models.Job, db: Session, error: Exception):
    """Handles the logic for when a job fails, including retries."""
    
    # --- ADD LOGGING ---
    error_message = f"Job failed with error: {error}"
    db.add(models.JobLog(job_id=job.id, message=error_message))
    
    job.last_error = str(error)
    job.current_attempt += 1
    
    max_attempts = job.retry_config.get("max_attempts", 1) if job.retry_config else 1

    if job.current_attempt < max_attempts:
        backoff_multiplier = job.retry_config.get("backoff_multiplier", 2) if job.retry_config else 2
        # Calculate delay in seconds. e.g., 5s, 10s, 20s
        delay_seconds = 5 * (backoff_multiplier ** (job.current_attempt))
        
        job.run_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay_seconds)
        job.status = models.JobStatus.PENDING # Set back to pending for the next attempt
        print(f"WORKER: Job {job.job_id} failed on attempt {job.current_attempt}. Rescheduling to run in {delay_seconds} seconds.")
    else:
        # Max attempts reached, fail permanently
        job.status = models.JobStatus.FAILED
        job.completed_at = datetime.datetime.utcnow()
        print(f"WORKER: Job {job.job_id} has failed permanently after {max_attempts} attempts.")
    
    db.commit()


async def execute_job(job: models.Job, db: Session):
    """Simulates the actual execution of a job."""

    # --- ADD LOGGING ---
    log_message = f"Executing job {job.job_id} (Type: {job.type})..."
    print(log_message)
    db.add(models.JobLog(job_id=job.id, message=log_message))
    db.commit()

    # Simulate different job behaviors based on payload for testing
    if job.payload and job.payload.get("should_fail"):
        raise ValueError("This job was configured to fail deliberately!")

    duration = job.payload.get("duration_seconds", 15) if job.payload else 15
    await asyncio.sleep(duration)


async def process_jobs():
    """Finds and runs a ready job, with full error, timeout, and retry handling."""
    db = SessionLocal()
    try:
        candidate_jobs = job_service.get_candidate_jobs(db)
        if not candidate_jobs:
            print("WORKER: No pending jobs found.")
            return

        job_to_run = None
        for job in candidate_jobs:
            if not job_service.are_dependencies_met(job):
                continue

            cpu_req = job.resource_requirements.get("cpu_units", 0) if job.resource_requirements else 0
            mem_req = job.resource_requirements.get("memory_mb", 0) if job.resource_requirements else 0
            
            if resource_manager.allocate(cpu_req, mem_req):
                job_to_run = job
                break 
            else:
                print(f"WORKER: Not enough resources for job {job.job_id}. Skipping.")
        
        if not job_to_run:
            print("WORKER: No jobs are ready to run or fit available resources.")
            return

        # We found a job, now execute it with failure handling
        cpu_req = job_to_run.resource_requirements.get("cpu_units", 0) if job_to_run.resource_requirements else 0
        mem_req = job_to_run.resource_requirements.get("memory_mb", 0) if job_to_run.resource_requirements else 0
        
        try:
            print(f"WORKER: Starting job {job_to_run.job_id}. Changing status to RUNNING.")
            job_to_run.status = models.JobStatus.RUNNING
            job_to_run.started_at = datetime.datetime.utcnow()
            job_to_run.current_attempt += 1
            db.commit()

            timeout = job_to_run.timeout_seconds or 300 # Default 5-min timeout
            await asyncio.wait_for(execute_job(job_to_run, db), timeout=timeout)

            job_to_run.status = models.JobStatus.SUCCESS
            print(f"WORKER: Job {job_to_run.job_id} completed successfully.")

        except Exception as e:
            print(f"WORKER: An error occurred while running job {job_to_run.job_id}: {e}")
            traceback.print_exc()
            handle_job_failure(job_to_run, db, e)
        finally:
            job_to_run.completed_at = datetime.datetime.utcnow()
            db.commit()
            resource_manager.release(cpu_req, mem_req)

    finally:
        db.close()


async def main():
    """The main loop that runs the worker process periodically."""
    print("--- Worker Process Started ---")
    while True:
        await process_jobs()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())