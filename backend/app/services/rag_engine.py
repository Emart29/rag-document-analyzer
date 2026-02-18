"""
RAG Engine - Retrieval-Augmented Generation
The core system that orchestrates document processing, retrieval, and answer generation

This is where the magic happens! 🧙‍♂️

RAG Flow:
1. User uploads document → Process & chunk → Generate embeddings → Store in ChromaDB
2. User asks question → Generate query embedding → Find relevant chunks → Pass to LLM → Return answer with sources
"""

import os
import hashlib
from typing import List, Dict, Optional, Tuple
import uuid
from datetime import datetime
import time
import logging

from .pdf_processor import PDFProcessor
from .embeddings import get_embedding_service
from .groq_client import GroqClient
from ..database.chroma_db import get_chroma_db
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Main RAG Engine that orchestrates all components.
    
    Responsibilities:
    - Document ingestion and processing
    - Question answering with context retrieval
    - Conversation management
    - Source citation
    """
    
    def __init__(self):
        """Initialize RAG engine with all required services."""
        
        logger.info("Initializing RAG Engine...")
        
        # Initialize components
        self.pdf_processor = PDFProcessor(
            chunk_size=int(os.getenv("CHUNK_SIZE", "500")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "50"))
        )
        
        self.embedding_service = get_embedding_service()
        self.groq_client = GroqClient()
        self.chroma_db = get_chroma_db()
        
        # Configuration
        self.top_k_results = int(os.getenv("TOP_K_RESULTS", "5"))
        
        # Conversation storage (in-memory for now)
        self.conversations = {}
        
        logger.info("RAG Engine initialized successfully!")
    
    def process_document(
        self,
        file_path: str,
        filename: str,
        file_size: int
    ) -> Dict:
        """
        Complete document processing pipeline.
        
        Steps:
        1. Check for duplicate content
        2. Extract text from PDF
        3. Chunk the text
        4. Generate embeddings for chunks
        5. Store in ChromaDB
        6. Return document metadata
        
        Args:
            file_path: Path to PDF file
            filename: Original filename
            file_size: File size in bytes
            
        Returns:
            Dict with processing results and document ID
        """
        
        try:
            start_time = time.time()
            
            logger.info(f"Processing document: {filename}")
            
            # Step 0: Generate content hash for duplicate detection
            content_hash = self._generate_file_hash(file_path)
            
            # Check for duplicate content
            existing_doc = self._check_duplicate(content_hash, filename)
            if existing_doc:
                match_type = existing_doc.get('match_type', 'unknown')
                logger.warning(f"Duplicate document detected ({match_type}): {filename} matches {existing_doc['filename']}")
                return {
                    'document_id': None,
                    'filename': filename,
                    'status': 'duplicate',
                    'error': f"Duplicate detected. This file matches existing document: {existing_doc['filename']}",
                    'existing_document_id': existing_doc['document_id'],
                    'message': f"Document already exists as '{existing_doc['filename']}'"
                }
            
            # Generate unique document ID
            document_id = f"doc_{uuid.uuid4().hex[:12]}"
            
            # Step 1: Process PDF
            logger.info("Step 1/4: Extracting text from PDF...")
            processed_data = self.pdf_processor.process_pdf(file_path)
            
            chunks = processed_data['chunks']
            logger.info(f"Created {len(chunks)} chunks")
            
            # Step 2: Generate embeddings
            logger.info("Step 2/4: Generating embeddings...")
            chunk_texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings(
                chunk_texts,
                show_progress=True
            )
            
            # Step 3: Prepare metadata
            logger.info("Step 3/4: Preparing metadata...")
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    'document_id': document_id,
                    'filename': filename,
                    'chunk_id': i,
                    'page_number': chunk.get('page_number'),
                    'file_size': file_size,
                    'page_count': processed_data.get('page_count'),
                    'chunk_length': chunk['chunk_length'],
                    'content_hash': content_hash,
                    'timestamp': datetime.now().isoformat()
                }
                # Remove any None values to satisfy ChromaDB metadata requirements
                metadata = {k: v for k, v in metadata.items() if v is not None}
                metadatas.append(metadata)
            
            # Step 4: Store in ChromaDB
            logger.info("Step 4/4: Storing in vector database...")
            chunk_ids = self.chroma_db.add_documents(
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            processing_time = time.time() - start_time
            
            result = {
                'document_id': document_id,
                'filename': filename,
                'status': 'completed',
                'page_count': processed_data.get('page_count'),
                'chunk_count': len(chunks),
                'file_size': file_size,
                'content_hash': content_hash,
                'processing_time': round(processing_time, 2),
                'message': f'Successfully processed {filename}'
            }
            
            logger.info(f"Document processed successfully in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                'document_id': None,
                'filename': filename,
                'status': 'failed',
                'error': str(e),
                'message': f'Failed to process {filename}'
            }
    
    def _generate_file_hash(self, file_path: str) -> str:
        """
        Generate SHA-256 hash of file content for duplicate detection.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex string of SHA-256 hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _check_duplicate(self, content_hash: str, filename: str = None) -> Optional[Dict]:
        """
        Check if a document with the same content hash or filename already exists.
        
        Args:
            content_hash: SHA-256 hash of file content
            filename: Original filename (for fallback check)
            
        Returns:
            Dict with existing document info if duplicate found, None otherwise
        """
        try:
            documents = self.list_documents()
            for doc in documents:
                # Check by filename first (simple duplicate check)
                if filename and doc.get('filename') == filename:
                    return {
                        'document_id': doc['document_id'],
                        'filename': doc['filename'],
                        'match_type': 'filename'
                    }
                
                # Check by content hash (exact content match)
                doc_chunks = self.chroma_db.get_by_document_id(doc['document_id'])
                if doc_chunks and doc_chunks.get('metadatas'):
                    for metadata in doc_chunks['metadatas']:
                        if metadata.get('content_hash') == content_hash:
                            return {
                                'document_id': doc['document_id'],
                                'filename': doc['filename'],
                                'match_type': 'content_hash'
                            }
            return None
        except Exception as e:
            logger.warning(f"Error checking for duplicates: {str(e)}")
            return None
    
    def answer_question(
        self,
        question: str,
        document_ids: Optional[List[str]] = None,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Answer a question using RAG.
        
        Steps:
        1. Generate embedding for question
        2. Retrieve relevant chunks from ChromaDB
        3. Build context from chunks
        4. Generate answer using Groq LLM
        5. Return answer with source citations
        
        Args:
            question: User's question
            document_ids: Optional list of document IDs to search (None = search all)
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict with answer, sources, and metadata
        """
        
        try:
            start_time = time.time()
            
            logger.info(f"Answering question: {question[:100]}...")
            
            # Generate conversation ID if not provided
            if conversation_id is None:
                conversation_id = f"conv_{uuid.uuid4().hex[:12]}"
            
            # Step 1: Generate query embedding
            logger.info("Step 1/4: Generating query embedding...")
            query_embedding = self.embedding_service.generate_embedding(question)
            
            # Step 2: Retrieve relevant chunks
            logger.info("Step 2/4: Retrieving relevant documents...")
            relevant_chunks = self.chroma_db.search_similar_chunks(
                query_embedding=query_embedding,
                document_ids=document_ids,
                top_k=self.top_k_results
            )
            
            if not relevant_chunks:
                return {
                    'answer': "I couldn't find any relevant information in the uploaded documents to answer this question.",
                    'sources': [],
                    'conversation_id': conversation_id,
                    'processing_time': time.time() - start_time,
                    'model_used': self.groq_client.model
                }
            
            # Step 3: Build context from chunks
            logger.info("Step 3/4: Building context...")
            context = self._build_context(relevant_chunks)
            
            # Get conversation history
            conversation_history = self.conversations.get(conversation_id, [])
            
            # Step 4: Generate answer
            logger.info("Step 4/4: Generating answer...")
            llm_result = self.groq_client.generate_answer(
                question=question,
                context=context,
                conversation_history=conversation_history,
                conversation_id=conversation_id,
                request_metadata={
                    "document_ids": document_ids or [],
                    "chunks_retrieved": len(relevant_chunks),
                },
            )
            answer = llm_result["answer"]
            
            # Step 5: Format sources
            sources = self._format_sources(relevant_chunks)
            
            # Update conversation history
            self._update_conversation(
                conversation_id,
                question,
                answer,
                sources
            )
            
            processing_time = time.time() - start_time
            
            result = {
                'answer': answer,
                'sources': sources,
                'conversation_id': conversation_id,
                'processing_time': round(processing_time, 2),
                'model_used': self.groq_client.model,
                'chunks_used': len(relevant_chunks),
                'prompt_tokens': llm_result['prompt_tokens'],
                'completion_tokens': llm_result['completion_tokens'],
                'total_tokens': llm_result['total_tokens'],
                'estimated_cost_usd': llm_result['cost_usd'],
                'llm_latency_ms': llm_result['latency_ms'],
                'prompt_template_key': llm_result['prompt_template_key'],
                'prompt_template_version': llm_result['prompt_template_version']
            }
            
            logger.info(f"Question answered in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            raise Exception(f"Failed to answer question: {str(e)}")
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: List of retrieved chunks with metadata
            
        Returns:
            Formatted context string
        """
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            
            # Format: [Source 1 - filename, page X] chunk_text
            source_info = f"[Source {i} - {metadata.get('filename', 'Unknown')}"
            
            if metadata.get('page_number'):
                source_info += f", Page {metadata['page_number']}"
            
            source_info += "]"
            
            context_parts.append(f"{source_info}\n{chunk['text']}\n")
        
        context = "\n".join(context_parts)
        
        return context
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """
        Format chunk information into source references.
        
        Args:
            chunks: Retrieved chunks
            
        Returns:
            List of formatted source dictionaries
        """
        
        sources = []
        
        for chunk in chunks:
            metadata = chunk['metadata']
            
            source = {
                'document_id': metadata.get('document_id'),
                'document_name': metadata.get('filename', 'Unknown'),
                'page_number': metadata.get('page_number'),
                'chunk_text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                'relevance_score': round(chunk['similarity_score'], 4)
            }
            
            sources.append(source)
        
        return sources
    
    def _update_conversation(
        self,
        conversation_id: str,
        question: str,
        answer: str,
        sources: List[Dict]
    ):
        """
        Update conversation history.
        
        Args:
            conversation_id: Conversation identifier
            question: User's question
            answer: Generated answer
            sources: Source references
        """
        
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # Add user message
        self.conversations[conversation_id].append({
            "role": "user",
            "content": question
        })
        
        # Add assistant message
        self.conversations[conversation_id].append({
            "role": "assistant",
            "content": answer
        })
        
        # Keep only last 10 exchanges (20 messages)
        if len(self.conversations[conversation_id]) > 20:
            self.conversations[conversation_id] = self.conversations[conversation_id][-20:]
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            List of messages
        """
        return self.conversations.get(conversation_id, [])
    
    def delete_document(self, document_id: str) -> Dict:
        """
        Delete a document and all its chunks.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Dict with deletion results
        """
        
        try:
            chunks_deleted = self.chroma_db.delete_document(document_id)
            
            if chunks_deleted == 0:
                return {
                    'document_id': document_id,
                    'chunks_deleted': 0,
                    'success': False,
                    'error': f'Document {document_id} not found',
                    'message': f'Document {document_id} not found'
                }
            
            return {
                'document_id': document_id,
                'chunks_deleted': chunks_deleted,
                'success': True,
                'message': f'Deleted document {document_id} ({chunks_deleted} chunks)'
            }
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return {
                'document_id': document_id,
                'success': False,
                'error': str(e),
                'message': 'Failed to delete document'
            }
    
    def list_documents(self) -> List[Dict]:
        """
        List all documents in the system.
        
        Returns:
            List of document metadata
        """
        
        try:
            documents = self.chroma_db.get_all_documents()
            
            # Add chunk count for each document
            for doc in documents:
                doc_chunks = self.chroma_db.get_by_document_id(doc['document_id'])
                doc['chunk_count'] = len(doc_chunks['ids'])
                doc['status'] = 'completed'
            
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get system statistics.
        
        Returns:
            Dict with stats
        """
        
        try:
            db_stats = self.chroma_db.get_stats()
            
            stats = {
                'total_documents': db_stats.get('total_documents', 0),
                'total_chunks': db_stats.get('total_chunks', 0),
                'total_conversations': len(self.conversations),
                'embedding_model': self.embedding_service.model_name,
                'llm_model': self.groq_client.model,
                'chunk_size': self.pdf_processor.chunk_size,
                'chunk_overlap': self.pdf_processor.chunk_overlap
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
    
    def health_check(self) -> Dict:
        """
        Check health of all components.
        
        Returns:
            Dict with health status
        """
        
        health = {
            'status': 'healthy',
            'components': {}
        }
        
        # Check Groq API
        try:
            groq_ok = self.groq_client.test_connection()
            health['components']['groq_api'] = 'healthy' if groq_ok else 'unhealthy'
        except:
            health['components']['groq_api'] = 'unhealthy'
            health['status'] = 'degraded'
        
        # Check ChromaDB
        try:
            chroma_ok = self.chroma_db.test_connection()
            health['components']['chromadb'] = 'healthy' if chroma_ok else 'unhealthy'
        except:
            health['components']['chromadb'] = 'unhealthy'
            health['status'] = 'degraded'
        
        # Check Embeddings
        try:
            embed_ok = self.embedding_service.test_embedding()
            health['components']['embeddings'] = 'healthy' if embed_ok else 'unhealthy'
        except:
            health['components']['embeddings'] = 'unhealthy'
            health['status'] = 'degraded'
        
        return health


# Singleton instance
_rag_engine_instance = None


def get_rag_engine() -> RAGEngine:
    """
    Get singleton instance of RAG Engine.
    
    Returns:
        RAGEngine instance
    """
    global _rag_engine_instance
    
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    
    return _rag_engine_instance


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing RAG Engine...")
    
    try:
        # Initialize engine
        engine = RAGEngine()
        
        # Test health check
        print("\n1️⃣ Testing health check...")
        health = engine.health_check()
        print(f"✅ System status: {health['status']}")
        print(f"   Components: {health['components']}")
        
        # Test stats
        print("\n2️⃣ Getting stats...")
        stats = engine.get_stats()
        print(f"✅ Documents: {stats.get('total_documents', 0)}")
        print(f"   Chunks: {stats.get('total_chunks', 0)}")
        print(f"   Model: {stats.get('llm_model', 'Unknown')}")
        
        # List documents
        print("\n3️⃣ Listing documents...")
        docs = engine.list_documents()
        print(f"✅ Found {len(docs)} documents")
        
        print("\n✅ RAG Engine is ready!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")