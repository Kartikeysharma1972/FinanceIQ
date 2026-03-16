from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None

class BaseTool(ABC):
    def __init__(self, name: str, description: str, parameters: List[ToolParameter]):
        self.name = name
        self.description = description
        self.parameters = parameters
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in self.parameters
            ]
        }
    
    def validate_parameters(self, **kwargs):
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                raise ValueError(f"Missing required parameter: {param.name}")
