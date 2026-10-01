"""
Validation Agent — verifies the reasoning agent's output.
Checks: citations validity, contradiction with CKG, rule violations, confidence calibration.
"""
import time
from typing import Dict, List
from sqlalchemy.orm import Session
from .base import BaseAgent
from ..models.graph_node import GraphNode
from ..services.deterministic_rules import check_rules


class ValidationAgent(BaseAgent):
    name = "validation"
    system_prompt = """You are a Validation Agent for an enterprise AI system.
Verify that the proposed answer is consistent with the provided context and rules.

Return STRICT JSON:
{
  "pass": true|false,
  "issues": ["issue 1", "issue 2"],
  "corrected_answer": "if pass=false and a simple correction is possible",
  "severity": "LOW" | "MEDIUM" | "HIGH"
}

Rules:
- Answer must not contradict context facts.
- Every claim should be supported by a citation.
- Confidence must be justified by context quality."""
    
    def run(self, query: str, answer: str, citations: List[Dict],
            context_items: List[Dict], user_role: str, db: Session) -> Dict:
        start = time.time()
        issues = []
        
        # 1. Citation existence check (deterministic)
        context_ids = {c["node_id"] for c in context_items}
        cited_ids = {c.get("node_id") for c in citations}
        orphan_citations = cited_ids - context_ids
        if orphan_citations:
            issues.append(f"Citations reference nodes not in context: {list(orphan_citations)}")
        
        if not citations and len(answer) > 60:
            issues.append("Answer has no citations but makes factual claims.")
        
        # 2. Deterministic rule check
        rule_violations = check_rules(query, answer, db, user_role)
        issues.extend(rule_violations)
        
        # 3. LLM contradiction check (only if LLM available and answer non-trivial)
        llm_pass = True
        llm_corrected = None
        if issues or len(context_items) > 0:
            ctx_text = "\n".join(
                f"- {c['label']} (id={c['node_id']}): {c.get('properties', {})}"
                for c in context_items[:10]
            )
            cit_text = "\n".join(
                f"- {c.get('label','?')} (id={c.get('node_id','?')}): \"{c.get('quote','')}\""
                for c in citations[:10]
            )
            user_prompt = f"""Query: {query}
User role: {user_role}

Context:
{ctx_text}

Proposed answer:
{answer}

Citations:
{cit_text}

Verify consistency. Flag contradictions or unsupported claims."""
            
            llm_result = self.call_llm(user_prompt, json_mode=True)
            if not llm_result.get("pass", True):
                llm_pass = False
                issues.extend(llm_result.get("issues", []))
                llm_corrected = llm_result.get("corrected_answer")
        
        overall_pass = len(issues) == 0 and llm_pass
        latency = (time.time() - start) * 1000
        
        return {
            "pass": overall_pass,
            "issues": issues,
            "corrected_answer": llm_corrected,
            "severity": "HIGH" if len(issues) >= 2 else ("MEDIUM" if issues else "LOW"),
            "latency_ms": latency,
        }
