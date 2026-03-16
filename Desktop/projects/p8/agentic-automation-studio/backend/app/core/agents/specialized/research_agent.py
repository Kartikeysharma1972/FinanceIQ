from typing import List
from app.core.agents.base_agent import BaseAgent

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Assistant",
            description="Specialized in gathering, analyzing, and summarizing information from various sources",
            system_prompt="""You are a research assistant AI. Your role is to:
- Gather relevant information from provided sources
- Analyze and synthesize information
- Create comprehensive summaries
- Identify key insights and patterns
- Provide well-structured research outputs

Be thorough, accurate, and cite sources when applicable."""
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Information gathering",
            "Document analysis",
            "Summarization",
            "Pattern recognition",
            "Research synthesis"
        ]
