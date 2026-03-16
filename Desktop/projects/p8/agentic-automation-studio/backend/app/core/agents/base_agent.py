from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from app.core.llm.ollama_client import ollama_client
from app.core.tools.registry import ToolRegistry

class BaseAgent(ABC):
    def __init__(self, name: str, description: str, system_prompt: str):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tool_registry = ToolRegistry()
        self.execution_log: List[Dict[str, Any]] = []
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.execution_log = []
        
        try:
            result = await self._reasoning_loop(task)
            return {
                "success": True,
                "result": result,
                "execution_log": self.execution_log
            }
        except Exception as e:
            logger.error(f"Agent {self.name} execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "execution_log": self.execution_log
            }
    
    async def _reasoning_loop(self, task: Dict[str, Any]) -> Any:
        observation = await self._observe(task)
        
        plan = await self._plan(observation)
        
        execution_result = await self._execute_plan(plan)
        
        evaluation = await self._evaluate(execution_result, task)
        
        return evaluation
    
    async def _observe(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self._log_step("observe", {
            "input": task,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return {
            "task": task,
            "available_tools": self.tool_registry.list_tools(),
            "context": task.get("context", {})
        }
    
    async def _plan(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        task_description = observation["task"].get("description", "")
        available_tools = observation["available_tools"]
        
        planning_prompt = f"""You are {self.name}. {self.description}

Task: {task_description}

Available tools: {', '.join([t['name'] for t in available_tools])}

Create a step-by-step plan to accomplish this task. For each step, specify:
1. What action to take
2. Which tool to use (if any)
3. Expected outcome

Respond in a structured format."""
        
        plan_text = await ollama_client.generate(
            prompt=planning_prompt,
            system=self.system_prompt,
            temperature=0.3
        )
        
        plan = {
            "reasoning": plan_text,
            "steps": self._parse_plan(plan_text)
        }
        
        self._log_step("plan", plan)
        return plan
    
    def _parse_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        steps = []
        lines = plan_text.split('\n')
        
        current_step = {}
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                if current_step:
                    steps.append(current_step)
                current_step = {"description": line}
            elif 'tool:' in line.lower():
                tool_name = line.split(':', 1)[1].strip()
                current_step["tool"] = tool_name
        
        if current_step:
            steps.append(current_step)
        
        return steps if steps else [{"description": plan_text}]
    
    async def _execute_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        
        for step in plan.get("steps", []):
            step_result = await self._execute_step(step)
            results.append(step_result)
        
        execution_result = {
            "steps_completed": len(results),
            "results": results
        }
        
        self._log_step("execute", execution_result)
        return execution_result
    
    async def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = step.get("tool")
        
        if tool_name:
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                try:
                    result = await tool.execute()
                    return {
                        "step": step["description"],
                        "tool": tool_name,
                        "result": result,
                        "success": True
                    }
                except Exception as e:
                    return {
                        "step": step["description"],
                        "tool": tool_name,
                        "error": str(e),
                        "success": False
                    }
        
        return {
            "step": step["description"],
            "success": True,
            "note": "No tool execution required"
        }
    
    async def _evaluate(self, execution_result: Dict[str, Any], original_task: Dict[str, Any]) -> Any:
        results_summary = "\n".join([
            f"- {r.get('step', 'Unknown')}: {'Success' if r.get('success') else 'Failed'}"
            for r in execution_result.get("results", [])
        ])
        
        evaluation_prompt = f"""Evaluate the execution results for this task:

Task: {original_task.get('description', '')}

Execution Results:
{results_summary}

Provide a final answer or output based on these results."""
        
        evaluation = await ollama_client.generate(
            prompt=evaluation_prompt,
            system=self.system_prompt,
            temperature=0.3
        )
        
        self._log_step("evaluate", {
            "evaluation": evaluation,
            "success": True
        })
        
        return evaluation
    
    def _log_step(self, phase: str, data: Dict[str, Any]):
        self.execution_log.append({
            "phase": phase,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        })
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        pass
