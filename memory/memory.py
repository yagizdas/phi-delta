from typing import List, Dict, Optional
from parsers import parse_agent
import re

class AgentMemory:
    
    def __init__(self):
        self.arxiv_links: List[str] = []
        self.chat_history: List[Dict] = []
        self.chat_summary: str = ""
        self.step_history: List[Dict] = []

    def add(self, role: str, content: str):
        self.chat_history.append({"role": role, "content": content})

    def get_last_messages(self, n: int = 5, role_filter: Optional[str] = None) -> List[str]:
        messages = self.chat_history
        if role_filter:
            messages = [m for m in messages if m["role"] == role_filter]
        return [m["content"] for m in messages[-n:]]


    def get_summaries(self, n: int = 5) -> List[str]:
        summaries = []

        for m in self.chat_history:

            if m["role"] == "user":
                summaries.append(m["content"])

            if m["role"] == "system" and "Summary:" in m["content"]:
                summary, _ = parse_agent(m["content"])  # use your existing parser
                summaries.append(summary)

        edited_summaries = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in memory.chat_history])

        return edited_summaries


    def get_user_query(self) -> Optional[str]:
        for m in reversed(self.chat_history):
            if m["role"] == "user":
                return m["content"]
        return None   
    
    def clear(self):
        self.chat_history = []
        self.arxiv_links = []


