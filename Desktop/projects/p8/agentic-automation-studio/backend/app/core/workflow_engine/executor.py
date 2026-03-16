from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.workflow import Workflow, WorkflowExecution
from app.core.agents.registry import AgentRegistry
from app.core.tools.registry import ToolRegistry
from app.core.llm.ollama_client import ollama_client

class WorkflowExecutor:
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        self.execution_context = {}
    
    async def execute(
        self,
        workflow: Workflow,
        trigger_data: Dict[str, Any],
        execution_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        logger.info(f"Starting workflow execution: {workflow.id}")
        
        self.execution_context = {
            "trigger": trigger_data,
            "variables": workflow.variables or {},
            "results": {}
        }
        
        nodes = workflow.nodes
        edges = workflow.edges or []
        
        execution_graph = self._build_execution_graph(nodes, edges)
        
        result = await self._execute_graph(execution_graph, execution_id, db)
        
        logger.info(f"Workflow execution completed: {workflow.id}")
        return result
    
    def _build_execution_graph(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        graph = {
            "nodes": {node["id"]: node for node in nodes},
            "edges": edges,
            "adjacency": {}
        }
        
        for node in nodes:
            graph["adjacency"][node["id"]] = []
        
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            graph["adjacency"][source].append({
                "target": target,
                "condition": edge.get("condition")
            })
        
        return graph
    
    async def _execute_graph(
        self,
        graph: Dict[str, Any],
        execution_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        start_nodes = self._find_start_nodes(graph)
        
        visited = set()
        results = {}
        
        for start_node_id in start_nodes:
            await self._execute_node_recursive(
                start_node_id,
                graph,
                visited,
                results,
                execution_id,
                db
            )
        
        return {
            "success": True,
            "results": results,
            "nodes_executed": len(visited)
        }
    
    def _find_start_nodes(self, graph: Dict[str, Any]) -> List[str]:
        all_nodes = set(graph["nodes"].keys())
        target_nodes = set()
        
        for edge in graph["edges"]:
            target_nodes.add(edge["target"])
        
        start_nodes = all_nodes - target_nodes
        
        return list(start_nodes) if start_nodes else list(all_nodes)[:1]
    
    async def _execute_node_recursive(
        self,
        node_id: str,
        graph: Dict[str, Any],
        visited: set,
        results: Dict[str, Any],
        execution_id: str,
        db: AsyncSession
    ):
        if node_id in visited:
            return
        
        visited.add(node_id)
        node = graph["nodes"][node_id]
        
        logger.info(f"Executing node: {node_id} ({node['type']})")
        
        node_result = await self._execute_node(node, execution_id, db)
        results[node_id] = node_result
        
        self.execution_context["results"][node_id] = node_result
        
        await self._log_execution_step(
            execution_id,
            node_id,
            node["type"],
            node_result,
            db
        )
        
        next_nodes = graph["adjacency"].get(node_id, [])
        for next_edge in next_nodes:
            should_execute = await self._evaluate_condition(
                next_edge.get("condition"),
                node_result
            )
            
            if should_execute:
                await self._execute_node_recursive(
                    next_edge["target"],
                    graph,
                    visited,
                    results,
                    execution_id,
                    db
                )
    
    async def _execute_node(
        self,
        node: Dict[str, Any],
        execution_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        node_type = node["type"]
        config = node.get("config", {})
        
        try:
            if node_type == "agent":
                return await self._execute_agent_node(config)
            elif node_type == "tool":
                return await self._execute_tool_node(config)
            elif node_type == "condition":
                return await self._execute_condition_node(config)
            elif node_type == "trigger":
                return {"success": True, "data": self.execution_context["trigger"]}
            else:
                return {"success": True, "message": f"Node type {node_type} executed"}
        except Exception as e:
            logger.error(f"Node execution failed: {node['id']} - {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_agent_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = config.get("agent_name", "research_assistant")
        task_description = self._resolve_template(config.get("task", ""))
        
        agent = self.agent_registry.get_agent(agent_name)
        
        if not agent:
            raise ValueError(f"Agent not found: {agent_name}")
        
        task = {
            "description": task_description,
            "context": self.execution_context
        }
        
        result = await agent.execute(task)
        return result
    
    async def _execute_tool_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = config.get("tool_name")
        parameters = config.get("parameters", {})
        
        resolved_params = {
            key: self._resolve_template(value)
            for key, value in parameters.items()
        }
        
        tool = self.tool_registry.get_tool(tool_name)
        
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        result = await tool.execute(**resolved_params)
        
        return {
            "success": True,
            "tool": tool_name,
            "result": result
        }
    
    async def _execute_condition_node(self, config: Dict[str, Any]) -> Dict[str, Any]:
        condition = config.get("condition", "")
        resolved_condition = self._resolve_template(condition)
        
        evaluation_prompt = f"""Evaluate the following condition and respond with only 'true' or 'false':

Condition: {resolved_condition}

Context: {self.execution_context.get('results', {})}

Answer (true/false):"""
        
        result = await ollama_client.generate(
            prompt=evaluation_prompt,
            temperature=0.1,
            max_tokens=10
        )
        
        is_true = "true" in result.lower()
        
        return {
            "success": True,
            "condition": condition,
            "evaluated": is_true
        }
    
    def _resolve_template(self, template: Any) -> Any:
        if not isinstance(template, str):
            return template
        
        import re
        
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_path = match.group(1).strip()
            parts = var_path.split('.')
            
            value = self.execution_context
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part, match.group(0))
                else:
                    return match.group(0)
            
            return str(value)
        
        return re.sub(pattern, replace_var, template)
    
    async def _evaluate_condition(
        self,
        condition: Optional[str],
        node_result: Dict[str, Any]
    ) -> bool:
        if not condition:
            return True
        
        try:
            resolved = self._resolve_template(condition)
            
            if resolved.lower() in ['true', '1', 'yes']:
                return True
            elif resolved.lower() in ['false', '0', 'no']:
                return False
            
            if node_result.get("success"):
                return True
            
            return True
        except:
            return True
    
    async def _log_execution_step(
        self,
        execution_id: str,
        node_id: str,
        node_type: str,
        result: Dict[str, Any],
        db: AsyncSession
    ):
        try:
            stmt = select(WorkflowExecution).where(WorkflowExecution.id == execution_id)
            db_result = await db.execute(stmt)
            execution = db_result.scalar_one_or_none()
            
            if execution:
                log_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "node_id": node_id,
                    "node_type": node_type,
                    "result": result
                }
                
                if execution.execution_log is None:
                    execution.execution_log = []
                
                execution.execution_log.append(log_entry)
                await db.commit()
        except Exception as e:
            logger.error(f"Failed to log execution step: {str(e)}")
