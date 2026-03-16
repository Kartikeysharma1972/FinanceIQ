from typing import Dict, List, Optional, Any
from loguru import logger

from app.core.agents.specialized.research_agent import ResearchAgent
from app.core.agents.specialized.analyst_agent import AnalystAgent
from app.core.agents.specialized.writer_agent import WriterAgent

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self._register_default_agents()
    
    def _register_default_agents(self):
        self.register_agent("research_assistant", ResearchAgent())
        self.register_agent("data_analyst", AnalystAgent())
        self.register_agent("content_writer", WriterAgent())
        
        logger.info(f"Registered {len(self.agents)} default agents")
    
    def register_agent(self, name: str, agent: Any):
        self.agents[name] = agent
        logger.info(f"Registered agent: {name}")
    
    def get_agent(self, name: str) -> Optional[Any]:
        return self.agents.get(name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": agent.description,
                "capabilities": agent.get_capabilities()
            }
            for name, agent in self.agents.items()
        ]
    
    def get_agent_info(self, name: str) -> Optional[Dict[str, Any]]:
        agent = self.agents.get(name)
        if agent:
            return {
                "name": name,
                "description": agent.description,
                "capabilities": agent.get_capabilities(),
                "system_prompt": agent.system_prompt
            }
        return None
