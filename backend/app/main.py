"""
Main FastAPI Application
RAG Document Analyzer Backend

This is the entry point for the backend API.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from collections import defaultdict
import time
import logging
import os
from dotenv import load_dotenv

from .database.observability_db import init_observability_db

# Load environment variables
load_dotenv()

# Import routers
from .routers import documents, query, system, observability

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Rate limiting configuration
class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed for this client."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > minute_ago
        ]
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return False
        
        # Record this request
        self.requests[client_ip].append(now)
        return True


# Initialize rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
)

# Create FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "RAG Document Analyzer API"),
    version=os.getenv("APP_VERSION", "1.0.0"),
    description="""
    🚀 RAG-Powered Document Analysis System
    
    Upload PDF documents and ask questions about their content using AI.
    
    Features:
    - PDF document upload and processing
    - Semantic search using embeddings
    - Question answering with source citations
    - Conversation history
    - Fast inference with Groq API
    
    Built with: FastAPI, Groq (Llama 3.1), ChromaDB, Sentence Transformers
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all requests."""
    # Skip rate limiting in development mode
    if os.getenv("DEBUG", "False") == "True":
        return await call_next(request)
    
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too many requests",
                "detail": "Rate limit exceeded. Please try again later."
            }
        )
    
    return await call_next(request)

# Include routers
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(system.router)
app.include_router(observability.router)


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "message": "🚀 RAG Document Analyzer API",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "docs": "/docs",
        "health": "/system/health",
        "endpoints": {
            "documents": {
                "upload": "POST /documents/upload",
                "list": "GET /documents/list",
                "delete": "DELETE /documents/{document_id}"
            },
            "query": {
                "ask": "POST /query/ask",
                "conversation": "GET /query/conversation/{conversation_id}"
            },
            "system": {
                "health": "GET /system/health",
                "stats": "GET /system/stats",
                "info": "GET /system/info"
            }
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "False") == "True" else "An unexpected error occurred"
        }
    )


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    logger.info("=" * 60)
    logger.info("🚀 Starting RAG Document Analyzer API")
    logger.info(f"   Version: {os.getenv('APP_VERSION', '1.0.0')}")
    logger.info(f"   Environment: {'Development' if os.getenv('DEBUG') == 'True' else 'Production'}")
    logger.info("=" * 60)
    
    # Initialize observability DB
    init_observability_db()

    # Initialize RAG engine (loads models)
    try:
        from .services.rag_engine import get_rag_engine
        rag_engine = get_rag_engine()
        logger.info("✅ RAG Engine initialized successfully")
        
        # Health check
        health = rag_engine.health_check()
        logger.info(f"✅ System health: {health['status']}")
        logger.info(f"   - Groq API: {health['components'].get('groq_api')}")
        logger.info(f"   - ChromaDB: {health['components'].get('chromadb')}")
        logger.info(f"   - Embeddings: {health['components'].get('embeddings')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG Engine: {str(e)}")
        logger.error("⚠️  Application may not function correctly")
    
    logger.info("=" * 60)
    logger.info("🎯 API is ready to accept requests!")
    logger.info(f"   📚 Docs: http://localhost:8000/docs")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    logger.info("=" * 60)
    logger.info("🛑 Shutting down RAG Document Analyzer API")
    logger.info("=" * 60)


# For testing purposes
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("DEBUG", "False") == "True"
    )