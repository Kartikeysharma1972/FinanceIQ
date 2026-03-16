import aiofiles
import pandas as pd
from typing import Any
from pathlib import Path
from loguru import logger

from app.core.tools.base_tool import BaseTool, ToolParameter

class ReadFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Read content from a text file",
            parameters=[
                ToolParameter(
                    name="file_path",
                    type="string",
                    description="Path to the file to read",
                    required=True
                )
            ]
        )
    
    async def execute(self, file_path: str, **kwargs) -> str:
        self.validate_parameters(file_path=file_path)
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            logger.info(f"Read file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise

class WriteFileTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Write content to a text file",
            parameters=[
                ToolParameter(
                    name="file_path",
                    type="string",
                    description="Path to the file to write",
                    required=True
                ),
                ToolParameter(
                    name="content",
                    type="string",
                    description="Content to write to the file",
                    required=True
                )
            ]
        )
    
    async def execute(self, file_path: str, content: str, **kwargs) -> str:
        self.validate_parameters(file_path=file_path, content=content)
        
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            logger.info(f"Wrote file: {file_path}")
            return f"Successfully wrote {len(content)} characters to {file_path}"
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {str(e)}")
            raise

class ReadCSVTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="read_csv",
            description="Read and parse a CSV file",
            parameters=[
                ToolParameter(
                    name="file_path",
                    type="string",
                    description="Path to the CSV file",
                    required=True
                ),
                ToolParameter(
                    name="max_rows",
                    type="integer",
                    description="Maximum number of rows to read",
                    required=False,
                    default=1000
                )
            ]
        )
    
    async def execute(self, file_path: str, max_rows: int = 1000, **kwargs) -> dict:
        self.validate_parameters(file_path=file_path)
        
        try:
            df = pd.read_csv(file_path, nrows=max_rows)
            
            result = {
                "rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict(orient='records'),
                "summary": {
                    "total_rows": len(df),
                    "total_columns": len(df.columns),
                    "column_types": df.dtypes.astype(str).to_dict()
                }
            }
            
            logger.info(f"Read CSV: {file_path} ({len(df)} rows)")
            return result
        except Exception as e:
            logger.error(f"Failed to read CSV {file_path}: {str(e)}")
            raise
