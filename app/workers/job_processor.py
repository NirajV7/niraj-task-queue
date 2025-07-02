# In app/workers/job_processor.py

import asyncio
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.services import job_service
from app.services.resource_manager import resource_manager # <-- IMPORT THE NEW MANAGER
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
        candidate_jobs = job_service.get_candidate_jobs(db)

        for job in candidate_jobs:
            if not are_dependencies_met(job):
                continue # Skip to the next job

            # --- NEW RESOURCE CHECK ---
            cpu_req = job.resource_requirements.get("cpu_units", 0)
            mem_req = job.resource_requirements.get("memory_mb", 0)

            if resource_manager.allocate(cpu_req, mem_req):
                job_to_run = job
                break # We found a job that fits, so we'll run it
            else:
                print(f"WORKER: Not enough resources for job {job.job_id}. Skipping.")
        
        if job_to_run:
            cpu_req = job_to_run.resource_requirements.get("cpu_units", 0)
            mem_req = job_to_run.resource_requirements.get("memory_mb", 0)
            
            try:
                print(f"WORKER: Found job {job_to_run.job_id} to run. Changing status to RUNNING.")
                job_to_run.status = models.JobStatus.RUNNING
                job_to_run.started_at = datetime.datetime.utcnow()
                db.commit()

                print(f"WORKER: Executing job {job_to_run.job_id}...")
                await asyncio.sleep(15) # Simulate a longer task

                job_to_run.status = models.JobStatus.SUCCESS
                job_to_run.completed_at = datetime.datetime.utcnow()
                db.commit()
                print(f"WORKER: Job {job_to_run.job_id} completed successfully.")
            finally:
                # CRITICAL: Always release resources, even if the job fails.
                resource_manager.release(cpu_req, mem_req)
        else:
            print("WORKER: No jobs are ready to run or fit available resources.")
            
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