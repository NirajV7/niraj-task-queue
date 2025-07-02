import enum
import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    Enum as SAEnum,
    ForeignKey,
    Text
)
from sqlalchemy.orm import relationship
from ..database import Base

# Using Python's built-in Enum for status and priority levels for type safety.
class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked" # For jobs waiting on dependencies

class PriorityLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False, index=True)
    priority = Column(SAEnum(PriorityLevel), default=PriorityLevel.NORMAL, nullable=False)
    status = Column(SAEnum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    payload = Column(JSON, nullable=True)
    
    # Execution and configuration details
    resource_requirements = Column(JSON, nullable=True)
    retry_config = Column(JSON, nullable=True)
    timeout_seconds = Column(Integer, nullable=True)
    
     # --- NEW FIELDS FOR FAILURE HANDLING ---
    last_error = Column(Text, nullable=True) # To store the last error message
    current_attempt = Column(Integer, default=0, nullable=False, server_default='0')
    run_at = Column(DateTime, nullable=True, index=True) # For scheduling retries
    
    # Timestamps for tracking
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships for dependencies
    # The jobs that this job depends on
    dependencies = relationship(
        "Job",
        secondary="job_dependencies",
        primaryjoin="Job.id==JobDependency.job_id",
        secondaryjoin="Job.id==JobDependency.depends_on_id",
        back_populates="dependents"
    )
    # The jobs that depend on this job
    dependents = relationship(
        "Job",
        secondary="job_dependencies",
        primaryjoin="Job.id==JobDependency.depends_on_id",
        secondaryjoin="Job.id==JobDependency.job_id",
        back_populates="dependencies"
    )

# Association table for many-to-many relationship for dependencies
class JobDependency(Base):
    __tablename__ = 'job_dependencies'
    job_id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)
    depends_on_id = Column(Integer, ForeignKey('jobs.id'), primary_key=True)