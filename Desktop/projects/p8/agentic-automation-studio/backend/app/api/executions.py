from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime
from loguru import logger

from app.core.database import get_db
from app.models.workflow import WorkflowExecution, ExecutionStatus, Workflow
from app.models.schemas import ExecutionTrigger, ExecutionResponse
from app.core.workflow_engine.executor import WorkflowExecutor

router = APIRouter()

@router.post("/trigger", response_model=ExecutionResponse)
async def trigger_execution(
    trigger: ExecutionTrigger,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == trigger.workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    execution = WorkflowExecution(
        workflow_id=trigger.workflow_id,
        trigger_data=trigger.trigger_data,
        status=ExecutionStatus.PENDING
    )
    
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    background_tasks.add_task(execute_workflow_async, execution.id, workflow, trigger.trigger_data)
    
    logger.info(f"Triggered execution: {execution.id} for workflow: {trigger.workflow_id}")
    return execution

async def execute_workflow_async(execution_id: str, workflow: Workflow, trigger_data: dict):
    from app.core.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
        execution = result.scalar_one_or_none()
        
        if not execution:
            logger.error(f"Execution not found: {execution_id}")
            return
        
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()
        await db.commit()
        
        try:
            executor = WorkflowExecutor()
            result = await executor.execute(workflow, trigger_data, execution_id, db)
            
            execution.status = ExecutionStatus.COMPLETED
            execution.result = result
            execution.completed_at = datetime.utcnow()
            
            logger.info(f"Execution completed: {execution_id}")
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.error = str(e)
            execution.completed_at = datetime.utcnow()
            
            logger.error(f"Execution failed: {execution_id} - {str(e)}")
        
        await db.commit()

@router.get("/", response_model=List[ExecutionResponse])
async def list_executions(
    workflow_id: str = None,
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(WorkflowExecution).order_by(WorkflowExecution.created_at.desc()).limit(limit)
    
    if workflow_id:
        query = query.where(WorkflowExecution.workflow_id == workflow_id)
    if status:
        query = query.where(WorkflowExecution.status == status)
    
    result = await db.execute(query)
    executions = result.scalars().all()
    return executions

@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution

@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed execution")
    
    execution.status = ExecutionStatus.CANCELLED
    execution.completed_at = datetime.utcnow()
    await db.commit()
    
    logger.info(f"Cancelled execution: {execution_id}")
    return {"message": "Execution cancelled", "execution_id": execution_id}

@router.get("/{execution_id}/logs")
async def get_execution_logs(
    execution_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
    execution = result.scalar_one_or_none()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return {
        "execution_id": execution_id,
        "logs": execution.execution_log or []
    }
