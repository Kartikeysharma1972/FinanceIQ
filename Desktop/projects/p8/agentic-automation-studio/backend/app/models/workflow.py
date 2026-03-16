from sqlalchemy import Column, String, JSON, DateTime, Enum as SQLEnum, Integer, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum
import uuid

class WorkflowStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"

class TriggerType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULE = "schedule"
    WEBHOOK = "webhook"
    FILE_UPLOAD = "file_upload"
    EVENT = "event"

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(String, primary_key=True, default=lambda: f"wf_{uuid.uuid4().hex[:12]}")
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(WorkflowStatus), default=WorkflowStatus.DRAFT)
    trigger_type = Column(SQLEnum(TriggerType), default=TriggerType.MANUAL)
    trigger_config = Column(JSON, default=dict)
    nodes = Column(JSON, nullable=False)
    edges = Column(JSON, default=list)
    variables = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String)

class ExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"
    
    id = Column(String, primary_key=True, default=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    workflow_id = Column(String, nullable=False)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING)
    trigger_data = Column(JSON, default=dict)
    execution_log = Column(JSON, default=list)
    result = Column(JSON)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
