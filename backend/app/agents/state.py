"""LangGraph Agent state definition"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Planner agent shared state"""
    messages: Annotated[list, add_messages]
    city: str
    days: int
    budget: float
    interests: str
    visitor_id: str