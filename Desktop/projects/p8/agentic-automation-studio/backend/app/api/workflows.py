from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from loguru import logger

from app.core.database import get_db
from app.models.workflow import Workflow, WorkflowStatus
from app.models.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse

router = APIRouter()

@router.post("/", response_model=WorkflowResponse)
async def create_workflow(
    workflow: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    db_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        trigger_type=workflow.trigger_type,
        trigger_config=workflow.trigger_config,
        nodes=[node.model_dump() for node in workflow.nodes],
        edges=[edge.model_dump() for edge in workflow.edges],
        variables=workflow.variables
    )
    
    db.add(db_workflow)
    await db.commit()
    await db.refresh(db_workflow)
    
    logger.info(f"Created workflow: {db_workflow.id} - {db_workflow.name}")
    return db_workflow

@router.get("/", response_model=List[WorkflowResponse])
async def list_workflows(
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Workflow)
    if status:
        query = query.where(Workflow.status == status)
    
    result = await db.execute(query)
    workflows = result.scalars().all()
    return workflows

@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    update_data = workflow_update.model_dump(exclude_unset=True)
    
    if "nodes" in update_data:
        update_data["nodes"] = [node.model_dump() if hasattr(node, 'model_dump') else node for node in update_data["nodes"]]
    if "edges" in update_data:
        update_data["edges"] = [edge.model_dump() if hasattr(edge, 'model_dump') else edge for edge in update_data["edges"]]
    
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    await db.commit()
    await db.refresh(workflow)
    
    logger.info(f"Updated workflow: {workflow_id}")
    return workflow

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    await db.delete(workflow)
    await db.commit()
    
    logger.info(f"Deleted workflow: {workflow_id}")
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/activate")
async def activate_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.status = WorkflowStatus.ACTIVE
    await db.commit()
    
    logger.info(f"Activated workflow: {workflow_id}")
    return {"message": "Workflow activated", "workflow_id": workflow_id}

@router.post("/{workflow_id}/pause")
async def pause_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.status = WorkflowStatus.PAUSED
    await db.commit()
    
    logger.info(f"Paused workflow: {workflow_id}")
    return {"message": "Workflow paused", "workflow_id": workflow_id}
