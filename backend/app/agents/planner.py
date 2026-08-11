"""LangGraph planner agent: LLM -> tools -> LLM -> end"""

import json
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState
from app.agents.prompts import SYSTEM_PROMPT
from app.tools.amap import AMAP_TOOLS
from app.tools.hotel import HOTEL_TOOLS
from app.tools.train import TRAIN_TOOLS
from app.core.config import settings

ALL_TOOLS = AMAP_TOOLS + HOTEL_TOOLS + TRAIN_TOOLS


def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        temperature=0.7,
    )


def create_planner_agent():
    llm = _build_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def planner_node(state: AgentState) -> dict:
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    tool_node = ToolNode(ALL_TOOLS)

    def should_continue(state: AgentState) -> str:
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


def build_initial_state(
    city: str, days: int, budget: float, interests: str, visitor_id: str = ""
) -> dict:
    user_message = (
        f"Please plan a {days}-day trip to {city}. "
        f"Budget: {budget} CNY. Interests: {interests}."
    )
    return {
        "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=user_message)],
        "city": city,
        "days": days,
        "budget": budget,
        "interests": interests,
        "visitor_id": visitor_id,
    }


def _sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def run_agent_stream(state: dict):
    """Stream agent execution via SSE, saving progress to DB."""
    from app.api.planning import _extract_json, _parse_itinerary_days, _parse_hotels, _parse_trains
    from app.core.database import async_session
    from app.repositories.plan_repo import save_plan, update_plan_status
    from app.repositories.event_repo import save_event

    agent = create_planner_agent()
    has_called_tools = False

    visitor_id = state.get("visitor_id", "")
    city = state.get("city", "")
    days = state.get("days", 0)
    budget = state.get("budget", 0)
    interests = state.get("interests", "")

    plan_id = None

    if visitor_id:
        async with async_session() as db:
            plan = await save_plan(db, visitor_id, city, days, budget, interests, "generating")
            plan_id = plan.id
            await save_event(db, plan_id, "analyzing", "Analyzing requirements...")

    yield _sse_event("phase", {"phase": "analyzing", "message": "Analyzing requirements...", "progress": 10})

    try:
        async for event in agent.astream_events(state, version="v2"):
            kind = event["event"]

            if kind == "on_chat_model_start":
                if has_called_tools:
                    if plan_id:
                        async with async_session() as db:
                            await save_event(db, plan_id, "generating_plan", "Generating travel plan...")
                    yield _sse_event("phase", {"phase": "generating_plan", "message": "Generating travel plan...", "progress": 70})

            elif kind == "on_tool_start":
                name = event.get("name", "")
                if name == "search_train":
                    phase, msg, prog = "searching_train", "Searching train tickets...", 40
                elif "route" in name.lower():
                    phase, msg, prog = "routing", "Calculating routes...", 50
                elif name == "search_hotel":
                    phase, msg, prog = "searching_hotel", "Searching hotels...", 35
                else:
                    phase, msg, prog = "searching_poi", "Searching attractions...", 30

                if plan_id:
                    async with async_session() as db:
                        await save_event(db, plan_id, phase, msg)
                yield _sse_event("phase", {"phase": phase, "message": msg, "progress": prog})
                has_called_tools = True

            elif kind == "on_chat_model_end":
                output = event["data"]["output"]
                if has_called_tools and not (hasattr(output, "tool_calls") and output.tool_calls):
                    content = output.content if hasattr(output, "content") else str(output)
                    raw = _extract_json(content)
                    days_plan = _parse_itinerary_days(raw)
                    hotels_data = _parse_hotels(raw)
                    trains_data = _parse_trains(raw)

                    itinerary = {
                        "destination": raw.get("destination", city),
                        "days": raw.get("days", days),
                        "days_plan": [d.model_dump() for d in days_plan],
                        "hotels": hotels_data,
                        "trains": trains_data,
                    }

                    result = {
                        "destination": itinerary["destination"],
                        "days": itinerary["days"],
                        "itinerary": [d.model_dump() for d in days_plan],
                        "days_plan": itinerary["days_plan"],
                        "hotels": itinerary["hotels"],
                        "trains": itinerary["trains"],
                    }

                    if plan_id:
                        async with async_session() as db:
                            await save_event(db, plan_id, "done", "Plan completed")
                            await update_plan_status(db, plan_id, "completed", itinerary)

                    yield _sse_event("result", result)

    except Exception as e:
        if plan_id:
            async with async_session() as db:
                await save_event(db, plan_id, "error", f"Plan failed: {str(e)}")
                await update_plan_status(db, plan_id, "failed")
        yield _sse_event("error", {"message": f"Plan failed: {str(e)}"})