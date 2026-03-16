from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from loguru import logger

from app.core.agents.registry import AgentRegistry
from app.models.schemas import AgentStep

router = APIRouter()

agent_registry = AgentRegistry()

@router.get("/")
async def list_agents():
    agents = agent_registry.list_agents()
    return {
        "agents": agents,
        "count": len(agents)
    }

@router.get("/{agent_name}")
async def get_agent_info(agent_name: str):
    agent_info = agent_registry.get_agent_info(agent_name)
    
    if not agent_info:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent_info

@router.post("/{agent_name}/execute")
async def execute_agent(
    agent_name: str,
    task: Dict[str, Any]
):
    try:
        agent = agent_registry.get_agent(agent_name)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        result = await agent.execute(task)
        
        return {
            "success": True,
            "agent": agent_name,
            "result": result
        }
    except Exception as e:
        logger.error(f"Agent execution failed: {agent_name} - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
