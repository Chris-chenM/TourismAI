"""LangGraph 智能体状态定义"""

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """规划智能体的共享状态"""
    messages: Annotated[list, add_messages]   # 对话历史（大模型 + 工具消息）
    city: str                                  # 目的地城市
    days: int                                  # 出行天数
    budget: float                              # 预算金额
    interests: str                             # 兴趣偏好
