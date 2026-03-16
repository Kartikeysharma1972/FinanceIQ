from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class NodeType(str, Enum):
    TRIGGER = "trigger"
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"

class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    name: str
    config: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, float]] = None

class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    condition: Optional[str] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: str = "manual"
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge] = Field(default_factory=list)
    variables: Dict[str, Any] = Field(default_factory=dict)

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    trigger_type: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    nodes: Optional[List[WorkflowNode]] = None
    edges: Optional[List[WorkflowEdge]] = None
    variables: Optional[Dict[str, Any]] = None

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    trigger_type: str
    trigger_config: Dict[str, Any]
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    variables: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ExecutionTrigger(BaseModel):
    workflow_id: str
    trigger_data: Dict[str, Any] = Field(default_factory=dict)

class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    trigger_data: Dict[str, Any]
    execution_log: List[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentStep(BaseModel):
    phase: str
    timestamp: datetime
    input_data: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    output: Optional[Any] = None
    error: Optional[str] = None

class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

class ToolExecutionResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time: float
