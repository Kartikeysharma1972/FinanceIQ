from fastapi import APIRouter, HTTPException
from typing import List
from loguru import logger

from app.core.tools.registry import ToolRegistry
from app.models.schemas import ToolExecutionRequest, ToolExecutionResponse
import time

router = APIRouter()

tool_registry = ToolRegistry()

@router.get("/")
async def list_tools():
    tools = tool_registry.list_tools()
    return {
        "tools": tools,
        "count": len(tools)
    }

@router.get("/{tool_name}")
async def get_tool_info(tool_name: str):
    tool_info = tool_registry.get_tool_info(tool_name)
    
    if not tool_info:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return tool_info

@router.post("/execute")
async def execute_tool(request: ToolExecutionRequest) -> ToolExecutionResponse:
    start_time = time.time()
    
    try:
        tool = tool_registry.get_tool(request.tool_name)
        
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool_name}")
        
        result = await tool.execute(**request.parameters)
        execution_time = time.time() - start_time
        
        logger.info(f"Tool executed: {request.tool_name} in {execution_time:.2f}s")
        
        return ToolExecutionResponse(
            success=True,
            result=result,
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Tool execution failed: {request.tool_name} - {str(e)}")
        
        return ToolExecutionResponse(
            success=False,
            result=None,
            error=str(e),
            execution_time=execution_time
        )
