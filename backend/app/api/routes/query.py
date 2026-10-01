from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.user import User
from ...models.query_log import QueryLog
from ...models.agent_trace import AgentTrace
from ...schemas.query import (
    QueryRequest, QueryResponse, QueryListItem,
    Citation, AgentStep,
)
from ...services.orchestrator import run_pipeline
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/query", tags=["query"])


@router.post("/", response_model=QueryResponse)
def submit_query(
    payload: QueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = run_pipeline(db, payload.query, str(current_user.id), current_user.role)
    return _to_response(result)


@router.get("/", response_model=list[QueryListItem])
def list_queries(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = db.query(QueryLog).filter(
        QueryLog.user_id == current_user.id
    ).order_by(desc(QueryLog.created_at)).limit(limit).all()
    return [
        QueryListItem(
            id=str(r.id),
            query_ref=r.query_ref,
            query_snippet=(r.original_query or "")[:100],
            confidence=r.confidence,
            validation_passed=r.validation_passed,
            threat_detected=r.threat_detected,
            latency_ms=r.latency_ms,
            created_at=r.created_at.isoformat(),
        ) for r in rows
    ]


@router.get("/{query_id}", response_model=QueryResponse)
def get_query(
    query_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(QueryLog).filter(
        QueryLog.id == query_id,
        QueryLog.user_id == current_user.id,
    ).first()
    if not q:
        raise HTTPException(status_code=404, detail="Query not found")
    
    traces = db.query(AgentTrace).filter(
        AgentTrace.query_id == q.id
    ).order_by(AgentTrace.step).all()
    
    steps = [
        {
            "step": t.step,
            "agent_name": t.agent_name,
            "input_summary": t.input_summary or "",
            "output": t.output_json or {},
            "latency_ms": t.latency_ms or 0.0,
        } for t in traces
    ]
    
    return _to_response({
        "query_id": str(q.id),
        "query_ref": q.query_ref,
        "original_query": q.original_query,
        "sanitized_query": q.sanitized_query,
        "final_answer": q.final_answer,
        "confidence": q.confidence,
        "validation_passed": q.validation_passed,
        "threat_detected": q.threat_detected,
        "citations": q.citations or [],
        "context_nodes": [],
        "agent_steps": steps,
        "latency_ms": q.latency_ms or 0.0,
        "created_at": q.created_at.isoformat(),
    })


def _to_response(r: dict) -> QueryResponse:
    return QueryResponse(
        query_id=r["query_id"],
        query_ref=r["query_ref"],
        original_query=r["original_query"],
        sanitized_query=r.get("sanitized_query"),
        final_answer=r.get("final_answer"),
        confidence=r.get("confidence"),
        validation_passed=r.get("validation_passed"),
        threat_detected=r.get("threat_detected"),
        citations=[Citation(**c) for c in r.get("citations", []) if c.get("node_id")],
        context_nodes=r.get("context_nodes", []),
        agent_steps=[AgentStep(**s) for s in r.get("agent_steps", [])],
        latency_ms=r.get("latency_ms", 0.0),
        created_at=r["created_at"],
    )
