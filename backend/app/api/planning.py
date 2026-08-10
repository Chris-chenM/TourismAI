"""行程规划接口"""

import json
import re
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.agents.planner import create_planner_agent, build_initial_state, run_agent_stream

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
    description: str = ""


class DayPlan(BaseModel):
    """单日行程"""
    day: int
    activities: list[Activity]


class PlanResponse(BaseModel):
    """规划结果"""
    destination: str
    days: int
    itinerary: list[DayPlan]


# ── 同步接口（保留不动） ──

@router.post("/api/plan", response_model=PlanResponse)
async def plan_trip(req: PlanRequest):
    """生成旅行计划"""
    try:
        agent = create_planner_agent()
        initial_state = build_initial_state(req.destination, req.days, req.budget, req.interests)

        result = await agent.ainvoke(initial_state)

        last_msg = result["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

        raw = _extract_json(content)
        itinerary = _parse_itinerary(raw)

        return PlanResponse(
            destination=raw.get("destination", req.destination),
            days=raw.get("days", req.days),
            itinerary=itinerary,
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 返回了不规范的 JSON，请重试。错误位置：{str(e)}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"规划失败：{str(e)}")


# ── SSE 流式接口 ──

@router.post("/api/plan/stream")
async def plan_trip_stream(req: PlanRequest):
    """生成旅行计划（SSE 流式推送进度与结果）"""
    initial_state = build_initial_state(req.destination, req.days, req.budget, req.interests)

    async def event_generator():
        async for sse_chunk in run_agent_stream(initial_state):
            yield sse_chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── JSON 提取 ──

def _extract_json(text: str) -> dict:
    """从大模型输出中提取 JSON，自动修复常见格式问题"""
    text = text.strip()

    # 去掉 Markdown 代码块
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 提取花括号内容
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        text = match.group()

    # 修复常见 LLM JSON 错误
    text = _repair_json(text)

    return json.loads(text)


def _repair_json(text: str) -> str:
    """修复 LLM 常见 JSON 格式错误"""
    # 1. 去掉尾部逗号（在 } 或 ] 之前）
    text = re.sub(r",\s*(\}|\])", r"\1", text)
    # 2. 去掉连续逗号
    text = re.sub(r",\s*,", ",", text)
    # 3. 去掉注释行 (// ...)
    text = re.sub(r"//[^\n]*", "", text)
    # 4. 修复中文引号
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")

    return text


def _parse_itinerary(raw: dict) -> list[DayPlan]:
    """将 LLM 输出的原始 dict 转为 Pydantic 模型，缺失字段自动补默认值"""
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
                description=act.get("description", ""),
            ))
        days.append(DayPlan(day=day_data.get("day", len(days) + 1), activities=activities))
    return days
