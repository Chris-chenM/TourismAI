"""Travel plan repository"""

import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.travel_plan import TravelPlan


async def save_plan(
    db: AsyncSession,
    visitor_id: str,
    destination: str,
    days: int,
    budget: float,
    interests: str,
    status: str = "generating",
) -> TravelPlan:
    plan = TravelPlan(
        visitor_id=visitor_id,
        destination=destination,
        days=days,
        budget=budget,
        interests=interests,
        status=status,
    )
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


async def update_plan_status(
    db: AsyncSession,
    plan_id: uuid.UUID,
    status: str,
    itinerary: dict | None = None,
) -> TravelPlan | None:
    plan = await db.get(TravelPlan, plan_id)
    if not plan:
        return None
    plan.status = status
    if itinerary is not None:
        plan.itinerary = itinerary
    await db.commit()
    await db.refresh(plan)
    return plan


async def list_plans(
    db: AsyncSession,
    visitor_id: str,
    limit: int = 20,
) -> list[TravelPlan]:
    result = await db.execute(
        select(TravelPlan)
        .where(TravelPlan.visitor_id == visitor_id)
        .order_by(desc(TravelPlan.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> TravelPlan | None:
    return await db.get(TravelPlan, plan_id)


async def delete_plan(
    db: AsyncSession,
    plan_id: uuid.UUID,
) -> bool:
    plan = await db.get(TravelPlan, plan_id)
    if not plan:
        return False
    await db.delete(plan)
    await db.commit()
    return True