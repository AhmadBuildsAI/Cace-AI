from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db
from ...models.user import User
from ...models.query_log import QueryLog
from ...models.security_event import SecurityEvent
from ...models.graph_node import GraphNode
from ...api.dependencies.auth import get_current_user
from ...core.config import settings

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    total_queries = db.query(QueryLog).count()
    blocked = db.query(SecurityEvent).count()
    passed = db.query(QueryLog).filter(QueryLog.validation_passed == "pass").count()
    failed = db.query(QueryLog).filter(QueryLog.validation_passed == "fail").count()
    
    avg_confidence = db.query(func.avg(QueryLog.confidence)).scalar() or 0.0
    avg_latency = db.query(func.avg(QueryLog.latency_ms)).scalar() or 0.0
    
    node_count = db.query(GraphNode).count()
    
    recent = db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(5).all()
    
    return {
        "total_queries": total_queries,
        "blocked_queries": blocked,
        "validation_passed": passed,
        "validation_failed": failed,
        "avg_confidence": round(float(avg_confidence), 4),
        "avg_latency_ms": round(float(avg_latency), 2),
        "graph_node_count": node_count,
        "recent_queries": [
            {
                "ref": q.query_ref,
                "snippet": (q.original_query or "")[:80],
                "confidence": q.confidence,
                "validation_passed": q.validation_passed,
                "threat_detected": q.threat_detected,
                "created_at": q.created_at.isoformat(),
            } for q in recent
        ],
    }


@router.get("/model-info")
def model_info(current_user: User = Depends(get_current_user)):
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL or "(provider default)",
        "llm_configured": bool(settings.LLM_API_KEY),
        "agents": [
            {"name": "security", "role": "Detect prompt injection, context bombing, exfiltration"},
            {"name": "retrieval", "role": "Fetch + rank context nodes from CKG"},
            {"name": "reasoning", "role": "Generate answer with citations"},
            {"name": "validation", "role": "Verify answer against CKG facts + rules"},
        ],
        "context_graph": {
            "node_types": ["business_entity", "process_step", "rule", "role",
                           "temporal_marker", "source_provenance", "confidence_score", "relationship"],
            "edge_types": ["DEPENDS_ON", "CONFLICTS_WITH", "SUPERSEDES",
                           "VALIDATES", "TRIGGERS", "CONTAINS"],
        },
        "deterministic_rules_count": 3,
        "limitations": [
            "Scaled-down demo — not production-grade",
            "Deterministic rules are illustrative, not exhaustive",
            "LLM-based validation may miss subtle contradictions",
            "Context graph seed data is synthetic",
        ],
    }
