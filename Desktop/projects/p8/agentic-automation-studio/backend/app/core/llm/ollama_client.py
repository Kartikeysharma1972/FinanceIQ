import httpx
from typing import List, Dict, Any, Optional
from loguru import logger
from app.core.config import settings

class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.DEFAULT_LLM_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        model = model or self.default_model
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                if system:
                    payload["system"] = system
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        model = model or self.default_model
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama chat failed: {str(e)}")
            raise
    
    async def embed(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        model = model or self.embedding_model
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                payload = {
                    "model": model,
                    "prompt": text
                }
                
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("embedding", [])
        except Exception as e:
            logger.error(f"Ollama embedding failed: {str(e)}")
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                result = response.json()
                return result.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []

ollama_client = OllamaClient()
