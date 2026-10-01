"""
Multi-provider LLM client using OpenAI SDK.
Supports OpenAI, Google Gemini (OpenAI-compatible endpoint), and DeepSeek.
Falls back to a deterministic mock when no API key is configured.
"""
from openai import OpenAI
from typing import Dict, List, Optional
import json
from .config import settings


PROVIDERS = {
    "openai": {
        "base_url": None,
        "default_model": "gpt-4o-mini",
    },
    "gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-1.5-flash",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "default_model": "deepseek-chat",
    },
}


class LLMClient:
    def __init__(self):
        self.enabled = bool(settings.LLM_API_KEY)
        self.provider = settings.LLM_PROVIDER.lower()
        self.model = settings.LLM_MODEL or PROVIDERS.get(self.provider, {}).get("default_model", "gpt-4o-mini")
        
        if self.enabled:
            cfg = PROVIDERS.get(self.provider)
            if not cfg:
                print(f"⚠️  Unknown provider '{self.provider}'. Falling back to mock.")
                self.enabled = False
                return
            self.client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=cfg["base_url"],
            )
            print(f"✅ LLM ready: provider={self.provider}, model={self.model}")
        else:
            print("⚠️  No LLM_API_KEY configured — using deterministic mock responses.")
    
    def chat(self, system: str, user: str, json_mode: bool = False) -> str:
        """Return raw text response (or JSON string if json_mode=True)."""
        if not self.enabled:
            return self._mock(system, user, json_mode)
        
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": settings.LLM_TEMPERATURE,
                "max_tokens": settings.LLM_MAX_TOKENS,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            resp = self.client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content or ""
        except Exception as e:
            print(f"LLM error: {e}")
            return self._mock(system, user, json_mode)
    
    def chat_json(self, system: str, user: str) -> Dict:
        raw = self.chat(system, user, json_mode=True)
        try:
            return json.loads(raw)
        except Exception:
            # Try to extract JSON substring
            start = raw.find("{")
            end = raw.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(raw[start:end+1])
                except Exception:
                    pass
            return {"error": "json_parse_failed", "raw": raw[:300]}
    
    def _mock(self, system: str, user: str, json_mode: bool) -> str:
        """Deterministic mock so the app runs without an API key."""
        if json_mode:
            if "threat" in system.lower() or "security" in system.lower():
                return json.dumps({
                    "threat_detected": False,
                    "threat_type": None,
                    "severity": None,
                    "reasoning": "mock: no LLM configured",
                })
            if "retrieval" in system.lower():
                return json.dumps({
                    "context_items": [],
                    "reasoning": "mock retrieval — configure LLM_API_KEY for real results",
                })
            if "reasoning" in system.lower():
                return json.dumps({
                    "answer": "Mock answer — configure LLM_API_KEY for real reasoning. Query received: " + user[:120],
                    "citations": [],
                    "confidence": 0.3,
                })
            if "validation" in system.lower():
                return json.dumps({
                    "pass": True,
                    "issues": ["mock validator — no LLM configured"],
                    "corrected_answer": None,
                })
            return json.dumps({"result": "mock"})
        return "Mock LLM response. Set LLM_API_KEY in .env for real answers."


llm_client = LLMClient()
