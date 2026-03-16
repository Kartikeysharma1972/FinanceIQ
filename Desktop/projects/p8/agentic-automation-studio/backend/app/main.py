from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.api import workflows, agents, executions, tools, memory, auth
from app.core.config import settings
from app.core.database import init_db
from app.core.memory.vector_store import VectorStore

logger.remove()
logger.add(sys.stdout, level="INFO")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Agentic Automation Studio...")
    
    await init_db()
    logger.info("Database initialized")
    
    vector_store = VectorStore()
    await vector_store.initialize()
    app.state.vector_store = vector_store
    logger.info("Vector store initialized")
    
    yield
    
    logger.info("Shutting down Agentic Automation Studio...")

app = FastAPI(
    title="Agentic Automation Studio",
    description="Production-grade AI workflow automation platform running on local models",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(executions.router, prefix="/api/executions", tags=["Executions"])
app.include_router(tools.router, prefix="/api/tools", tags=["Tools"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])

@app.get("/")
async def root():
    return {
        "name": "Agentic Automation Studio",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "ollama": settings.OLLAMA_BASE_URL,
        "model": settings.DEFAULT_LLM_MODEL
    }
