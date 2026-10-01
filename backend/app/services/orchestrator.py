"""
Orchestrator — runs the 4-agent pipeline:
Security → Retrieval → Reasoning → Validation
Records every step in agent_traces.
"""
import time
import re
from typing import Dict
from sqlalchemy.orm import Session
from ..models.query_log import QueryLog
from ..models.agent_trace import AgentTrace
from ..models.security_event import SecurityEvent
from ..agents.security_agent import SecurityAgent
from ..agents.retrieval_agent import RetrievalAgent
from ..agents.reasoning_agent import ReasoningAgent
from ..agents.validation_agent import ValidationAgent




def _redact_sensitive_output(answer: str, user_role: str) -> str:
    if user_role == "admin":
        return answer
    answer = re.sub(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', '[REDACTED_EMAIL]', answer, flags=re.I)
    answer = re.sub(r'\b(?:\+?\d[\d\s().-]{7,}\d)\b', '[REDACTED_PHONE]', answer)
    return answer


def run_pipeline(db: Session, query: str, user_id: str, user_role: str) -> Dict:
    start = time.time()
    
    # Create query log entry
    count = db.query(QueryLog).count()
    ref = f"Q-{1001 + count}"
    q = QueryLog(
        query_ref=ref,
        user_id=user_id,
        user_role=user_role,
        original_query=query,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    
    steps = []
    
    # STEP 1: Security
    sec = SecurityAgent(db)
    sec_result = sec.run(query, user_role)
    steps.append({
        "step": 1,
        "agent_name": "security",
        "input_summary": f"query ({len(query)} chars)",
        "output": {k: v for k, v in sec_result.items() if k != "latency_ms"},
        "latency_ms": sec_result["latency_ms"],
    })
    
    if sec_result["threat_detected"]:
        db.add(SecurityEvent(
            query_id=q.id,
            user_id=user_id,
            threat_type=sec_result["threat_type"] or "unknown",
            severity=sec_result["severity"] or "MEDIUM",
            confidence=sec_result["confidence"],
            reasoning=sec_result["reasoning"],
            evidence={"evidence": sec_result.get("evidence", [])},
            blocked="true",
        ))
        q.threat_detected = sec_result["threat_type"]
        q.final_answer = "⛔ Request blocked by Security Agent."
        q.confidence = 0.0
        q.validation_passed = "blocked"
        q.latency_ms = (time.time() - start) * 1000
        db.commit()
        
        _persist_traces(db, q.id, steps)
        return _build_response(q, steps, [], [])
    
    q.sanitized_query = sec_result["sanitized_query"]
    db.commit()
    
    # STEP 2: Retrieval
    ret = RetrievalAgent(db)
    ret_result = ret.run(query, user_role, db)
    steps.append({
        "step": 2,
        "agent_name": "retrieval",
        "input_summary": f"query + role={user_role}",
        "output": {
            "context_count": len(ret_result["context_items"]),
            "reasoning": ret_result["reasoning"],
        },
        "latency_ms": ret_result["latency_ms"],
    })
    
    # STEP 3: Reasoning
    rea = ReasoningAgent(db)
    rea_result = rea.run(query, ret_result["context_items"], user_role)
    steps.append({
        "step": 3,
        "agent_name": "reasoning",
        "input_summary": f"{len(ret_result['context_items'])} context nodes",
        "output": {
            "answer": rea_result["answer"][:400],
            "citation_count": len(rea_result["citations"]),
            "confidence": rea_result["confidence"],
            "insufficient_context": rea_result["insufficient_context"],
        },
        "latency_ms": rea_result["latency_ms"],
    })
    
    # STEP 4: Validation
    rea_result["answer"] = _redact_sensitive_output(rea_result["answer"], user_role)
    val = ValidationAgent(db)
    val_result = val.run(
        query, rea_result["answer"], rea_result["citations"],
        ret_result["context_items"], user_role, db,
    )
    steps.append({
        "step": 4,
        "agent_name": "validation",
        "input_summary": f"answer ({len(rea_result['answer'])} chars)",
        "output": {
            "pass": val_result["pass"],
            "issue_count": len(val_result["issues"]),
            "severity": val_result["severity"],
        },
        "latency_ms": val_result["latency_ms"],
    })
    
    # Persist result
    final_answer = val_result.get("corrected_answer") or rea_result["answer"]
    if not val_result["pass"]:
        final_answer = f"⚠️ Validation flagged issues:\n" + "\n".join(f"- {i}" for i in val_result["issues"]) + f"\n\nProposed answer:\n{rea_result['answer']}"
    
    q.final_answer = final_answer
    q.confidence = rea_result["confidence"]
    q.validation_passed = "pass" if val_result["pass"] else "fail"
    q.citations = rea_result["citations"]
    q.context_node_ids = [c["node_id"] for c in ret_result["context_items"]]
    q.latency_ms = (time.time() - start) * 1000
    db.commit()
    
    _persist_traces(db, q.id, steps)
    return _build_response(q, steps, rea_result["citations"], ret_result["context_items"])


def _persist_traces(db: Session, query_id, steps):
    for s in steps:
        db.add(AgentTrace(
            query_id=query_id,
            step=s["step"],
            agent_name=s["agent_name"],
            input_summary=s["input_summary"],
            output_json=s["output"],
            latency_ms=s["latency_ms"],
        ))
    db.commit()


def _build_response(q: QueryLog, steps, citations, context_nodes) -> Dict:
    return {
        "query_id": str(q.id),
        "query_ref": q.query_ref,
        "original_query": q.original_query,
        "sanitized_query": q.sanitized_query,
        "final_answer": q.final_answer,
        "confidence": q.confidence,
        "validation_passed": q.validation_passed,
        "threat_detected": q.threat_detected,
        "citations": citations,
        "context_nodes": context_nodes,
        "agent_steps": steps,
        "latency_ms": q.latency_ms or 0.0,
        "created_at": q.created_at.isoformat(),
    }
