"""
Pydantic Models for Request/Response Validation

These models ensure type safety and automatic API documentation
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Status of document processing"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Metadata for uploaded documents"""
    filename: str
    file_size: int
    upload_date: datetime = Field(default_factory=datetime.now)
    page_count: Optional[int] = None
    file_type: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "research_paper.pdf",
                "file_size": 2048576,
                "upload_date": "2024-01-15T10:30:00",
                "page_count": 15,
                "file_type": "pdf"
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    filename: str
    status: DocumentStatus
    message: str
    metadata: Optional[DocumentMetadata] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "filename": "research_paper.pdf",
                "status": "completed",
                "message": "Document processed successfully",
                "metadata": {
                    "filename": "research_paper.pdf",
                    "file_size": 2048576,
                    "page_count": 15,
                    "file_type": "pdf"
                }
            }
        }


class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., min_length=3, max_length=500)
    document_ids: Optional[List[str]] = None  # If None, search all documents
    conversation_id: Optional[str] = None
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the main findings of this research?",
                "document_ids": ["doc_123456"],
                "conversation_id": "conv_789"
            }
        }


class SourceReference(BaseModel):
    """Reference to source document and location"""
    document_id: str
    document_name: str
    page_number: Optional[int] = None
    chunk_text: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_123456",
                "document_name": "research_paper.pdf",
                "page_number": 5,
                "chunk_text": "The study found that...",
                "relevance_score": 0.92
            }
        }



class LLMObservabilityData(BaseModel):
    """Observability metrics returned with each answer."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    llm_latency_ms: float
    prompt_template_key: Optional[str] = None
    prompt_template_version: Optional[int] = None


class QuestionResponse(BaseModel):
    """Response model for questions"""
    answer: str
    sources: List[SourceReference]
    conversation_id: str
    processing_time: float
    model_used: str
    observability: Optional[LLMObservabilityData] = None

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The main findings indicate that...",
                "sources": [
                    {
                        "document_id": "doc_123456",
                        "document_name": "research_paper.pdf",
                        "page_number": 5,
                        "chunk_text": "The study found that...",
                        "relevance_score": 0.92
                    }
                ],
                "conversation_id": "conv_789",
                "processing_time": 1.23,
                "model_used": "llama-3.1-70b-versatile",
                "observability": {
                    "prompt_tokens": 122,
                    "completion_tokens": 96,
                    "total_tokens": 218,
                    "estimated_cost_usd": 0.00015,
                    "llm_latency_ms": 540.12,
                    "prompt_template_key": "rag_qa_system_prompt",
                    "prompt_template_version": 1
                }
            }
        }


class PromptTemplateCreate(BaseModel):
    """Create a new prompt template version."""
    template_key: str = Field(..., min_length=2, max_length=100)
    template_text: str = Field(..., min_length=10)
    description: Optional[str] = None
    activate: bool = True


class PromptTemplateResponse(BaseModel):
    id: int
    template_key: str
    version: int
    template_text: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime


class LLMLogEntry(BaseModel):
    id: int
    request_type: str
    conversation_id: Optional[str] = None
    model: str
    question: Optional[str] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    success: bool
    error_message: Optional[str] = None
    created_at: datetime


class LLMObservabilitySummary(BaseModel):
    window_hours: int
    summary: Dict[str, Any]
    trends: List[Dict[str, Any]]


class DocumentInfo(BaseModel):
    """Information about a stored document"""
    document_id: str
    filename: str
    upload_date: datetime
    page_count: Optional[int] = None
    chunk_count: int
    file_size: int
    status: DocumentStatus


class DocumentListResponse(BaseModel):
    """Response for listing documents"""
    documents: List[DocumentInfo]
    total_count: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "document_id": "doc_123456",
                        "filename": "research_paper.pdf",
                        "upload_date": "2024-01-15T10:30:00",
                        "page_count": 15,
                        "chunk_count": 45,
                        "file_size": 2048576,
                        "status": "completed"
                    }
                ],
                "total_count": 1
            }
        }


class DocumentDeleteResponse(BaseModel):
    """Response after deleting a document"""
    document_id: str
    message: str
    success: bool


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    groq_api_status: str
    chromadb_status: str
    embedding_model_loaded: bool


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Document not found",
                "detail": "The requested document ID does not exist",
                "error_code": "DOC_NOT_FOUND"
            }
        }


class ChatMessage(BaseModel):
    """Single message in conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sources: Optional[List[SourceReference]] = None


class ConversationHistory(BaseModel):
    """Conversation history"""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


class StatsResponse(BaseModel):
    """System statistics"""
    total_documents: int
    total_chunks: int
    total_conversations: int
    total_questions_answered: int
    average_response_time: float
    uptime_seconds: float