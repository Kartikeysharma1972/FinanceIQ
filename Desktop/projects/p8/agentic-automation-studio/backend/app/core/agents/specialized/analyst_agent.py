from typing import List
from app.core.agents.base_agent import BaseAgent

class AnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Data Analyst",
            description="Specialized in analyzing data, identifying trends, and generating insights",
            system_prompt="""You are a data analyst AI. Your role is to:
- Analyze structured and unstructured data
- Identify trends and patterns
- Generate statistical insights
- Create data-driven recommendations
- Produce clear analytical reports

Be precise, data-driven, and provide actionable insights."""
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Data analysis",
            "Trend identification",
            "Statistical analysis",
            "Report generation",
            "Insight extraction"
        ]
