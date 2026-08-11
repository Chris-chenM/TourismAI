"""Trip planning API"""

import json
import re
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.planner import create_planner_agent, build_initial_state, run_agent_stream
from app.core.database import get_db
from app.repositories import plan_repo, event_repo

router = APIRouter()


class PlanRequest(BaseModel):
    destination: str = Field(..., examples=["Hangzhou"])
    days: int = Field(..., ge=1, le=30, examples=[3])
    budget: float = Field(..., gt=0, examples=[2000])
    interests: str = Field(default="", examples=["history, food"])
    visitor_id: str = Field(default="")


class Activity(BaseModel):
    name: str
    location: str
    longitude: float
    latitude: float
    start_time: str
    duration: int
    transport: str
    description: str = ""


class DayPlan(BaseModel):
    day: int
    activities: list[Activity]


class PlanResponse(BaseModel):
    destination: str
    days: int
    itinerary: list[DayPlan]


class PlanSummary(BaseModel):
    id: str
    destination: str
    days: int
    budget: float
    interests: str
    status: str
    created_at: str


class AgentEventOut(BaseModel):
    id: str
    phase: str
    message: str
    created_at: str


class PlanDetail(BaseModel):
    id: str
    visitor_id: str
    destination: str
    days: int
    budget: float
    interests: str
    status: str
    itinerary: dict | None
    events: list[AgentEventOut]
    created_at: str


