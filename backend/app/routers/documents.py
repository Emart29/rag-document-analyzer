"""
Document Routes
API endpoints for document upload, management, and deletion
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
import os
import shutil
from pathlib import Path
import logging

from ..models import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    DocumentInfo,
    DocumentStatus,
    DocumentMetadata
)
from ..services.rag_engine import get_rag_engine

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

# Get upload directory from env
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

# File validation
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024  # MB to bytes
ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.
    
    Steps:
    1. Validate file (type, size)
    2. Save file temporarily
    3. Process with RAG engine
    4. Return document ID and metadata
    """
    
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Only PDF files are supported."
            )
        
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Save file temporarily
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        logger.info(f"Saved file: {file.filename} ({file_size} bytes)")
        
        # Process document with RAG engine
        rag_engine = get_rag_engine()
        
        result = rag_engine.process_document(
            file_path=file_path,
            filename=file.filename,
            file_size=file_size
        )
        
        # Clean up temporary file (optional - keep if you want to preserve originals)
        # os.remove(file_path)
        
        if result['status'] == 'failed':
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Document processing failed')
            )
        
        if result['status'] == 'duplicate':
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.get('error', 'Duplicate document detected')
            )
        
        # Build response
        metadata = DocumentMetadata(
            filename=file.filename,
            file_size=file_size,
            page_count=result.get('page_count'),
            file_type=file_ext[1:]  # Remove the dot
        )
        
        response = DocumentUploadResponse(
            document_id=result['document_id'],
            filename=file.filename,
            status=DocumentStatus.COMPLETED,
            message=result['message'],
            metadata=metadata
        )
        
        logger.info(f"Document processed successfully: {result['document_id']}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """
    Get list of all uploaded documents.
    """
    
    try:
        rag_engine = get_rag_engine()
        documents = rag_engine.list_documents()
        
        # Convert to DocumentInfo models
        doc_infos = []
        for doc in documents:
            doc_info = DocumentInfo(
                document_id=doc['document_id'],
                filename=doc['filename'],
                upload_date=doc['upload_date'],
                page_count=doc.get('page_count'),
                chunk_count=doc.get('chunk_count', 0),
                file_size=doc.get('file_size', 0),
                status=DocumentStatus.COMPLETED
            )
            doc_infos.append(doc_info)
        
        response = DocumentListResponse(
            documents=doc_infos,
            total_count=len(doc_infos)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks.
    """
    
    try:
        rag_engine = get_rag_engine()
        result = rag_engine.delete_document(document_id)
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Document not found')
            )
        
        response = DocumentDeleteResponse(
            document_id=document_id,
            message=result['message'],
            success=True
        )
        
        logger.info(f"Document deleted: {document_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document_info(document_id: str):
    """
    Get detailed information about a specific document.
    """
    
    try:
        rag_engine = get_rag_engine()
        documents = rag_engine.list_documents()
        
        # Find the document
        doc = next((d for d in documents if d['document_id'] == document_id), None)
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        return doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document info: {str(e)}"
        )