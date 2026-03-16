from celery import Task
from loguru import logger
from datetime import datetime

from app.core.tasks.celery_app import celery_app
from app.core.workflow_engine.executor import WorkflowExecutor

@celery_app.task(bind=True, name='execute_workflow')
def execute_workflow_task(self: Task, workflow_id: str, execution_id: str, trigger_data: dict):
    logger.info(f"Celery task started: execute_workflow - {execution_id}")
    
    try:
        import asyncio
        from app.core.database import AsyncSessionLocal
        from app.models.workflow import Workflow, WorkflowExecution, ExecutionStatus
        from sqlalchemy import select
        
        async def run_workflow():
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
                workflow = result.scalar_one_or_none()
                
                if not workflow:
                    raise ValueError(f"Workflow not found: {workflow_id}")
                
                result = await db.execute(select(WorkflowExecution).where(WorkflowExecution.id == execution_id))
                execution = result.scalar_one_or_none()
                
                if not execution:
                    raise ValueError(f"Execution not found: {execution_id}")
                
                execution.status = ExecutionStatus.RUNNING
                execution.started_at = datetime.utcnow()
                await db.commit()
                
                executor = WorkflowExecutor()
                result = await executor.execute(workflow, trigger_data, execution_id, db)
                
                execution.status = ExecutionStatus.COMPLETED
                execution.result = result
                execution.completed_at = datetime.utcnow()
                await db.commit()
                
                return result
        
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(run_workflow())
        
        logger.info(f"Celery task completed: {execution_id}")
        return result
    
    except Exception as e:
        logger.error(f"Celery task failed: {execution_id} - {str(e)}")
        raise

@celery_app.task(name='scheduled_workflow_trigger')
def scheduled_workflow_trigger(workflow_id: str):
    logger.info(f"Scheduled trigger for workflow: {workflow_id}")
    
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.models.workflow import Workflow, WorkflowExecution, ExecutionStatus
    from sqlalchemy import select
    
    async def create_execution():
        async with AsyncSessionLocal() as db:
            execution = WorkflowExecution(
                workflow_id=workflow_id,
                status=ExecutionStatus.PENDING,
                trigger_data={"trigger_type": "scheduled"}
            )
            
            db.add(execution)
            await db.commit()
            await db.refresh(execution)
            
            return execution.id
    
    loop = asyncio.get_event_loop()
    execution_id = loop.run_until_complete(create_execution())
    
    execute_workflow_task.delay(workflow_id, execution_id, {"trigger_type": "scheduled"})
    
    return {"execution_id": execution_id}
