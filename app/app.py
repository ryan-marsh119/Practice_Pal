from fastapi import FastAPI, Depends, HTTPException
from app.schemas import NewPracticeSession, SavedPracticeSession
from app.db import PracticeSession, get_async_session, create_db_and_tables
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import uuid
# from .routers import 

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/logs')
async def get_logs(
    db: AsyncSession = Depends(get_async_session)
) -> list[SavedPracticeSession]:
    stmt = select(PracticeSession)
    result = await db.scalars(stmt)
    all_logs = result.all()

    return [SavedPracticeSession.model_validate(all, from_attributes=True) for all in all_logs]

@app.get('/logs/{id}')
async def get_logs(
    id: str,
    db: AsyncSession = Depends(get_async_session)
) ->SavedPracticeSession:
    
    log_uuid = uuid.UUID(id)
    stmt = select(PracticeSession).where(PracticeSession.id==log_uuid)
    result = await db.scalars(stmt)
    log = result.one_or_none()


    if not log:
        raise HTTPException(status_code=404, detail="Practice session not found!")

    return SavedPracticeSession.model_validate(log, from_attributes=True)


@app.post('/newlog')
async def newlog(
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
    

@app.delete('/deletelog', status_code=204)
async def deletelog(
    id: str,
    db: AsyncSession = Depends(get_async_session)
) -> None:

    log_uuid = uuid.UUID(id)

    stmt = select(PracticeSession).where(PracticeSession.id == log_uuid)
    result = await db.scalars(stmt)
    deleted_log = result.one_or_none()

    if not deleted_log:
        raise HTTPException(status_code=404, detail="Practice session not found!")
    
    await db.delete(deleted_log)
    await db.commit()

