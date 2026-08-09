"""行程规划接口"""

import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.planner import create_planner_agent, build_initial_state

router = APIRouter()


# ── 请求模型 ──

class PlanRequest(BaseModel):
    """规划请求"""
    destination: str = Field(..., description="目的地城市", examples=["杭州"])
    days: int = Field(..., ge=1, le=30, description="出行天数", examples=[3])
    budget: float = Field(..., gt=0, description="预算（元）", examples=[2000])
    interests: str = Field(default="", description="兴趣偏好", examples=["历史文化、美食"])


# ── 响应模型 ──

class Activity(BaseModel):
    """单个景点活动"""
    name: str
    location: str
    longitude: float
    latitude: float
    start_time: str
    duration: int
    transport: str


class DayPlan(BaseModel):
    """单日行程"""
    day: int
    activities: list[Activity]


class PlanResponse(BaseModel):
    """规划结果"""
    destination: str
    days: int
    itinerary: list[DayPlan]


# ── 接口 ──

@router.post("/api/plan", response_model=PlanResponse)
async def plan_trip(req: PlanRequest):
    """生成旅行计划"""
    try:
        agent = create_planner_agent()
        initial_state = build_initial_state(req.destination, req.days, req.budget, req.interests)

        result = await agent.ainvoke(initial_state)

        # 取最后一条 AI 消息
        last_msg = result["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        # 提取 JSON 并校验
        raw = _extract_json(content)
        itinerary = _parse_itinerary(raw)

        return PlanResponse(
            destination=raw.get("destination", req.destination),
            days=raw.get("days", req.days),
            itinerary=itinerary,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"规划失败：{str(e)}")


# ── 辅助函数 ──

def _extract_json(text: str) -> dict:
    """从大模型输出中提取 JSON"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        return {}


def _parse_itinerary(raw: dict) -> list[DayPlan]:
    """将 LLM 输出的原始 dict 转为 Pydantic 模型列表，缺失字段自动补默认值"""
    days = []
    for day_data in raw.get("itinerary", []):
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
            ))
        days.append(DayPlan(day=day_data.get("day", len(days) + 1), activities=activities))
    return days
