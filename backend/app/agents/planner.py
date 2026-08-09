"""LangGraph 规划智能体：LLM → 工具 → LLM → 结束"""

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT
from app.tools.amap import AMAP_TOOLS
from app.core.config import settings


def _build_llm() -> ChatOpenAI:
    """根据当前用户配置构建 LLM 实例"""
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=0.7,
    )


def create_planner_agent():
    """创建规划智能体（每次请求新建，使用最新的 LLM 配置）"""
    llm = _build_llm()
    llm_with_tools = llm.bind_tools(AMAP_TOOLS)

    def planner_node(state: AgentState) -> dict:
        """LLM 节点：调用模型，可能产出工具调用或最终回复"""
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(AMAP_TOOLS)

    def should_continue(state: AgentState) -> str:
        """判断下一步：有工具调用 → 执行工具，否则结束"""
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("tools", tool_node)

    graph.add_edge("__start__", "planner")
    graph.add_conditional_edges("planner", should_continue, {"tools": "tools", "__end__": END})
    graph.add_edge("tools", "planner")

    return graph.compile()


def build_initial_state(city: str, days: int, budget: float, interests: str) -> dict:
    """构造智能体的初始状态"""
    user_message = f"请为我规划{city}{days}日游行程。预算{budget}元，兴趣偏好：{interests}。"
    return {
        "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_message)],
        "city": city,
        "days": days,
        "budget": budget,
        "interests": interests,
    }
