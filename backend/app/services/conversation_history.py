"""
Conversation history manager for tracking user interactions
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

CONTEXT_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "context_database.json")

def load_database() -> Dict[str, Any]:
    """Load the entire database"""
    try:
        with open(CONTEXT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading database: {e}")
        return {}

def save_database(data: Dict[str, Any]) -> bool:
    """Save the entire database"""
    try:
        with open(CONTEXT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def add_message_to_history(client_id: UUID, user_message: str, assistant_message: str) -> bool:
    """
    Add a conversation exchange to the history

    Args:
        client_id: UUID of the client
        user_message: What the user said
        assistant_message: What the assistant responded

    Returns:
        True if successful, False otherwise
    """
    db = load_database()

    if "conversation_history" not in db:
        db["conversation_history"] = {
            "enabled": True,
            "max_messages_per_user": 50,
            "sessions": []
        }

    client_id_str = str(client_id)

    # Find existing session for this client
    session = None
    for s in db["conversation_history"]["sessions"]:
        if s.get("client_id") == client_id_str:
            session = s
            break

    # Create new session if not found
    if not session:
        session = {
            "client_id": client_id_str,
            "started_at": datetime.now().isoformat(),
            "last_interaction": datetime.now().isoformat(),
            "messages": []
        }
        db["conversation_history"]["sessions"].append(session)

    # Add the message exchange
    session["messages"].append({
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "assistant": assistant_message
    })
    session["last_interaction"] = datetime.now().isoformat()

    # Limit the number of messages
    max_messages = db["conversation_history"].get("max_messages_per_user", 50)
    if len(session["messages"]) > max_messages:
        session["messages"] = session["messages"][-max_messages:]

    return save_database(db)

def get_conversation_history(client_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent conversation history for a client

    Args:
        client_id: UUID of the client
        limit: Maximum number of message exchanges to return

    Returns:
        List of message exchanges (user + assistant pairs)
    """
    db = load_database()

    if "conversation_history" not in db:
        return []

    client_id_str = str(client_id)

    # Find session for this client
    for session in db["conversation_history"]["sessions"]:
        if session.get("client_id") == client_id_str:
            messages = session.get("messages", [])
            return messages[-limit:] if limit else messages

    return []

def format_history_for_llm(client_id: UUID, limit: int = 5) -> str:
    """
    Format conversation history as a string for LLM context

    Args:
        client_id: UUID of the client
        limit: Maximum number of exchanges to include

    Returns:
        Formatted conversation history string
    """
    history = get_conversation_history(client_id, limit)

    if not history:
        return ""

    parts = ["EELMINE VESTLUS:"]
    for msg in history:
        parts.append(f"Kasutaja: {msg['user']}")
        parts.append(f"Assistent: {msg['assistant']}")
    parts.append("")

    return "\n".join(parts)

def clear_conversation_history(client_id: UUID) -> bool:
    """
    Clear conversation history for a specific client

    Args:
        client_id: UUID of the client

    Returns:
        True if successful, False otherwise
    """
    db = load_database()

    if "conversation_history" not in db:
        return True

    client_id_str = str(client_id)

    # Remove session for this client
    db["conversation_history"]["sessions"] = [
        s for s in db["conversation_history"]["sessions"]
        if s.get("client_id") != client_id_str
    ]

    return save_database(db)

def get_all_sessions() -> List[Dict[str, Any]]:
    """Get all conversation sessions"""
    db = load_database()
    return db.get("conversation_history", {}).get("sessions", [])

def cleanup_old_sessions(days: int = 30) -> bool:
    """
    Remove sessions older than specified days

    Args:
        days: Number of days to keep

    Returns:
        True if successful, False otherwise
    """
    from datetime import timedelta

    db = load_database()

    if "conversation_history" not in db:
        return True

    cutoff = datetime.now() - timedelta(days=days)

    # Keep only recent sessions
    db["conversation_history"]["sessions"] = [
        s for s in db["conversation_history"]["sessions"]
        if datetime.fromisoformat(s.get("last_interaction", "2000-01-01")) > cutoff
    ]

    return save_database(db)

