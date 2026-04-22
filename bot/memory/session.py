# bot/memory/session.py - Conversation memory manager per user.

"""Conversation memory manager per user."""

from collections import deque
from typing import Dict, List, Optional

from bot.config import MAX_HISTORY


class SessionManager:
    """Manages conversation history for multiple users."""

    def __init__(self, max_history: int = MAX_HISTORY):
        self.max_history = max_history
        # Stores conversation context (Ollama's context tokens) per user
        self.contexts: Dict[int, List[int]] = {}
        # Optional: store raw message history for debugging
        self.history: Dict[int, deque] = {}

    def get_context(self, user_id: int) -> Optional[List[int]]:
        """Retrieve stored context for a user."""
        return self.contexts.get(user_id)

    def set_context(self, user_id: int, context: List[int]):
        """Store context for a user."""
        if context:
            self.contexts[user_id] = context

    def reset_context(self, user_id: int):
        """Clear context and history for a user."""
        self.contexts.pop(user_id, None)
        self.history.pop(user_id, None)

    def add_exchange(self, user_id: int, user_message: str, bot_response: str):
        """Add a message exchange to history (optional, for logging)."""
        if user_id not in self.history:
            self.history[user_id] = deque(maxlen=self.max_history)
        self.history[user_id].append({"user": user_message, "bot": bot_response})

    def get_history(self, user_id: int) -> List[Dict]:
        """Retrieve conversation history (for debugging or future features)."""
        if user_id not in self.history:
            return []
        return list(self.history[user_id])
