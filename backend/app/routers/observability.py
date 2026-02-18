"""Observability routes for logs, metrics and prompt versioning."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from ..models import (
    LLMLogEntry,
    LLMObservabilitySummary,
    PromptTemplateCreate,
    PromptTemplateResponse,
)
from ..services.observability_service import get_observability_service

router = APIRouter(prefix="/observability", tags=["Observability"])


@router.get("/metrics", response_model=LLMObservabilitySummary)
async def get_metrics(window_hours: int = Query(default=24, ge=1, le=720)):
    service = get_observability_service()
    return service.get_metrics_summary(window_hours=window_hours)


@router.get("/logs", response_model=List[LLMLogEntry])
async def get_logs(limit: int = Query(default=50, ge=1, le=500)):
    service = get_observability_service()
    logs = service.get_recent_logs(limit=limit)
    return [
        LLMLogEntry(
            id=entry["id"],
            request_type=entry["request_type"],
            conversation_id=entry.get("conversation_id"),
            model=entry["model"],
            question=entry.get("question"),
            prompt_tokens=entry["prompt_tokens"],
            completion_tokens=entry["completion_tokens"],
            total_tokens=entry["total_tokens"],
            cost_usd=entry["cost_usd"],
            latency_ms=entry["latency_ms"],
            success=entry["success"],
            error_message=entry.get("error_message"),
            created_at=datetime.fromisoformat(entry["created_at"]),
        )
        for entry in logs
    ]


@router.get("/prompts", response_model=List[PromptTemplateResponse])
async def get_prompt_templates(template_key: Optional[str] = None):
    service = get_observability_service()
    templates = service.get_prompt_templates(template_key=template_key)
    return [
        PromptTemplateResponse(
            id=item["id"],
            template_key=item["template_key"],
            version=item["version"],
            template_text=item["template_text"],
            description=item.get("description"),
            is_active=item["is_active"],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in templates
    ]


@router.post("/prompts", response_model=PromptTemplateResponse)
async def create_prompt_template(payload: PromptTemplateCreate):
    service = get_observability_service()
    try:
        created = service.create_prompt_version(
            template_key=payload.template_key,
            template_text=payload.template_text,
            description=payload.description,
            activate=payload.activate,
        )
        return PromptTemplateResponse(
            id=created.id,
            template_key=created.template_key,
            version=created.version,
            template_text=created.template_text,
            description=created.description,
            is_active=created.is_active,
            created_at=created.created_at,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create prompt version: {exc}")
