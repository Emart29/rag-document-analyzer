"""Database models and helpers for LLM observability data."""

from __future__ import annotations

import os
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker


OBSERVABILITY_DB_URL = os.getenv("OBSERVABILITY_DB_URL", "sqlite:///./observability.db")

engine = create_engine(
    OBSERVABILITY_DB_URL,
    connect_args={"check_same_thread": False} if OBSERVABILITY_DB_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class PromptTemplate(Base):
    """Versioned prompt templates used by the LLM layer."""

    __tablename__ = "prompt_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_key = Column(String(100), index=True, nullable=False)
    version = Column(Integer, nullable=False)
    template_text = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LLMRequestLog(Base):
    """Full request/response log for every LLM invocation."""

    __tablename__ = "llm_request_logs"

    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String(64), nullable=False, index=True)
    conversation_id = Column(String(64), nullable=True, index=True)
    model = Column(String(100), nullable=False)
    question = Column(Text, nullable=True)
    prompt_input = Column(Text, nullable=False)
    prompt_template_key = Column(String(100), nullable=True)
    prompt_template_version = Column(Integer, nullable=True)
    response_text = Column(Text, nullable=True)
    request_metadata = Column(JSON, nullable=True)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, default=0, nullable=False)
    cost_usd = Column(Float, default=0.0, nullable=False)
    latency_ms = Column(Float, default=0.0, nullable=False)
    success = Column(Boolean, default=True, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


def init_observability_db() -> None:
    """Create observability tables if they do not exist."""
    Base.metadata.create_all(bind=engine)

