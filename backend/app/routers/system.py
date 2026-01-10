"""
System Routes
Health checks, stats, and system information
"""

from fastapi import APIRouter, HTTPException
import logging
import os

from ..models import HealthResponse, StatsResponse
from ..services.rag_engine import get_rag_engine

router = APIRouter(prefix="/system", tags=["System"])
logger = logging.getLogger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check system health and component status.
    """
    
    try:
        rag_engine = get_rag_engine()
        health = rag_engine.health_check()
        
        response = HealthResponse(
            status=health['status'],
            version=os.getenv("APP_VERSION", "1.0.0"),
            groq_api_status=health['components'].get('groq_api', 'unknown'),
            chromadb_status=health['components'].get('chromadb', 'unknown'),
            embedding_model_loaded=health['components'].get('embeddings') == 'healthy'
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            version=os.getenv("APP_VERSION", "1.0.0"),
            groq_api_status="unknown",
            chromadb_status="unknown",
            embedding_model_loaded=False
        )


@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Get system statistics.
    """
    
    try:
        rag_engine = get_rag_engine()
        stats = rag_engine.get_stats()
        
        # Calculate average response time (mock for now)
        # In production, you'd track this in a database
        avg_response_time = 1.5
        
        # Calculate uptime (mock)
        uptime_seconds = 3600.0
        
        response = StatsResponse(
            total_documents=stats.get('total_documents', 0),
            total_chunks=stats.get('total_chunks', 0),
            total_conversations=stats.get('total_conversations', 0),
            total_questions_answered=0,  # Would track this in production
            average_response_time=avg_response_time,
            uptime_seconds=uptime_seconds
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/info")
async def get_system_info():
    """
    Get detailed system information.
    """
    
    try:
        rag_engine = get_rag_engine()
        stats = rag_engine.get_stats()
        
        return {
            "app_name": os.getenv("APP_NAME", "RAG Document Analyzer"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "embedding_model": stats.get('embedding_model', 'unknown'),
            "llm_model": stats.get('llm_model', 'unknown'),
            "chunk_size": stats.get('chunk_size', 500),
            "chunk_overlap": stats.get('chunk_overlap', 50),
            "max_file_size_mb": int(os.getenv("MAX_FILE_SIZE_MB", "10")),
            "allowed_file_types": os.getenv("ALLOWED_FILE_TYPES", ".pdf").split(",")
        }
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system info: {str(e)}"
        )