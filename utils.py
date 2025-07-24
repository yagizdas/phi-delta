import uuid
from datetime import datetime

from config import MAIN_PATH, SESSION_BASED_PATHING
import os

def extract_tool_names(conversation:dict) -> list[str]:
    """
    Extracts tool names from a conversation dictionary.
    """
    tool_names = set()
    for msg in conversation.get('messages', []):
        calls = []
        if hasattr(msg, 'tool_calls'):
            calls = msg.tool_calls or []
        elif isinstance(msg,dict):
            calls = msg.get('tool_calls') or []
            if not calls and isinstance(msg.get('additional_kwargs'), dict):
                calls = msg['additional_kwargs'].get('tool_calls', [])
        else:
            ak = getattr(msg, 'additional_kwargs', None)
            if isinstance(ak, dict):
                calls = ak.get('tool_calls', [])
        for call in calls:
            if isinstance(call, dict):
                if 'name' in call:
                    tool_names.add(call['name'])
                elif 'function' in call and isinstance(call['function'], dict):
                    fn = call['function']
                    if 'name' in fn:
                        tool_names.add(fn['name'])
    return sorted(tool_names)


def create_session_id() -> str:
    """
    Creates a unique session ID based on the current timestamp and a random UUID.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_id = uuid.uuid4().hex[:2]  # Short random string
    return f"{timestamp}_{random_id}"

def create_session_directory(session_id: str, 
                          pdfs_path: str = MAIN_PATH) -> str:
    """
    Creates a session-specific directory for storing files.
    """
    if session_id is None:
        # Generate a unique session ID using timestamp and UUID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_id = uuid.uuid4().hex[:2]  # Short random string
        session_id = f"{timestamp}_{random_id}"

    session_path = os.path.join(pdfs_path, SESSION_BASED_PATHING.format(session_id=session_id))
    
    if not os.path.exists(session_path):
        os.makedirs(session_path)
    
    return session_path

def get_user_prompts(conversation: list[dict]) -> list[dict]:
    """
    Extracts user prompts from a conversation dictionary.
    """
    user_messages = [entry for entry in conversation if entry.get("role") == "user"]

    return user_messages