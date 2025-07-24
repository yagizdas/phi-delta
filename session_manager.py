import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid

from memory.memory import AgentMemory

from config import MAIN_PATH
from utils import create_session_id

import shutil

class SessionManager:
    def __init__(self, sessions_dir: str = "model_files/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, session_path: str, session_id: str, memory: AgentMemory,
                    additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save a chat session to disk
        
        Args:
            session_id: Unique identifier for the session
            memory: AgentMemory instance to save
            additional_data: Any additional data to save with the session
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            session_data = {
                "session_id": session_id,
                "session_path": session_path,
                "timestamp": datetime.now().isoformat(),
                "memory": memory.to_dict(),
                "additional_data": additional_data or {}
            }

            session_file = Path(session_path) / f"{session_id}.json"

            print("Saving session to:", session_file)  # Debug log

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                print("Session saved successfully.")
            return True
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            return False

    def load_session(self, session_path: str, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a chat session from disk
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dict containing session data or None if not found
        """
        try:
            session_file = Path(session_path) / f"{session_id}.json"
            if not session_file.exists():
                return None
                
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                
            # Convert memory dict back to AgentMemory instance
            memory_data = session_data.get("memory", {})
            memory = AgentMemory.from_dict(memory_data)

            print("Session loaded successfully:", session_id)  # Debug log
            print("Loaded Session data:", session_data)  # Debug log
            
            return {
                "session_id": session_data["session_id"],
                "session_path": session_data["session_path"],
                "timestamp": session_data["timestamp"],
                "memory": memory,
                "additional_data": session_data.get("additional_data", {})
            }
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """
        List all available sessions
        
        Returns:
            List of session metadata (id, timestamp, title)
        """
        sessions = []
        try:
            for folders in Path(MAIN_PATH).iterdir():
                for file in folders.iterdir():
                    for session_file in file.glob("*.json"):
                        try:
                            with open(session_file, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                            
                            # Check for AI generated title first
                            session_id = session_data["session_id"]
                            session_path = session_data.get("session_path", file.parent)
                            title_file = Path(session_path) / "utils" / "title.txt"
                            
                            title = "New Chat"  # Default title
                            
                            # Try to read generated title first
                            if title_file.exists():
                                try:
                                    with open(title_file, 'r', encoding='utf-8') as tf:
                                        generated_title = tf.read().strip()
                                        if generated_title:
                                            title = generated_title
                                except Exception as e:
                                    print(f"Error reading title file {title_file}: {e}")
                            
                            # If no generated title, fall back to first user message
                            if title == "New Chat":
                                memory_data = session_data.get("memory", {})
                                chat_history = memory_data.get("chat_history", [])
                                
                                for msg in chat_history:
                                    if msg.get("role") == "user":
                                        content = msg.get("content", "")
                                        title = content[:50] + "..." if len(content) > 50 else content
                                        break
                            
                            sessions.append({
                                "session_id": session_data["session_id"],
                                "timestamp": session_data["timestamp"],
                                "title": title
                            })
                        except Exception as e:
                            print(f"Error reading session file {session_file}: {e}")
                            continue
                        
            # Sort by timestamp (most recent first)
            sessions.sort(key=lambda s: s["timestamp"], reverse=True)
            return sessions
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_path: str, session_id: str) -> bool:
        """
        Delete a session from disk, including all its contents.
        
        Args:
            session_path: Path to the session directory.
            session_id: Unique identifier for the session.
            
        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        try:
            session_dir = Path(session_path)
            print(f"Deleting session {session_id} from path {session_dir}")  # Debug log

            if session_dir.exists() and session_dir.is_dir():
                print(f"Session directory found: {session_dir}")
                shutil.rmtree(session_dir)  # Recursively delete the directory and its contents
                print(f"Session {session_id} deleted successfully.")
                return True
            else:
                print(f"Session directory does not exist: {session_dir}")
                return False
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return create_session_id()

    def cleanup_old_sessions(self, max_sessions: int = 50):
        """
        Keep only the most recent sessions
        
        Args:
            max_sessions: Maximum number of sessions to keep
        """
        try:
            sessions = self.list_sessions()
            if len(sessions) > max_sessions:
                sessions_to_delete = sessions[max_sessions:]
                for session in sessions_to_delete:
                    self.delete_session(session["session_id"])
                print(f"Cleaned up {len(sessions_to_delete)} old sessions")
        except Exception as e:
            print(f"Error during cleanup: {e}")


# Global session manager instance
session_manager = SessionManager()
