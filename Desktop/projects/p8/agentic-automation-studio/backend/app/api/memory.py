from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from pydantic import BaseModel
from loguru import logger

router = APIRouter()

class DocumentStore(BaseModel):
    content: str
    metadata: dict = {}

class DocumentSearch(BaseModel):
    query: str
    top_k: int = 5
    filter: Optional[dict] = None

@router.post("/store")
async def store_document(
    document: DocumentStore,
    request: Request
):
    try:
        vector_store = request.app.state.vector_store
        doc_id = await vector_store.add_document(
            content=document.content,
            metadata=document.metadata
        )
        
        logger.info(f"Document stored: {doc_id}")
        return {
            "success": True,
            "document_id": doc_id
        }
    except Exception as e:
        logger.error(f"Failed to store document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(
    search: DocumentSearch,
    request: Request
):
    try:
        vector_store = request.app.state.vector_store
        results = await vector_store.search(
            query=search.query,
            top_k=search.top_k,
            filter=search.filter
        )
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_memory_stats(request: Request):
    try:
        vector_store = request.app.state.vector_store
        stats = await vector_store.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    request: Request
):
    try:
        vector_store = request.app.state.vector_store
        await vector_store.delete_document(document_id)
        
        logger.info(f"Document deleted: {document_id}")
        return {
            "success": True,
            "message": "Document deleted"
        }
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
