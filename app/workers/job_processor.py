# In app/workers/job_processor.py

import asyncio
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.services import job_service
from app import models

def are_dependencies_met(job: models.Job) -> bool:
    """Check if all dependencies for a job are met."""
    for dep in job.dependencies:
        if dep.status != models.JobStatus.SUCCESS:
            print(f"WORKER: Job {job.job_id} is waiting for dependency {dep.job_id} (status: {dep.status.value})")
            return False
    return True

async def process_jobs():
    """The main worker function that finds and runs a ready job."""
    print("WORKER: Checking for pending jobs...")
    db = SessionLocal()
    job_to_run = None
    try:
        # 1. Fetch a list of candidate jobs
        candidate_jobs = job_service.get_candidate_jobs(db)

        # 2. Find the first job whose dependencies are met
        for job in candidate_jobs:
            if are_dependencies_met(job):
                job_to_run = job
                break # Exit the loop once we find a runnable job
        
        # 3. If a runnable job was found, execute it
        if job_to_run:
            print(f"WORKER: Found job {job_to_run.job_id} to run. Changing status to RUNNING.")
            
            job_to_run.status = models.JobStatus.RUNNING
            job_to_run.started_at = datetime.datetime.utcnow()
            db.commit()
            db.refresh(job_to_run)

            # Simulate work
            print(f"WORKER: Executing job {job_to_run.job_id}...")
            await asyncio.sleep(10)

            # Mark as successful
            job_to_run.status = models.JobStatus.SUCCESS
            job_to_run.completed_at = datetime.datetime.utcnow()
            db.commit()
            
            print(f"WORKER: Job {job_to_run.job_id} completed successfully.")
        else:
            print("WORKER: No jobs are ready to run.")
            
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