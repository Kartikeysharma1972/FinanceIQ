import json
import aiofiles
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from loguru import logger

from app.core.tools.base_tool import BaseTool, ToolParameter

class SaveJSONTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="save_json",
            description="Save structured data as JSON file",
            parameters=[
                ToolParameter(
                    name="data",
                    type="object",
                    description="Data to save as JSON",
                    required=True
                ),
                ToolParameter(
                    name="file_path",
                    type="string",
                    description="Path to save the JSON file",
                    required=False,
                    default=None
                )
            ]
        )
    
    async def execute(self, data: Any, file_path: str = None, **kwargs) -> str:
        self.validate_parameters(data=data)
        
        try:
            if file_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"./data/outputs/output_{timestamp}.json"
            
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            json_str = json.dumps(data, indent=2, default=str)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json_str)
            
            logger.info(f"Saved JSON to: {file_path}")
            return f"Successfully saved data to {file_path}"
        except Exception as e:
            logger.error(f"Failed to save JSON: {str(e)}")
            raise

class GenerateReportTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="generate_report",
            description="Generate a formatted report from data",
            parameters=[
                ToolParameter(
                    name="title",
                    type="string",
                    description="Report title",
                    required=True
                ),
                ToolParameter(
                    name="data",
                    type="object",
                    description="Data to include in the report",
                    required=True
                ),
                ToolParameter(
                    name="format",
                    type="string",
                    description="Report format (markdown, html, text)",
                    required=False,
                    default="markdown"
                )
            ]
        )
    
    async def execute(self, title: str, data: Dict, format: str = "markdown", **kwargs) -> str:
        self.validate_parameters(title=title, data=data)
        
        try:
            if format == "markdown":
                report = self._generate_markdown_report(title, data)
            elif format == "html":
                report = self._generate_html_report(title, data)
            else:
                report = self._generate_text_report(title, data)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"./data/reports/report_{timestamp}.{format if format != 'text' else 'txt'}"
            
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(report)
            
            logger.info(f"Generated report: {file_path}")
            return report
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise
    
    def _generate_markdown_report(self, title: str, data: Dict) -> str:
        report = f"# {title}\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += "---\n\n"
        
        for key, value in data.items():
            report += f"## {key.replace('_', ' ').title()}\n\n"
            
            if isinstance(value, dict):
                for k, v in value.items():
                    report += f"- **{k}**: {v}\n"
            elif isinstance(value, list):
                for item in value:
                    report += f"- {item}\n"
            else:
                report += f"{value}\n"
            
            report += "\n"
        
        return report
    
    def _generate_html_report(self, title: str, data: Dict) -> str:
        report = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        .timestamp {{ color: #999; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""
        
        for key, value in data.items():
            report += f"    <h2>{key.replace('_', ' ').title()}</h2>\n"
            report += f"    <p>{value}</p>\n"
        
        report += "</body>\n</html>"
        return report
    
    def _generate_text_report(self, title: str, data: Dict) -> str:
        report = f"{title}\n"
        report += "=" * len(title) + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for key, value in data.items():
            report += f"{key.replace('_', ' ').title()}\n"
            report += "-" * len(key) + "\n"
            report += f"{value}\n\n"
        
        return report
