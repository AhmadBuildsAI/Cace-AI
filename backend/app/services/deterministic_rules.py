"""
Deterministic business rules layer.
Runs alongside the LLM-based validation for compliance-grade checks.
"""
from typing import List
from sqlalchemy.orm import Session
from ..models.graph_node import GraphNode


# Hardcoded demo rules
RULES = [
    {
        "id": "R1",
        "name": "High-value order approval",
        "description": "Orders above 10,000 require VP approval.",
        "check": lambda q, a, role, db: (
            "order" in q.lower() and any(n in a.lower() for n in ["10,000", "10000"])
            and role not in ("admin", "manager")
            and "vp" not in a.lower() and "approval" not in a.lower()
        ),
        "message": "Answer mentions high-value order but doesn't cite VP approval requirement.",
    },
    {
        "id": "R2",
        "name": "Role-based data access",
        "description": "Viewers cannot access financial figures.",
        "check": lambda q, a, role, db: (
            role == "viewer"
            and any(w in a.lower() for w in ["revenue", "profit", "cost", "$", "salary"])
        ),
        "message": "Viewer role attempted to access financial data.",
    },
    {
        "id": "R3",
        "name": "Customer PII redaction",
        "description": "Customer email/phone should not appear in answers for non-admin roles.",
        "check": lambda q, a, role, db: (
            role != "admin"
            and ("@" in a and ".com" in a)
        ),
        "message": "Answer contains what appears to be PII (email) for non-admin role.",
    },
]


def check_rules(query: str, answer: str, db: Session, user_role: str) -> List[str]:
    """Return list of violation messages."""
    violations = []
    for rule in RULES:
        try:
            if rule["check"](query, answer, user_role, db):
                violations.append(f"[{rule['id']}] {rule['message']}")
        except Exception:
            pass
    return violations
