"""Service layer for LLM observability and monitoring."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc, func

from ..database.observability_db import LLMRequestLog, PromptTemplate, SessionLocal

logger = logging.getLogger(__name__)


def _safe_float(value: str, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class ObservabilityService:
    """Handles prompt versioning, logging, and dashboard metric aggregation."""

    def __init__(self):
        self.prompt_token_cost_per_1k = _safe_float(
            os.getenv("GROQ_INPUT_TOKEN_COST_PER_1K", "0.00059"),
            0.00059,
        )
        self.completion_token_cost_per_1k = _safe_float(
            os.getenv("GROQ_OUTPUT_TOKEN_COST_PER_1K", "0.00079"),
            0.00079,
        )

    def ensure_prompt_template(
        self,
        template_key: str,
        template_text: str,
        description: Optional[str] = None,
    ) -> PromptTemplate:
        """Create an initial active version for a prompt template if needed."""
        db = SessionLocal()
        try:
            existing = (
                db.query(PromptTemplate)
                .filter(PromptTemplate.template_key == template_key)
                .order_by(desc(PromptTemplate.version))
                .first()
            )
            if existing:
                return existing

            prompt = PromptTemplate(
                template_key=template_key,
                version=1,
                template_text=template_text,
                description=description,
                is_active=True,
            )
            db.add(prompt)
            db.commit()
            db.refresh(prompt)
            logger.info("Created prompt template '%s' v1", template_key)
            return prompt
        finally:
            db.close()

    def get_active_prompt_template(self, template_key: str) -> Optional[PromptTemplate]:
        """Fetch active prompt version for a given key."""
        db = SessionLocal()
        try:
            return (
                db.query(PromptTemplate)
                .filter(
                    PromptTemplate.template_key == template_key,
                    PromptTemplate.is_active.is_(True),
                )
                .order_by(desc(PromptTemplate.version))
                .first()
            )
        finally:
            db.close()

    def create_prompt_version(
        self,
        template_key: str,
        template_text: str,
        description: Optional[str] = None,
        activate: bool = True,
    ) -> PromptTemplate:
        """Create a new prompt template version for audit/experimentation."""
        db = SessionLocal()
        try:
            latest_version = (
                db.query(func.max(PromptTemplate.version))
                .filter(PromptTemplate.template_key == template_key)
                .scalar()
            ) or 0

            if activate:
                db.query(PromptTemplate).filter(
                    PromptTemplate.template_key == template_key,
                    PromptTemplate.is_active.is_(True),
                ).update({PromptTemplate.is_active: False})

            prompt = PromptTemplate(
                template_key=template_key,
                version=latest_version + 1,
                template_text=template_text,
                description=description,
                is_active=activate,
            )
            db.add(prompt)
            db.commit()
            db.refresh(prompt)
            return prompt
        finally:
            db.close()

    def calculate_cost_usd(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate request cost from configured per-1K token rates."""
        prompt_cost = (prompt_tokens / 1000.0) * self.prompt_token_cost_per_1k
        completion_cost = (completion_tokens / 1000.0) * self.completion_token_cost_per_1k
        return round(prompt_cost + completion_cost, 8)

    def log_llm_request(
        self,
        *,
        request_type: str,
        model: str,
        prompt_input: str,
        response_text: Optional[str],
        question: Optional[str] = None,
        conversation_id: Optional[str] = None,
        prompt_template_key: Optional[str] = None,
        prompt_template_version: Optional[int] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        latency_ms: float = 0.0,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> int:
        """Persist one LLM request log entry."""
        db = SessionLocal()
        try:
            total_tokens = prompt_tokens + completion_tokens
            cost_usd = self.calculate_cost_usd(prompt_tokens, completion_tokens)

            log_entry = LLMRequestLog(
                request_type=request_type,
                conversation_id=conversation_id,
                model=model,
                question=question,
                prompt_input=prompt_input,
                prompt_template_key=prompt_template_key,
                prompt_template_version=prompt_template_version,
                response_text=response_text,
                request_metadata=request_metadata,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                success=success,
                error_message=error_message,
            )
            db.add(log_entry)
            db.commit()
            db.refresh(log_entry)
            return log_entry.id
        finally:
            db.close()

    def get_prompt_templates(self, template_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return prompt template versions."""
        db = SessionLocal()
        try:
            query = db.query(PromptTemplate)
            if template_key:
                query = query.filter(PromptTemplate.template_key == template_key)

            templates = query.order_by(PromptTemplate.template_key, desc(PromptTemplate.version)).all()
            return [
                {
                    "id": item.id,
                    "template_key": item.template_key,
                    "version": item.version,
                    "template_text": item.template_text,
                    "description": item.description,
                    "is_active": item.is_active,
                    "created_at": item.created_at.isoformat(),
                }
                for item in templates
            ]
        finally:
            db.close()

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return most recent request logs."""
        db = SessionLocal()
        try:
            logs = (
                db.query(LLMRequestLog)
                .order_by(desc(LLMRequestLog.created_at))
                .limit(limit)
                .all()
            )
            return [
                {
                    "id": log.id,
                    "request_type": log.request_type,
                    "conversation_id": log.conversation_id,
                    "model": log.model,
                    "question": log.question,
                    "prompt_tokens": log.prompt_tokens,
                    "completion_tokens": log.completion_tokens,
                    "total_tokens": log.total_tokens,
                    "cost_usd": log.cost_usd,
                    "latency_ms": log.latency_ms,
                    "success": log.success,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat(),
                }
                for log in logs
            ]
        finally:
            db.close()

    def get_metrics_summary(self, window_hours: int = 24) -> Dict[str, Any]:
        """Aggregate headline metrics for dashboarding."""
        db = SessionLocal()
        try:
            since = datetime.utcnow() - timedelta(hours=window_hours)
            base = db.query(LLMRequestLog).filter(LLMRequestLog.created_at >= since)

            totals = base.with_entities(
                func.count(LLMRequestLog.id),
                func.coalesce(func.sum(LLMRequestLog.prompt_tokens), 0),
                func.coalesce(func.sum(LLMRequestLog.completion_tokens), 0),
                func.coalesce(func.sum(LLMRequestLog.total_tokens), 0),
                func.coalesce(func.sum(LLMRequestLog.cost_usd), 0.0),
                func.coalesce(func.avg(LLMRequestLog.latency_ms), 0.0),
            ).first()

            success_count = base.filter(LLMRequestLog.success.is_(True)).count()
            failure_count = base.filter(LLMRequestLog.success.is_(False)).count()

            daily_trend_rows = (
                db.query(
                    func.date(LLMRequestLog.created_at).label("date"),
                    func.count(LLMRequestLog.id).label("queries"),
                    func.coalesce(func.sum(LLMRequestLog.total_tokens), 0).label("tokens"),
                    func.coalesce(func.sum(LLMRequestLog.cost_usd), 0.0).label("cost"),
                    func.coalesce(func.avg(LLMRequestLog.latency_ms), 0.0).label("avg_latency"),
                )
                .filter(LLMRequestLog.created_at >= since)
                .group_by(func.date(LLMRequestLog.created_at))
                .order_by(func.date(LLMRequestLog.created_at))
                .all()
            )

            return {
                "window_hours": window_hours,
                "summary": {
                    "total_queries": totals[0] or 0,
                    "prompt_tokens": totals[1] or 0,
                    "completion_tokens": totals[2] or 0,
                    "total_tokens": totals[3] or 0,
                    "total_cost_usd": round(float(totals[4] or 0.0), 8),
                    "average_latency_ms": round(float(totals[5] or 0.0), 2),
                    "success_count": success_count,
                    "failure_count": failure_count,
                },
                "trends": [
                    {
                        "date": str(row.date),
                        "queries": int(row.queries),
                        "tokens": int(row.tokens),
                        "cost_usd": round(float(row.cost), 8),
                        "average_latency_ms": round(float(row.avg_latency), 2),
                    }
                    for row in daily_trend_rows
                ],
            }
        finally:
            db.close()


_observability_service_instance: Optional[ObservabilityService] = None


def get_observability_service() -> ObservabilityService:
    """Get singleton observability service instance."""
    global _observability_service_instance
    if _observability_service_instance is None:
        _observability_service_instance = ObservabilityService()
    return _observability_service_instance
