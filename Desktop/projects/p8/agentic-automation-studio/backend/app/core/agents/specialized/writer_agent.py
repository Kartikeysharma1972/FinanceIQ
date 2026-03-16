from typing import List
from app.core.agents.base_agent import BaseAgent

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Content Writer",
            description="Specialized in creating engaging, well-structured written content",
            system_prompt="""You are a content writer AI. Your role is to:
- Create engaging and clear written content
- Adapt tone and style to the audience
- Structure information effectively
- Generate creative and compelling copy
- Ensure grammatical accuracy

Be creative, clear, and audience-focused."""
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "Content creation",
            "Copywriting",
            "Editing",
            "Tone adaptation",
            "Creative writing"
        ]
