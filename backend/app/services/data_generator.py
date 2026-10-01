"""
Seed a realistic enterprise context graph:
- 40 business entities (customers, products, orders)
- 15 process steps (approvals, workflows)
- 20 rules (compliance, business logic)
- 6 roles
- Edges connecting them
"""
import random
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.graph_node import GraphNode
from ..models.graph_edge import GraphEdge


CUSTOMERS = ["Acme Corp", "Globex", "Initech", "Soylent Inc", "Umbrella Corp", "Stark Industries",
             "Wayne Enterprises", "Cyberdyne", "Massive Dynamic", "Hooli"]
PRODUCTS = ["Widget Pro", "Gadget X", "Service Basic", "Service Enterprise", "Bundle A",
            "Bundle B", "Add-on Plus", "License Pro", "Support Plus", "Training Pack"]
PROCESSES = ["Order Approval", "Refund Processing", "Customer Onboarding",
             "Invoice Generation", "Contract Review", "Escalation Path",
             "Inventory Reorder", "Payment Reconciliation"]
RULES = [
    "Orders above 10,000 require VP approval",
    "Refunds above 5,000 require manager review",
    "New customers require KYC verification",
    "Enterprise contracts require legal review",
    "Data export requires data governance approval",
    "PII access requires explicit role permission",
]
ROLES = ["admin", "manager", "analyst", "viewer"]


def ensure_seed_data(db: Session) -> None:
    if db.query(GraphNode).count() > 0:
        return
    
    now = datetime.utcnow()
    nodes = []
    
    # Business entities
    for i, c in enumerate(CUSTOMERS):
        n = GraphNode(
            node_type="business_entity",
            label=f"Customer: {c}",
            properties={"kind": "customer", "tier": random.choice(["gold", "silver", "bronze"])},
            confidence=1.0,
            source="CRM",
            valid_from=now - timedelta(days=random.randint(30, 500)),
        )
        db.add(n); nodes.append(n)
    
    for p in PRODUCTS:
        n = GraphNode(
            node_type="business_entity",
            label=f"Product: {p}",
            properties={"kind": "product", "price": random.randint(100, 5000)},
            confidence=1.0,
            source="Catalog",
            valid_from=now - timedelta(days=random.randint(30, 900)),
        )
        db.add(n); nodes.append(n)
    
    # Process steps
    for p in PROCESSES:
        n = GraphNode(
            node_type="process_step",
            label=f"Process: {p}",
            properties={"kind": "workflow", "sla_hours": random.choice([4, 24, 48, 72])},
            confidence=0.95,
            source="Process KB",
        )
        db.add(n); nodes.append(n)
    
    # Rules
    for r in RULES:
        n = GraphNode(
            node_type="rule",
            label=f"Rule: {r}",
            properties={"kind": "policy", "enforced": True},
            confidence=1.0,
            source="Policy Manual v3.2",
        )
        db.add(n); nodes.append(n)
    
    # Roles (restricted to admins only)
    for r in ROLES:
        n = GraphNode(
            node_type="role",
            label=f"Role: {r}",
            properties={"kind": "access_role"},
            confidence=1.0,
            source="IAM",
            required_role="admin",
        )
        db.add(n); nodes.append(n)
    
    db.commit()
    
    # Edges
    entity_nodes = [n for n in nodes if n.node_type == "business_entity"]
    process_nodes = [n for n in nodes if n.node_type == "process_step"]
    rule_nodes = [n for n in nodes if n.node_type == "rule"]
    
    edges = []
    for pn in process_nodes:
        # Each process CONTAINS a random rule
        rn = random.choice(rule_nodes)
        edges.append(GraphEdge(source_id=pn.id, target_id=rn.id, edge_type="CONTAINS", confidence=0.9))
    
    for en in entity_nodes:
        # Each entity DEPENDS_ON a random process
        pn = random.choice(process_nodes)
        edges.append(GraphEdge(source_id=en.id, target_id=pn.id, edge_type="DEPENDS_ON", confidence=0.85))
    
    for _ in range(20):
        a = random.choice(rule_nodes)
        b = random.choice(rule_nodes)
        if a.id != b.id:
            edges.append(GraphEdge(source_id=a.id, target_id=b.id, edge_type="SUPERSEDES", confidence=0.6))
    
    for e in edges:
        db.add(e)
    db.commit()
