"""LangGraph 规划智能体：LLM → 工具 → LLM → 结束"""

import json
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


# ── SSE 辅助函数 ──

def _sse_event(event_type: str, data: dict) -> str:
    """构造一条 SSE 事件字符串"""
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


# ── 流式执行器 ──

async def run_agent_stream(state: dict):
    """流式执行 Agent，通过 SSE 事件推送实时进度与最终结果。

    阶段判断：
    - analyzing：on_chat_model_start 且尚未见过工具调用
    - searching_poi：on_tool_start 且工具名含 search / geocode
    - routing：on_tool_start 且工具名含 route
    - generating_plan：on_chat_model_start 且已见过工具调用
    - done：on_chat_model_end 且无 tool_calls 且已见过工具调用
    """
    from app.api.planning import _extract_json, _parse_itinerary

    agent = create_planner_agent()
    has_called_tools = False

    yield _sse_event("phase", {"phase": "analyzing", "message": "正在分析需求…", "progress": 10})

    try:
        async for event in agent.astream_events(state, version="v2"):
            kind = event["event"]

            if kind == "on_chat_model_start":
                if has_called_tools:
                    yield _sse_event("phase", {"phase": "generating_plan", "message": "正在生成旅行计划…", "progress": 70})

            elif kind == "on_tool_start":
                name = event.get("name", "")
                if "route" in name.lower():
                    yield _sse_event("phase", {"phase": "routing", "message": "正在计算路线…", "progress": 50})
                else:
                    yield _sse_event("phase", {"phase": "searching_poi", "message": "正在搜索景点…", "progress": 30})
                has_called_tools = True

            elif kind == "on_chat_model_end":
                output = event["data"]["output"]
                if has_called_tools and not (hasattr(output, "tool_calls") and output.tool_calls):
                    content = output.content if hasattr(output, "content") else str(output)
                    raw = _extract_json(content)
                    itinerary = _parse_itinerary(raw)
                    result = {
                        "destination": raw.get("destination", state.get("city", "")),
                        "days": raw.get("days", state.get("days", 0)),
                        "itinerary": [d.model_dump() for d in itinerary],
                    }
                    yield _sse_event("result", result)

    except Exception as e:
        yield _sse_event("error", {"message": f"规划失败：{str(e)}"})
