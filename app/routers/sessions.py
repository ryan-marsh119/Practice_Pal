from fastapi import APIRouter, HTTPException, Depends
from ..db import PracticeSession, get_async_session, User, Goal
from ..users import current_active_user
from ..schemas import NewPracticeSession, SavedPracticeSession, UpdatePracticeSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

router = APIRouter(
    prefix="/practice_session",
    tags=["practice_sessions"]
)

@router.get('/')
async def get_practice_session(
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> list[SavedPracticeSession]:
    stmt = (
        select(PracticeSession)
        .join(Goal, PracticeSession.goal_id == Goal.id)
        .where(Goal.user_id == user.id)
    )
    result = await db.scalars(stmt)
    db_result = result.all()

    if not db_result:
        raise HTTPException(status_code=404, detail="No practice sessions. Go practice!")
    
    return [SavedPracticeSession.model_validate(r, from_attributes=True) for r in db_result]

@router.get('/{id}')
async def get_practice_session(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> SavedPracticeSession:
    stmt = (
        select(PracticeSession)
        .join(Goal, PracticeSession.goal_id == Goal.id)
        .where(Goal.user_id == user.id)
        .where(PracticeSession.id == id)
    )
    result = await db.execute(stmt)
    db_result = result.scalar_one_or_none()

    if not db_result:
        raise HTTPException(status_code=404, detail="Practice session not found.")
    
    return SavedPracticeSession.model_validate(db_result, from_attributes=True)


@router.post('/new', status_code=201)
async def new_practice_session(
    practice_session: NewPracticeSession,
    db: AsyncSession = Depends(get_async_session)
) -> SavedPracticeSession:
    try:
        new_log = PracticeSession(
            **practice_session.model_dump()
        )
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)
        return SavedPracticeSession.model_validate(new_log, from_attributes=True)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Session not saved. {str(e)}")

@router.put("/update/{id}", status_code=200)
async def update_practice_session(
    id: uuid.UUID,
    session_data: UpdatePracticeSession,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> SavedPracticeSession:
    
    stmt = (
        select(PracticeSession)
        .join(Goal, PracticeSession.goal_id == Goal.id)
        .where(Goal.user_id == user.id)
        .where(PracticeSession.id == id)
    )
    result = await db.execute(stmt)
    db_result = result.scalar_one_or_none()

    if not db_result:
        raise HTTPException(status_code=404, detail="Practice session not found.")
    
    update_data = session_data.model_dump()
    for key, value in update_data.items():
        setattr(db_result, key, value)

    await db.commit()
    await db.refresh(db_result)

    return SavedPracticeSession.model_validate(db_result, from_attributes=True)

@router.patch("/update/{id}", status_code=200)
async def edit_practice_session(
    id: uuid.UUID,
    session_data: UpdatePracticeSession,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)

) -> SavedPracticeSession:
    stmt = (
        select(PracticeSession)
        .join(Goal, PracticeSession.goal_id == Goal.id)
        .where(Goal.user_id == user.id)
        .where(PracticeSession.id == id)
    )
    result = await db.execute(stmt)
    db_result = result.scalar_one_or_none()

    if not db_result:
        raise HTTPException(status_code=404, detail="Practice session not found.")
    
    update_data = session_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_result, key, value)

    await db.commit()
    await db.refresh(db_result)

    return SavedPracticeSession.model_validate(db_result, from_attributes=True)

@router.delete("/delete/{id}", status_code=204)
async def delete_practice_session(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
) -> None:
    stmt = (
        select(PracticeSession)
        .join(Goal, PracticeSession.goal_id == Goal.id)
        .where(Goal.user_id == user.id)
        .where(PracticeSession.id ==id)
    )
    result = await db.execute(stmt)
    deleted_session = result.scalar_one_or_none()

    if not deleted_session:
        raise HTTPException(status_code=404, detail="Practice Session not found.")
    
    await db.delete(deleted_session)
    await db.commit()