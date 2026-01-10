"""
ChromaDB Handler
Vector database for storing and retrieving document embeddings

Why ChromaDB?
- Lightweight (no server needed!)
- Fast similarity search
- Perfect for RAG applications
- Works great on 8GB RAM
- Persistent storage
"""

import os
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
import uuid
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaDBHandler:
    """
    Handler for ChromaDB vector database operations.
    
    Manages:
    - Document storage with embeddings
    - Semantic search
    - Document metadata
    - Collection management
    """
    
    def __init__(
        self,
        persist_directory: str = None,
        collection_name: str = None
    ):
        """
        Initialize ChromaDB handler.
        
        Args:
            persist_directory: Directory to store database
            collection_name: Name of collection to use
        """
        
        # Get settings from environment or use defaults
        if persist_directory is None:
            persist_directory = os.getenv("CHROMA_DB_DIR", "chroma_db")
        
        if collection_name is None:
            collection_name = os.getenv("COLLECTION_NAME", "document_embeddings")
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        logger.info(f"Initializing ChromaDB at: {persist_directory}")
        
        try:
            # Initialize ChromaDB client with persistence
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Document chunks for RAG"}
            )
            
            logger.info(f"ChromaDB initialized. Collection: {collection_name}")
            logger.info(f"Current document count: {self.collection.count()}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents with embeddings to the database.
        
        Args:
            documents: List of text chunks
            embeddings: List of embedding vectors
            metadatas: List of metadata dicts for each document
            ids: Optional list of IDs (auto-generated if None)
            
        Returns:
            List of document IDs
        """
        
        try:
            # Generate IDs if not provided
            if ids is None:
                ids = [str(uuid.uuid4()) for _ in range(len(documents))]
            
            # Add timestamp to metadata
            for metadata in metadatas:
                if 'timestamp' not in metadata:
                    metadata['timestamp'] = datetime.now().isoformat()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to ChromaDB")
            
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Query the database for similar documents.
        
        Args:
            query_embedding: Query vector
            n_results: Number of results to return
            where: Filter on metadata (e.g., {"document_id": "doc_123"})
            where_document: Filter on document content
            
        Returns:
            Dict with 'ids', 'documents', 'metadatas', 'distances'
        """
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            
            # Flatten results (query returns list of lists)
            flattened_results = {
                'ids': results['ids'][0] if results['ids'] else [],
                'documents': results['documents'][0] if results['documents'] else [],
                'metadatas': results['metadatas'][0] if results['metadatas'] else [],
                'distances': results['distances'][0] if results['distances'] else []
            }
            
            logger.info(f"Query returned {len(flattened_results['ids'])} results")
            
            return flattened_results
            
        except Exception as e:
            logger.error(f"Error querying database: {str(e)}")
            raise
    
    def get_by_document_id(self, document_id: str) -> Dict:
        """
        Get all chunks for a specific document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Dict with document chunks and metadata
        """
        
        try:
            # Query with metadata filter
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            logger.info(f"Retrieved {len(results['ids'])} chunks for document {document_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving document: {str(e)}")
            raise
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks for a specific document.
        
        Args:
            document_id: Document identifier
            
        Returns:
            Number of chunks deleted
        """
        
        try:
            # Get all IDs for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            chunk_ids = results['ids']
            
            if chunk_ids:
                # Delete by IDs
                self.collection.delete(ids=chunk_ids)
                logger.info(f"Deleted {len(chunk_ids)} chunks for document {document_id}")
            else:
                logger.info(f"No chunks found for document {document_id}")
            
            return len(chunk_ids)
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            raise
    
    def get_all_documents(self) -> List[Dict]:
        """
        Get metadata for all documents in the database.
        
        Returns:
            List of unique documents with their metadata
        """
        
        try:
            # Get all items
            all_items = self.collection.get()
            
            # Extract unique documents
            documents = {}
            
            for metadata in all_items['metadatas']:
                doc_id = metadata.get('document_id')
                
                if doc_id and doc_id not in documents:
                    documents[doc_id] = {
                        'document_id': doc_id,
                        'filename': metadata.get('filename', 'Unknown'),
                        'upload_date': metadata.get('timestamp', 'Unknown'),
                        'file_size': metadata.get('file_size', 0),
                        'page_count': metadata.get('page_count', 0)
                    }
            
            document_list = list(documents.values())
            
            logger.info(f"Retrieved {len(document_list)} unique documents")
            
            return document_list
            
        except Exception as e:
            logger.error(f"Error retrieving all documents: {str(e)}")
            raise
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dict with stats
        """
        
        try:
            total_chunks = self.collection.count()
            all_docs = self.get_all_documents()
            
            stats = {
                'total_chunks': total_chunks,
                'total_documents': len(all_docs),
                'collection_name': self.collection_name,
                'persist_directory': self.persist_directory
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
    
    def clear_collection(self) -> bool:
        """
        Clear all data from the collection.
        
        WARNING: This deletes everything!
        
        Returns:
            True if successful
        """
        
        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate empty collection
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Document chunks for RAG"}
            )
            
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
    
    def search_similar_chunks(
        self,
        query_embedding: List[float],
        document_ids: Optional[List[str]] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Search for similar chunks with detailed information.
        
        Args:
            query_embedding: Query vector
            document_ids: Optional list of document IDs to search within
            top_k: Number of results to return
            
        Returns:
            List of dicts with chunk info and similarity scores
        """
        
        try:
            # Build where filter if document_ids provided
            where = None
            if document_ids:
                if len(document_ids) == 1:
                    where = {"document_id": document_ids[0]}
                else:
                    # ChromaDB $in operator for multiple values
                    where = {"document_id": {"$in": document_ids}}
            
            # Query database
            results = self.query(
                query_embedding=query_embedding,
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = []
            
            for i in range(len(results['ids'])):
                # Convert distance to similarity score (1 - distance)
                # ChromaDB returns L2 distance, lower is better
                distance = results['distances'][i]
                similarity = 1 / (1 + distance)  # Convert to 0-1 similarity
                
                result = {
                    'chunk_id': results['ids'][i],
                    'text': results['documents'][i],
                    'metadata': results['metadatas'][i],
                    'similarity_score': similarity,
                    'distance': distance
                }
                
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching chunks: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test if ChromaDB is working.
        
        Returns:
            True if working, False otherwise
        """
        try:
            # Try to get collection count
            count = self.collection.count()
            logger.info(f"ChromaDB connection successful. Documents: {count}")
            return True
            
        except Exception as e:
            logger.error(f"ChromaDB connection test failed: {str(e)}")
            return False


# Singleton instance
_chroma_db_instance = None


def get_chroma_db() -> ChromaDBHandler:
    """
    Get singleton instance of ChromaDBHandler.
    
    Returns:
        ChromaDBHandler instance
    """
    global _chroma_db_instance
    
    if _chroma_db_instance is None:
        _chroma_db_instance = ChromaDBHandler()
    
    return _chroma_db_instance


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing ChromaDB Handler...")
    
    try:
        # Initialize
        db = ChromaDBHandler()
        
        # Test connection
        if db.test_connection():
            print("✅ ChromaDB connection successful!")
        
        # Test adding documents
        print("\n1️⃣ Testing document addition...")
        
        test_docs = [
            "Python is a high-level programming language.",
            "Machine learning is transforming technology.",
            "Data science combines statistics and programming."
        ]
        
        # Mock embeddings (in real use, these come from EmbeddingService)
        test_embeddings = [[0.1] * 384 for _ in test_docs]
        
        test_metadata = [
            {"document_id": "test_doc_1", "filename": "test.pdf", "page": 1},
            {"document_id": "test_doc_1", "filename": "test.pdf", "page": 2},
            {"document_id": "test_doc_1", "filename": "test.pdf", "page": 3}
        ]
        
        ids = db.add_documents(
            documents=test_docs,
            embeddings=test_embeddings,
            metadatas=test_metadata
        )
        
        print(f"✅ Added {len(ids)} documents")
        
        # Test query
        print("\n2️⃣ Testing query...")
        query_embedding = [0.1] * 384
        
        results = db.query(query_embedding, n_results=2)
        print(f"✅ Query returned {len(results['ids'])} results")
        
        # Get stats
        print("\n3️⃣ Getting stats...")
        stats = db.get_stats()
        print(f"✅ Total chunks: {stats['total_chunks']}")
        print(f"   Total documents: {stats['total_documents']}")
        
        print("\n✅ All tests passed!")
        
        # Optional: Clear test data
        # db.clear_collection()
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")