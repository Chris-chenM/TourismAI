"""Agent event repository"""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.travel_plan import AgentEvent


async def save_event(
    db: AsyncSession,
    plan_id: uuid.UUID,
    phase: str,
    message: str,
) -> AgentEvent:
    event = AgentEvent(plan_id=plan_id, phase=phase, message=message)
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def get_events(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> list[AgentEvent]:
    result = await db.execute(
        select(AgentEvent)
        .where(AgentEvent.plan_id == plan_id)
        .order_by(AgentEvent.created_at)
    )
    return list(result.scalars().all())