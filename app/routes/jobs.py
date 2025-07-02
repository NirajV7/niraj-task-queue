# In app/routes/jobs.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from .. import models, schemas
from ..services import job_service # Import the new service
from ..database import get_db
from typing import List, Optional
import asyncio
from ..services.connection_manager import manager

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("/", response_model=schemas.JobResponse, status_code=201)
async def submit_job(job_in: schemas.JobCreate, db: Session = Depends(get_db)): #<-- Changed to async
    """Submit a new job to the queue."""
    new_job = job_service.create_job(db=db, job_in=job_in)
    # Broadcast the update to all connected clients
    await manager.broadcast(f"Job {new_job.job_id} created with status: {new_job.status.value}")
    return new_job

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
async def cancel_job(job_id: str, db: Session = Depends(get_db)): #<-- Changed to async
    """
    Cancel a job if it is in a pending state.
    """
    db_job = job_service.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if db_job.status != models.JobStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status '{db_job.status.value}'."
        )

    db_job.status = models.JobStatus.CANCELLED
    db.commit()
    db.refresh(db_job)
    
    # Broadcast the update to all connected clients
    await manager.broadcast(f"Job {db_job.job_id} status changed to: {db_job.status.value}")
    return db_job

@router.websocket("/stream")
async def stream_job_updates(websocket: WebSocket):
    await manager.connect(websocket)
    print("WebSocket client connected to stream.")
    try:
        while True:
            # This loop keeps the connection alive.
            # The client will receive broadcasts sent from other parts of the app.
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket client disconnected from stream.")
        
@router.get("/{job_id}/logs", response_model=List[schemas.JobLogResponse])
def get_job_logs(job_id: str, db: Session = Depends(get_db)):
    """
    Get the execution logs for a specific job.
    """
    db_job = job_service.get_job(db=db, job_id=job_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return db_job.logs