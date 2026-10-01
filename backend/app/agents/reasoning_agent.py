"""
Reasoning Agent — generates the answer with mandatory citations.
"""
import time
from typing import Dict, List
from .base import BaseAgent


class ReasoningAgent(BaseAgent):
    name = "reasoning"
    system_prompt = """You are a Reasoning Agent for an enterprise AI system.
Answer the user's question using ONLY the provided context. Never invent facts.

RULES:
1. Every factual claim MUST cite a context node id in the "citations" array.
2. If the context is insufficient, say so and set confidence < 0.5.
3. Do NOT answer questions that require data outside the provided context.
4. Be concise — 2-5 sentences unless the question requires more.

Return STRICT JSON:
{
  "answer": "your answer with citations inline like [1], [2]",
  "citations": [{"node_id": "id", "label": "node label", "quote": "relevant text"}],
  "confidence": 0.0-1.0,
  "insufficient_context": true|false
}"""
    
    def run(self, query: str, context_items: List[Dict], user_role: str) -> Dict:
        start = time.time()
        
        if not context_items:
            return {
                "answer": "I don't have enough context to answer this question.",
                "citations": [],
                "confidence": 0.1,
                "insufficient_context": True,
                "latency_ms": (time.time() - start) * 1000,
            }
        
        ctx_text = "\n".join(
            f"[{i+1}] id={c['node_id']} type={c['node_type']} :: {c['label']} :: {c.get('properties', {})}"
            for i, c in enumerate(context_items)
        )
        
        user_prompt = f"""User role: {user_role}
Query: {query}

Context nodes:
{ctx_text}

Generate your answer with citations."""
        
        result = self.call_llm(user_prompt, json_mode=True)
        
        latency = (time.time() - start) * 1000
        return {
            "answer": result.get("answer", ""),
            "citations": result.get("citations", []),
            "confidence": float(result.get("confidence", 0.5)),
            "insufficient_context": bool(result.get("insufficient_context", False)),
            "latency_ms": latency,
        }
