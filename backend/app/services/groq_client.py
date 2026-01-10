"""
Groq API Client
Handles all interactions with Groq's LLM API

"""

import os
from typing import List, Dict, Optional
from groq import Groq
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroqClient:
    """
    Client for interacting with Groq API.
    
    Handles:
    - Chat completions with context
    - Streaming responses (for future real-time chat)
    - Error handling and retries
    - Token management
    """
    
    def __init__(self):
        """Initialize Groq client with API key from environment."""
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        
        # Model configuration from .env or defaults
        self.model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
        
        logger.info(f"GroqClient initialized with model: {self.model}")
    
    def generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate an answer using RAG context.
        
        Args:
            question: User's question
            context: Retrieved context from documents
            conversation_history: Previous messages for context
            
        Returns:
            Generated answer string
        """
        
        # Build the system prompt for RAG
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

IMPORTANT RULES:
1. Answer ONLY based on the context provided
2. If the context doesn't contain the answer, say "I cannot find this information in the provided documents"
3. Be concise but comprehensive
4. Cite specific parts of the context when relevant
5. If you're uncertain, express your uncertainty
6. Use a professional but friendly tone

Context from documents:
{context}

Remember: Only use information from the context above. Do not use your general knowledge."""
        
        # Format the system prompt with context
        formatted_system_prompt = system_prompt.format(context=context)
        
        # Build messages array
        messages = [
            {"role": "system", "content": formatted_system_prompt}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False  # Set to True for streaming in future
            )
            
            # Extract answer
            answer = response.choices[0].message.content
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise Exception(f"Failed to generate answer: {str(e)}")
    
    def generate_streaming_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ):
        """
        Generate streaming answer (for real-time responses).
        
        This will be useful when we add WebSocket support!
        
        Args:
            question: User's question
            context: Retrieved context
            conversation_history: Previous messages
            
        Yields:
            Chunks of the generated answer
        """
        
        system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

IMPORTANT RULES:
1. Answer ONLY based on the context provided
2. If the context doesn't contain the answer, say "I cannot find this information in the provided documents"
3. Be concise but comprehensive
4. Cite specific parts of the context when relevant

Context from documents:
{context}"""
        
        formatted_system_prompt = system_prompt.format(context=context)
        
        messages = [
            {"role": "system", "content": formatted_system_prompt}
        ]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": question})
        
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            raise Exception(f"Streaming failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test if Groq API is accessible.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            logger.info("Groq API connection successful")
            return True
            
        except Exception as e:
            logger.error(f"Groq API connection failed: {str(e)}")
            return False
    
    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of document text.
        
        Useful for creating document previews.
        
        Args:
            text: Full document text
            max_length: Maximum summary length in words
            
        Returns:
            Summary string
        """
        
        prompt = f"""Summarize the following text in approximately {max_length} words. 
Be concise and capture the main points.

Text:
{text[:4000]}  # Limit input to avoid token limits

Summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for summaries
                max_tokens=300
            )
            
            summary = response.choices[0].message.content
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed"


# Example usage and testing
if __name__ == "__main__":
    # Test the Groq client
    try:
        client = GroqClient()
        
        # Test connection
        if client.test_connection():
            print("✅ Groq API connection successful!")
            
            # Test answer generation
            test_context = """
            The Python programming language was created by Guido van Rossum.
            It was first released in 1991. Python emphasizes code readability
            and uses significant whitespace.
            """
            
            test_question = "Who created Python and when?"
            
            answer = client.generate_answer(
                question=test_question,
                context=test_context
            )
            
            print(f"\nQuestion: {test_question}")
            print(f"Answer: {answer}")
        else:
            print("❌ Groq API connection failed!")
            
    except Exception as e:
        print(f"Error: {str(e)}")