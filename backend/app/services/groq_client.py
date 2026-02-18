"""
Groq API Client
Handles all interactions with Groq's LLM API

"""

import os
from typing import Any, Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv
import logging
import time

from .observability_service import get_observability_service

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

    RAG_PROMPT_TEMPLATE_KEY = "rag_qa_system_prompt"

    def __init__(self):
        """Initialize Groq client with API key from environment."""
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=self.api_key)

        # Model configuration from .env or defaults
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "1024"))

        self.observability = get_observability_service()
        self.default_rag_system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

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

        self.observability.ensure_prompt_template(
            template_key=self.RAG_PROMPT_TEMPLATE_KEY,
            template_text=self.default_rag_system_prompt,
            description="Default RAG system prompt template used for question answering.",
        )

        logger.info(f"GroqClient initialized with model: {self.model}")

    def _extract_usage(self, response: Any) -> Dict[str, int]:
        usage = getattr(response, "usage", None)
        if not usage:
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
        completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        total_tokens = int(getattr(usage, "total_tokens", prompt_tokens + completion_tokens) or 0)
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    def _resolve_rag_prompt_template(self) -> Dict[str, Any]:
        prompt_template = self.observability.get_active_prompt_template(self.RAG_PROMPT_TEMPLATE_KEY)
        if not prompt_template:
            prompt_template = self.observability.ensure_prompt_template(
                template_key=self.RAG_PROMPT_TEMPLATE_KEY,
                template_text=self.default_rag_system_prompt,
                description="Default RAG system prompt template used for question answering.",
            )
        return {
            "template_key": prompt_template.template_key,
            "version": prompt_template.version,
            "template_text": prompt_template.template_text,
        }

    def generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        conversation_id: Optional[str] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate an answer using RAG context and capture observability metrics.

        Returns:
            Dict with answer + token/cost/latency metadata
        """

        prompt_info = self._resolve_rag_prompt_template()
        formatted_system_prompt = prompt_info["template_text"].format(context=context)

        messages = [{"role": "system", "content": formatted_system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": question})

        started_at = time.perf_counter()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1,
                stream=False,
            )

            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            usage = self._extract_usage(response)
            answer = response.choices[0].message.content
            cost_usd = self.observability.calculate_cost_usd(
                usage["prompt_tokens"],
                usage["completion_tokens"],
            )

            metadata = {
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "history_messages": len(conversation_history or []),
                "context_length": len(context),
            }
            if request_metadata:
                metadata.update(request_metadata)

            self.observability.log_llm_request(
                request_type="rag_answer",
                model=self.model,
                question=question,
                conversation_id=conversation_id,
                prompt_input=formatted_system_prompt,
                prompt_template_key=prompt_info["template_key"],
                prompt_template_version=prompt_info["version"],
                response_text=answer,
                request_metadata=metadata,
                prompt_tokens=usage["prompt_tokens"],
                completion_tokens=usage["completion_tokens"],
                latency_ms=latency_ms,
                success=True,
            )

            logger.info(
                "Generated answer | latency_ms=%s prompt_tokens=%s completion_tokens=%s cost_usd=%s",
                latency_ms,
                usage["prompt_tokens"],
                usage["completion_tokens"],
                cost_usd,
            )

            return {
                "answer": answer,
                "latency_ms": latency_ms,
                "prompt_tokens": usage["prompt_tokens"],
                "completion_tokens": usage["completion_tokens"],
                "total_tokens": usage["total_tokens"],
                "cost_usd": cost_usd,
                "prompt_template_key": prompt_info["template_key"],
                "prompt_template_version": prompt_info["version"],
            }

        except Exception as e:
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            self.observability.log_llm_request(
                request_type="rag_answer",
                model=self.model,
                question=question,
                conversation_id=conversation_id,
                prompt_input=formatted_system_prompt,
                prompt_template_key=prompt_info["template_key"],
                prompt_template_version=prompt_info["version"],
                response_text=None,
                request_metadata=request_metadata or {},
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=latency_ms,
                success=False,
                error_message=str(e),
            )
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )

            logger.info("Groq API connection successful")
            return bool(response.choices)

        except Exception as e:
            logger.error(f"Groq API connection failed: {str(e)}")
            return False

    def summarize_document(self, text: str, max_length: int = 200) -> str:
        """
        Generate a summary of document text.

        Useful for creating document previews.
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
                temperature=0.3,
                max_tokens=300
            )

            summary = response.choices[0].message.content
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Summary generation failed"
