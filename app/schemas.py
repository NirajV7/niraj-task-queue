import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .models.job import JobStatus, PriorityLevel

# Pydantic model for creating a new job (request body for POST /jobs)
class JobCreate(BaseModel):
    type: str = Field(..., example="data_export")
    priority: PriorityLevel = PriorityLevel.NORMAL
    payload: Dict[str, Any] = Field(..., example={"user_id": 123, "format": "csv"})
    resource_requirements: Optional[Dict[str, Any]] = Field(None, example={"cpu_units": 2, "memory_mb": 512})
    depends_on: Optional[List[str]] = Field(None, example=["job_abc123"])
    retry_config: Optional[Dict[str, Any]] = Field(None, example={"max_attempts": 3, "backoff_multiplier": 2})
    timeout_seconds: Optional[int] = Field(None, example=3600)

# Pydantic model for the response when a job is created or retrieved
class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    created_at: datetime.datetime
    priority: PriorityLevel
    
    # This allows Pydantic to read data from ORM models (like our Job class)
    class Config:
        from_attributes = True