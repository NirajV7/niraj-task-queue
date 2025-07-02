# In app/workers/job_processor.py
import asyncio
from app.database import SessionLocal
from app.services import job_service
import datetime
from app import models

async def process_jobs():
    """The main worker function that will be run in a loop."""
    print("WORKER: Checking for pending jobs...")
    db = SessionLocal()
    try:
        job_to_run = job_service.get_pending_job_to_run(db)

        if job_to_run:
            print(f"WORKER: Found job {job_to_run.job_id}. Changing status to RUNNING.")

            # --- NEW LOGIC STARTS HERE ---

            # 1. Update status to RUNNING
            job_to_run.status = models.JobStatus.RUNNING
            job_to_run.started_at = datetime.datetime.utcnow()
            db.commit()
            db.refresh(job_to_run)

            # 2. Simulate doing the actual work
            print(f"WORKER: Executing job {job_to_run.job_id}...")
            await asyncio.sleep(10) # Simulate a 10-second task

            # 3. Update status to SUCCESS
            job_to_run.status = models.JobStatus.SUCCESS
            job_to_run.completed_at = datetime.datetime.utcnow()
            db.commit()

            print(f"WORKER: Job {job_to_run.job_id} completed successfully.")
            # --- NEW LOGIC ENDS HERE ---

        else:
            print("WORKER: No pending jobs found.")
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