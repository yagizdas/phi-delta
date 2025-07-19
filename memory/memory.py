from typing import List, Dict, Optional
from parsers import parse_agent
import re

class AgentMemory:
    
    def __init__(self, max_history_length: int = 20):
        self.arxiv_links: List[str] = []
        self.chat_history: List[Dict] = []
        self.chat_summary: str = ""
        self.step_history: List[Dict] = []
        self.thinkingsteps: List[Dict] = []
        self.max_history_length = max_history_length

    def add(self, role: str, content: str):
        self.chat_history.append({"role": role, "content": content})
        self._manage_history_length()
    
    def _manage_history_length(self):
        """Manage chat history length by keeping recent messages and summarizing older ones"""
        if len(self.chat_history) > self.max_history_length:
            # Keep the last 10 messages (5 pairs of user/assistant)
            recent_messages = self.chat_history[-10:]
            
            # The messages to be summarized (everything except recent)
            old_messages = self.chat_history[:-10]
            
            # Only summarize if there are old messages
            if old_messages:
                # Create a summary of old messages
                old_summary = self._create_conversation_summary(old_messages)
                
                # Update the main summary
                if self.chat_summary:
                    self.chat_summary = f"{self.chat_summary}\n\nPrevious conversation: {old_summary}"
                else:
                    self.chat_summary = f"Previous conversation: {old_summary}"
                
                # Keep only recent messages
                self.chat_history = recent_messages
    
    def _create_conversation_summary(self, messages: List[Dict]) -> str:
        """Create a concise summary of conversation messages"""
        if not messages:
            return ""
        
        summary_parts = []
        for i in range(0, len(messages), 2):  # Process in pairs
            if i < len(messages):
                user_msg = messages[i].get('content', '')
                assistant_msg = messages[i + 1].get('content', '') if i + 1 < len(messages) else ''
                
                # Create a brief summary of this exchange
                user_summary = user_msg[:100] + "..." if len(user_msg) > 100 else user_msg
                assistant_summary = assistant_msg[:100] + "..." if len(assistant_msg) > 100 else assistant_msg
                
                summary_parts.append(f"Q: {user_summary} A: {assistant_summary}")
        
        return " | ".join(summary_parts)

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

        edited_summaries = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.chat_history])

        return edited_summaries


    def get_user_query(self) -> Optional[str]:
        for m in reversed(self.chat_history):
            if m["role"] == "user":
                return m["content"]
        return None   
    
    def clear(self):
        self.chat_history = []
        self.arxiv_links = []


