from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_LLM_MODEL: str = "deepseek-coder"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    
    DATABASE_URL: str = "sqlite:///./agentic_studio.db"
    REDIS_URL: str = "redis://localhost:6379"  # Optional, can be removed
    
    CHROMADB_PATH: str = "./data/chromadb"
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    MAX_WORKFLOW_EXECUTION_TIME: int = 3600
    MAX_AGENT_ITERATIONS: int = 10
    ENABLE_TOOL_SAFETY_CHECKS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
