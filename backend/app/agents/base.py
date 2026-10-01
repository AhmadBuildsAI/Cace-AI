"""Base agent class with common helpers."""
import time
import json
from typing import Dict, Any
from ..core.llm_client import llm_client


class BaseAgent:
    name = "base"
    system_prompt = "You are a helpful AI agent."
    
    def __init__(self, db=None):
        self.db = db
    
    def run(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError
    
    def call_llm(self, user_prompt: str, json_mode: bool = True) -> Dict:
        raw = llm_client.chat_json(self.system_prompt, user_prompt) if json_mode else {"text": llm_client.chat(self.system_prompt, user_prompt)}
        return raw
