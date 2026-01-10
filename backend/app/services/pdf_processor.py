"""
PDF Processing Module
Handles PDF text extraction and chunking for RAG

Why chunking?
- LLMs have token limits
- Better retrieval accuracy
- Preserves context
"""

import os
from typing import List, Dict, Tuple
import PyPDF2
import pdfplumber
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Processes PDF files for RAG applications.
    
    Features:
    - Text extraction from PDFs
    - Intelligent chunking with overlap
    - Page number tracking
    - Metadata extraction
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize PDF processor.
        
        Args:
            chunk_size: Target size of each text chunk (in characters)
            chunk_overlap: Overlap between chunks (preserves context)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        logger.info(f"PDFProcessor initialized - chunk_size: {chunk_size}, overlap: {chunk_overlap}")
    
    def extract_text_pypdf2(self, pdf_path: str) -> Tuple[str, int]:
        """
        Extract text using PyPDF2 (faster, but less accurate).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, page_count)
        """
        try:
            text = ""
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
            
            logger.info(f"Extracted {len(text)} characters from {page_count} pages using PyPDF2")
            return text, page_count
            
        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            raise
    
    def extract_text_pdfplumber(self, pdf_path: str) -> Tuple[str, int, Dict]:
        """
        Extract text using pdfplumber (more accurate, preserves layout).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, page_count, page_texts_dict)
        """
        try:
            text = ""
            page_texts = {}
            
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text()
                    
                    if page_text:
                        page_texts[i] = page_text
                        text += f"[Page {i}]\n{page_text}\n\n"
            
            logger.info(f"Extracted {len(text)} characters from {page_count} pages using pdfplumber")
            return text, page_count, page_texts
            
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}")
            raise
    
    def extract_text(self, pdf_path: str) -> Tuple[str, int, Dict]:
        """
        Extract text using best available method.
        
        Tries pdfplumber first (better quality), falls back to PyPDF2.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (text, page_count, page_texts)
        """
        try:
            # Try pdfplumber first (better quality)
            return self.extract_text_pdfplumber(pdf_path)
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying PyPDF2: {str(e)}")
            try:
                # Fallback to PyPDF2
                text, page_count = self.extract_text_pypdf2(pdf_path)
                return text, page_count, {}
            except Exception as e2:
                logger.error(f"All extraction methods failed: {str(e2)}")
                raise Exception("Failed to extract text from PDF")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text.
        
        Removes:
        - Extra whitespace
        - Special characters that might cause issues
        - Multiple newlines
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        # Remove multiple newlines (keep max 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove special characters that might cause issues
        text = text.replace('\x00', '')
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(
        self,
        text: str,
        page_texts: Dict[int, str] = None
    ) -> List[Dict]:
        """
        Split text into overlapping chunks.
        
        Why overlap?
        - Preserves context across chunk boundaries
        - Improves retrieval quality
        - Prevents information loss
        
        Args:
            text: Text to chunk
            page_texts: Dict mapping page numbers to text (for page tracking)
            
        Returns:
            List of chunk dictionaries with metadata
        """
        
        # Clean the text first
        text = self.clean_text(text)
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Don't split in middle of word
            if end < len(text):
                # Find next space to avoid splitting words
                while end < len(text) and text[end] not in [' ', '\n', '.', '!', '?']:
                    end += 1
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only add non-empty chunks
                # Try to determine page number from chunk
                page_num = self._get_page_number(chunk_text, page_texts)
                
                chunk = {
                    'id': chunk_id,
                    'text': chunk_text,
                    'start_char': start,
                    'end_char': end,
                    'page_number': page_num,
                    'chunk_length': len(chunk_text)
                }
                
                chunks.append(chunk)
                chunk_id += 1
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap
            
            # Ensure we make progress
            if start <= 0 and end >= len(text):
                break
        
        logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
        return chunks
    
    def _get_page_number(self, chunk_text: str, page_texts: Dict) -> int:
        """
        Try to determine which page a chunk came from.
        
        Args:
            chunk_text: Text of the chunk
            page_texts: Dict mapping page numbers to full page text
            
        Returns:
            Page number (or None if can't determine)
        """
        if not page_texts:
            # Try to extract from [Page X] markers
            match = re.search(r'\[Page (\d+)\]', chunk_text)
            if match:
                return int(match.group(1))
            return None
        
        # Find which page contains this chunk
        for page_num, page_text in page_texts.items():
            if chunk_text[:100] in page_text:  # Check first 100 chars
                return page_num
        
        return None
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Complete PDF processing pipeline.
        
        Steps:
        1. Extract text
        2. Clean text
        3. Create chunks
        4. Return processed data
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with processed data and metadata
        """
        try:
            # Get file info
            file_name = Path(pdf_path).name
            file_size = os.path.getsize(pdf_path)
            
            logger.info(f"Processing PDF: {file_name} ({file_size} bytes)")
            
            # Extract text
            full_text, page_count, page_texts = self.extract_text(pdf_path)
            
            # Create chunks
            chunks = self.chunk_text(full_text, page_texts)
            
            # Prepare result
            result = {
                'filename': file_name,
                'file_size': file_size,
                'page_count': page_count,
                'total_characters': len(full_text),
                'chunk_count': len(chunks),
                'chunks': chunks,
                'full_text': full_text[:1000]  # First 1000 chars for preview
            }
            
            logger.info(f"Successfully processed {file_name}: {page_count} pages, {len(chunks)} chunks")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise Exception(f"PDF processing failed: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Test the PDF processor
    processor = PDFProcessor(chunk_size=500, chunk_overlap=50)
    
    # Create a test text
    test_text = """
    This is a test document about artificial intelligence.
    AI has revolutionized many industries.
    
    Machine learning is a subset of AI that focuses on learning from data.
    Deep learning uses neural networks with multiple layers.
    
    Natural language processing enables computers to understand human language.
    """ * 10  # Repeat to create enough text for chunking
    
    # Test chunking
    chunks = processor.chunk_text(test_text)
    
    print(f"Created {len(chunks)} chunks from test text")
    print(f"\nFirst chunk:")
    print(chunks[0]['text'][:200])
    
    print(f"\nChunk metadata:")
    print(f"- Chunk ID: {chunks[0]['id']}")
    print(f"- Length: {chunks[0]['chunk_length']}")
    print(f"- Start: {chunks[0]['start_char']}, End: {chunks[0]['end_char']}")