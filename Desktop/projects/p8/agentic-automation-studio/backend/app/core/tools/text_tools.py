from typing import Any, List
from loguru import logger

from app.core.tools.base_tool import BaseTool, ToolParameter
from app.core.llm.ollama_client import ollama_client

class SummarizeTextTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="summarize_text",
            description="Summarize long text into a concise summary",
            parameters=[
                ToolParameter(
                    name="text",
                    type="string",
                    description="Text to summarize",
                    required=True
                ),
                ToolParameter(
                    name="max_length",
                    type="integer",
                    description="Maximum length of summary in words",
                    required=False,
                    default=200
                )
            ]
        )
    
    async def execute(self, text: str, max_length: int = 200, **kwargs) -> str:
        self.validate_parameters(text=text)
        
        try:
            prompt = f"""Summarize the following text in no more than {max_length} words. 
Focus on the key points and main ideas.

Text:
{text}

Summary:"""
            
            summary = await ollama_client.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=max_length * 2
            )
            
            logger.info(f"Summarized text ({len(text)} -> {len(summary)} chars)")
            return summary.strip()
        except Exception as e:
            logger.error(f"Failed to summarize text: {str(e)}")
            raise

class ExtractEntitiesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="extract_entities",
            description="Extract named entities (people, organizations, locations) from text",
            parameters=[
                ToolParameter(
                    name="text",
                    type="string",
                    description="Text to extract entities from",
                    required=True
                )
            ]
        )
    
    async def execute(self, text: str, **kwargs) -> dict:
        self.validate_parameters(text=text)
        
        try:
            prompt = f"""Extract named entities from the following text. 
Categorize them as: PERSON, ORGANIZATION, LOCATION, DATE, or OTHER.

Format your response as a JSON object with entity types as keys and lists of entities as values.

Text:
{text}

Entities (JSON):"""
            
            entities_text = await ollama_client.generate(
                prompt=prompt,
                temperature=0.1,
                max_tokens=1000
            )
            
            import json
            try:
                entities = json.loads(entities_text.strip())
            except:
                entities = {"raw_output": entities_text}
            
            logger.info(f"Extracted entities from text")
            return entities
        except Exception as e:
            logger.error(f"Failed to extract entities: {str(e)}")
            raise

class SentimentAnalysisTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="sentiment_analysis",
            description="Analyze the sentiment of text (positive, negative, neutral)",
            parameters=[
                ToolParameter(
                    name="text",
                    type="string",
                    description="Text to analyze",
                    required=True
                )
            ]
        )
    
    async def execute(self, text: str, **kwargs) -> dict:
        self.validate_parameters(text=text)
        
        try:
            prompt = f"""Analyze the sentiment of the following text.
Respond with:
1. Overall sentiment (positive/negative/neutral)
2. Confidence score (0-1)
3. Brief explanation

Text:
{text}

Analysis:"""
            
            analysis = await ollama_client.generate(
                prompt=prompt,
                temperature=0.2,
                max_tokens=300
            )
            
            result = {
                "text": text[:100] + "..." if len(text) > 100 else text,
                "analysis": analysis.strip()
            }
            
            logger.info(f"Analyzed sentiment")
            return result
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            raise
