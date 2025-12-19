from fastapi import APIRouter, HTTPException, Depends
from ..db import Goal, PracticeSession, get_async_session, User
from ..users import current_active_user
from ..schemas import NewGoal, SavedGoal, UpdateGoal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

router = APIRouter(
    prefix = "/goals",
    tags = ["goals"]
)

@router.get("/")
async def get_goal(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> list[SavedGoal]:
    stmt = select(Goal).where(Goal.user_id == user.id)
    result = await db.scalars(stmt)
    goals = result.all()

    if not goals:
        raise HTTPException(status_code=404, detail="No goals. Go set some goals!")
    
    return [SavedGoal.model_validate(g, from_attributes=True) for g in goals]

@router.get("/{id}")
async def get_goal(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> SavedGoal:
    stmt = select(Goal).where(Goal.user_id == user.id).where(Goal.id == id)
    result = await db.scalars(stmt)
    goal = result.one_or_none()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    
    return SavedGoal.model_validate(goal, from_attributes=True)

@router.put("/make_goal", status_code=201)
async def make_goal(
    goal: NewGoal,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> SavedGoal:
    try:
        new_goal = Goal(
            user_id = user.id,
            **goal.model_dump()
        )
        db.add(new_goal)
        await db.commit()
        await db.refresh(new_goal)
        return SavedGoal.model_validate(new_goal, from_attributes=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/complete/{id}", status_code=200)
async def complete_goal(
    id: uuid.UUID,
    goal_data: UpdateGoal,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> SavedGoal:
    stmt = select(Goal).where(Goal.id == id)
    result = await db.execute(stmt)
    db_result = result.scalar_one_or_none()

    if not db_result:
        raise HTTPException(status_code=404, detail="Goal not found.")

    if db_result.user_id != user.id:
        raise HTTPException(status_code=401, detail="Not your goal. Cannot update.")
    
    update_data = goal_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_result, key, value)

    await db.commit()
    await db.refresh(db_result)

    return SavedGoal.model_validate(db_result, from_attributes=True)

# https://docs.pydantic.dev/2.12/errors/validation_errors/#model_attributes_type

#@router.put("/update_goal")    
# 3850c5a8-889f-4e4d-af7d-a7a06321fb8f