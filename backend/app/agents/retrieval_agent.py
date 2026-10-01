"""
Retrieval Agent — fetches relevant context from the CKG.
Combines deterministic keyword matching with LLM-based ranking.
"""
import time
from typing import Dict, List
from sqlalchemy.orm import Session
from .base import BaseAgent
from ..models.graph_node import GraphNode
from ..models.graph_edge import GraphEdge


class RetrievalAgent(BaseAgent):
    name = "retrieval"
    system_prompt = """You are a Context Retrieval Agent for an enterprise AI system.
Given a user query and a list of candidate context nodes, rank and select the most relevant ones.

Return STRICT JSON:
{
  "context_node_ids": ["id1", "id2", ...],
  "reasoning": "why these nodes are relevant"
}

Select at most 10 nodes. Prefer specificity over quantity."""
    
    def run(self, query: str, user_role: str, db: Session, max_nodes: int = 15) -> Dict:
        start = time.time()
        
        # 1. Deterministic candidate selection: keyword overlap
        q_lower = query.lower()
        tokens = set(t for t in q_lower.split() if len(t) > 3)
        
        candidates = db.query(GraphNode).limit(200).all()
        
        scored: List = []
        for node in candidates:
            # Role filter
            if node.required_role and node.required_role != user_role and user_role != "admin":
                continue
            
            label_lower = (node.label or "").lower()
            props_str = str(node.properties or {}).lower()
            
            score = 0.0
            for tok in tokens:
                if tok in label_lower:
                    score += 0.4
                if tok in props_str:
                    score += 0.15
            
            # Boost by confidence
            score += node.confidence * 0.2
            
            if score > 0:
                scored.append((score, node))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:max_nodes]
        
        # 2. LLM reranking (if candidates exist and LLM configured)
        top_ids = [str(n.id) for _, n in top]
        if top and len(top) > 3:
            node_summaries = "\n".join(
                f"- {n.id}: [{n.node_type}] {n.label}" for _, n in top[:20]
            )
            user_prompt = f"Query: {query}\n\nCandidates:\n{node_summaries}\n\nSelect most relevant IDs."
            llm_result = self.call_llm(user_prompt, json_mode=True)
            llm_ids = llm_result.get("context_node_ids", [])
            if llm_ids:
                top_ids = [i for i in llm_ids if i in top_ids][:10]
        
        # 3. Fetch final context items
        context_items = []
        for nid in top_ids:
            node = next((n for _, n in top if str(n.id) == nid), None)
            if node:
                context_items.append({
                    "node_id": str(node.id),
                    "label": node.label,
                    "node_type": node.node_type,
                    "properties": node.properties,
                    "confidence": node.confidence,
                    "source": node.source,
                })
        
        latency = (time.time() - start) * 1000
        return {
            "context_items": context_items,
            "reasoning": f"Selected {len(context_items)} nodes via keyword + LLM reranking",
            "latency_ms": latency,
        }