@router.post("/api/plan", response_model=PlanResponse)
async def plan_trip(req: PlanRequest):
    try:
        agent = create_planner_agent()
        initial_state = build_initial_state(
            req.destination, req.days, req.budget, req.interests, req.visitor_id
        )

        plan_id = None
        if req.visitor_id:
            async for db in _get_db_session():
                plan = await plan_repo.save_plan(
                    db, req.visitor_id, req.destination, req.days,
                    req.budget, req.interests, "generating"
                )
                plan_id = plan.id

        result = await agent.ainvoke(initial_state)
        last_msg = result["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        raw = _extract_json(content)
        days_plan = _parse_itinerary_days(raw)

        if plan_id:
            itinerary_doc = {
                "destination": raw.get("destination", req.destination),
                "days": raw.get("days", req.days),
                "days_plan": [d.model_dump() for d in days_plan],
                "hotels": _parse_hotels(raw),
                "trains": _parse_trains(raw),
            }
            async for db in _get_db_session():
                await plan_repo.update_plan_status(db, plan_id, "completed", itinerary_doc)

        return PlanResponse(
            destination=raw.get("destination", req.destination),
            days=raw.get("days", req.days),
            itinerary=days_plan,
        )
    except json.JSONDecodeError as e:
        if plan_id:
            async for db in _get_db_session():
                await plan_repo.update_plan_status(db, plan_id, "failed")
        raise HTTPException(status_code=500, detail=f"Invalid JSON from AI: {e}")
    except Exception as e:
        if plan_id:
            async for db in _get_db_session():
                await plan_repo.update_plan_status(db, plan_id, "failed")
        raise HTTPException(status_code=500, detail=f"Plan failed: {e}")


@router.post("/api/plan/stream")
async def plan_trip_stream(req: PlanRequest):
    initial_state = build_initial_state(
        req.destination, req.days, req.budget, req.interests, req.visitor_id
    )

    async def event_generator():
        async for sse_chunk in run_agent_stream(initial_state):
            yield sse_chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/api/plans", response_model=list[PlanSummary])
async def list_plans(visitor_id: str, db: AsyncSession = Depends(get_db)):
    plans = await plan_repo.list_plans(db, visitor_id)
    return [
        PlanSummary(
            id=str(p.id),
            destination=p.destination,
            days=p.days,
            budget=p.budget,
            interests=p.interests,
            status=p.status,
            created_at=p.created_at.isoformat() if p.created_at else "",
        )
        for p in plans
    ]


@router.get("/api/plans/{plan_id}", response_model=PlanDetail)
async def get_plan_detail(plan_id: str, db: AsyncSession = Depends(get_db)):
    try:
        pid = uuid.UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    plan = await plan_repo.get_plan(db, pid)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    events = await event_repo.get_events(db, pid)
    return PlanDetail(
        id=str(plan.id),
        visitor_id=plan.visitor_id,
        destination=plan.destination,
        days=plan.days,
        budget=plan.budget,
        interests=plan.interests,
        status=plan.status,
        itinerary=plan.itinerary,
        events=[
            AgentEventOut(
                id=str(e.id),
                phase=e.phase,
                message=e.message,
                created_at=e.created_at.isoformat() if e.created_at else "",
            )
            for e in events
        ],
        created_at=plan.created_at.isoformat() if plan.created_at else "",
    )


@router.delete("/api/plans/{plan_id}")
async def delete_plan(plan_id: str, db: AsyncSession = Depends(get_db)):
    try:
        pid = uuid.UUID(plan_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    deleted = await plan_repo.delete_plan(db, pid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Deleted"}


async def _get_db_session():
    from app.core.database import async_session
    async with async_session() as session:
        yield session


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Attempt 1: parse as-is
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Attempt 2: extract outermost { } and repair
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group()
    text = _repair_json(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Attempt 3: try to balance braces and retry
        balanced = _balance_braces(text)
        try:
            return json.loads(balanced)
        except json.JSONDecodeError:
            pass
        # Log the raw output for debugging
        import logging
        logging.getLogger(__name__).warning(
            "Failed to parse LLM JSON at line %d col %d. Raw (first 500 chars): %s",
            e.lineno, e.colno, text[:500]
        )
        raise



def _balance_braces(text: str) -> str:
    """Try to make braces balanced by adding missing closing brackets."""
    open_braces = text.count("{") - text.count("}")
    open_brackets = text.count("[") - text.count("]")
    fixed = text.rstrip()
    if open_braces > 0:
        fixed += "\n" + "\n}" * open_braces
    if open_brackets > 0:
        fixed += "\n" + "\n]" * open_brackets
    return fixed

def _repair_json(text: str) -> str:
    """Repair common LLM JSON formatting errors."""
    # Remove markdown code fences (in case _extract_json didn't catch them)
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text)
    # Remove trailing commas before ] or }
    text = re.sub(r",\s*(\}|\])", r"\1", text)
    # Remove double commas
    text = re.sub(r",\s*,", ",", text)
    # Remove single-line comments
    text = re.sub(r"//[^\n]*", "", text)
    # Fix smart/curly quotes
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    # Fix missing commas between objects in arrays: {...} {...} -> {...}, {...}
    text = re.sub(r"\}\s*\{", "}, {", text)
    # Fix missing commas between arrays: ] [ -> ], [
    text = re.sub(r"\]\s*\[", "], [", text)
    # Fix unquoted property names: {key: value} -> {"key": value}
    text = re.sub(r'(?<=[{,])\s*(\w+)\s*:', r'"\1":', text)
    return text


def _parse_itinerary_days(raw: dict) -> list[DayPlan]:
    days_list = raw.get("days_plan", raw.get("itinerary", []))
    result = []
    for day_data in days_list:
        activities = []
        for act in day_data.get("activities", []):
            activities.append(Activity(
                name=act.get("name", ""),
                location=act.get("location", ""),
                longitude=float(act.get("longitude", 0)),
                latitude=float(act.get("latitude", 0)),
                start_time=act.get("start_time", "09:00"),
                duration=int(act.get("duration", 120)),
                transport=act.get("transport", ""),
                description=act.get("description", ""),
            ))
        result.append(DayPlan(day=day_data.get("day", len(result) + 1), activities=activities))
    return result


def _parse_hotels(raw: dict) -> list[dict]:
    return raw.get("hotels", [])


def _parse_trains(raw: dict) -> list[dict]:
    return raw.get("trains", [])