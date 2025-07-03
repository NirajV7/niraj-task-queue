# In app/schemas.py

import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .models.job import JobStatus, PriorityLevel

# Pydantic model for the request body when creating a new job
class JobCreate(BaseModel):
    idempotency_key: Optional[str] = None
    type: str = Field(..., example="data_export")
    priority: PriorityLevel = Field(default=PriorityLevel.NORMAL, example="normal")
    payload: Optional[Dict[str, Any]] = Field(None, example={"user_id": 123, "format": "csv"})
    resource_requirements: Optional[Dict[str, Any]] = Field(None, example={"cpu_units": 2, "memory_mb": 512})
    depends_on: Optional[List[str]] = Field(None, example=["job_abc123"])
    retry_config: Optional[Dict[str, Any]] = Field(None, example={"max_attempts": 3, "backoff_multiplier": 2})
    timeout_seconds: Optional[int] = Field(None, example=3600)


# Pydantic model for the data sent back by the API
class JobResponse(BaseModel):
    job_id: str
    type: str
    status: JobStatus
    created_at: datetime.datetime
    priority: PriorityLevel

    # This is the new way to set ORM mode in Pydantic V2
    model_config = ConfigDict(from_attributes=True)
        
class JobLogResponse(BaseModel):
    timestamp: datetime.datetime
    message: str

    class Config:
        from_attributes = True