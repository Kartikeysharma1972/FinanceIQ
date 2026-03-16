from typing import Dict, List, Optional, Any
from loguru import logger

from app.core.tools.file_tools import ReadFileTool, WriteFileTool, ReadCSVTool
from app.core.tools.text_tools import SummarizeTextTool, ExtractEntitiesTool
from app.core.tools.data_tools import SaveJSONTool, GenerateReportTool

class ToolRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance.tools = {}
            cls._instance._register_default_tools()
        return cls._instance
    
    def _register_default_tools(self):
        self.register_tool(ReadFileTool())
        self.register_tool(WriteFileTool())
        self.register_tool(ReadCSVTool())
        self.register_tool(SummarizeTextTool())
        self.register_tool(ExtractEntitiesTool())
        self.register_tool(SaveJSONTool())
        self.register_tool(GenerateReportTool())
        
        logger.info(f"Registered {len(self.tools)} default tools")
    
    def register_tool(self, tool: Any):
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[Any]:
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "description": tool.description,
                "parameters": [
                    {
                        "name": p.name,
                        "type": p.type,
                        "description": p.description,
                        "required": p.required
                    }
                    for p in tool.parameters
                ]
            }
            for name, tool in self.tools.items()
        ]
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        tool = self.tools.get(name)
        if tool:
            return tool.get_schema()
        return None
