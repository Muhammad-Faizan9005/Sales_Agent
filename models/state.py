"""Custom agent state schema."""

from typing import TypedDict, Annotated
from langgraph.graph import add_messages


class GroceryAgentState(TypedDict):
    """Extended state for grocery inventory agent.
    
    This state extends the base agent state with custom fields
    for tracking inventory context and user preferences.
    """
    
    messages: Annotated[list, add_messages]  # Conversation history
    session_id: str  # User session tracking
    user_preferences: dict  # User-specific settings
    pending_orders: list  # Orders awaiting confirmation
    context: dict  # Runtime context (inventory snapshot, etc.)
