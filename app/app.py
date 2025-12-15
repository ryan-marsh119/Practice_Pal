from fastapi import FastAPI, Depends, HTTPException
from app.schemas import NewPracticeSession, SavedPracticeSession
from app.db import PracticeSession, get_async_session, create_db_and_tables
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
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
