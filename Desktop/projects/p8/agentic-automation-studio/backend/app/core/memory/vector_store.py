import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import uuid
from loguru import logger

from app.core.config import settings
from app.core.llm.ollama_client import ollama_client

class VectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self.initialized = False
    
    async def initialize(self):
        try:
            self.client = chromadb.PersistentClient(
                path=settings.CHROMADB_PATH,
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.client.get_or_create_collection(
                name="agentic_memory",
                metadata={"description": "Long-term memory for AI agents"}
            )
            
            self.initialized = True
            logger.info("Vector store initialized")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise
    
    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        if not self.initialized:
            await self.initialize()
        
        try:
            doc_id = f"doc_{uuid.uuid4().hex[:12]}"
            
            embedding = await ollama_client.embed(content)
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}]
            )
            
            return doc_id
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
            raise
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if not self.initialized:
            await self.initialize()
        
        try:
            query_embedding = await ollama_client.embed(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter
            )
            
            documents = []
            if results["ids"] and len(results["ids"]) > 0:
                for i in range(len(results["ids"][0])):
                    documents.append({
                        "id": results["ids"][0][i],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })
            
            return documents
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        if not self.initialized:
            await self.initialize()
        
        try:
            result = self.collection.get(ids=[doc_id])
            
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0] if result["metadatas"] else {}
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get document: {str(e)}")
            return None
    
    async def delete_document(self, doc_id: str):
        if not self.initialized:
            await self.initialize()
        
        try:
            self.collection.delete(ids=[doc_id])
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        if not self.initialized:
            await self.initialize()
        
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"total_documents": 0}
