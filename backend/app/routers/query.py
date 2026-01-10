"""
Query Routes
API endpoints for asking questions and getting answers from documents
"""

from fastapi import APIRouter, HTTPException, status
from typing import Optional
import logging

from ..models import (
    QuestionRequest,
    QuestionResponse,
    SourceReference
)
from ..services.rag_engine import get_rag_engine

router = APIRouter(prefix="/query", tags=["Query"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer based on uploaded documents.
    
    This is the main RAG endpoint!
    
    Flow:
    1. Receive question
    2. Generate embedding for question
    3. Find relevant document chunks
    4. Pass chunks + question to LLM
    5. Return answer with sources
    """
    
    try:
        logger.info(f"Received question: {request.question[:100]}...")
        logger.debug(f"Document IDs: {request.document_ids}, Conversation ID: {request.conversation_id}")
        
        # Get RAG engine
        rag_engine = get_rag_engine()
        
        # Answer the question
        result = rag_engine.answer_question(
            question=request.question,
            document_ids=request.document_ids,
            conversation_id=request.conversation_id
        )
        
        # Convert sources to SourceReference models
        sources = [
            SourceReference(
                document_id=src['document_id'],
                document_name=src['document_name'],
                page_number=src['page_number'],
                chunk_text=src['chunk_text'],
                relevance_score=src['relevance_score']
            )
            for src in result['sources']
        ]
        
        # Build response
        response = QuestionResponse(
            answer=result['answer'],
            sources=sources,
            conversation_id=result['conversation_id'],
            processing_time=result['processing_time'],
            model_used=result['model_used']
        )
        
        logger.info(f"Question answered in {result['processing_time']:.2f}s")
        
        return response
        
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@router.get("/conversation/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history for a specific conversation.
    """
    
    try:
        rag_engine = get_rag_engine()
        history = rag_engine.get_conversation_history(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "message_count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )