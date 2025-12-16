from fastapi import FastAPI, Depends, HTTPException
from app.schemas import UserRead, UserCreate, UserUpdate, NewPracticeSession, SavedPracticeSession 
from app.db import get_async_session, create_db_and_tables, PracticeSession
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from app.users import auth_backend, fastapi_users, current_active_user 
from datetime import date, time, timedelta
# from .routers import 

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(fastapi_users.get_auth_router(auth_backend), prefix='/auth/jwt', tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])

@app.get('/root')
async def get_root():
    return {"message": "root path works."}

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
        start_delta = timedelta(
            hours=practice_session.start_time.hour,
            minutes=practice_session.start_time.minute
            )
        
        end_delta = timedelta(
            hours=practice_session.end_time.hour,
            minutes=practice_session.end_time.minute
        )

        diff = end_delta - start_delta 
        total_minutes = diff.seconds / 60

        # print(total_minutes)

        new_log = PracticeSession(
            duration = total_minutes,
            **practice_session.model_dump()
        )
        db.add(new_log)
        await db.commit()
        await db.refresh(new_log)
        return SavedPracticeSession.model_validate(new_log, from_attributes=True)

    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Session not saved. {str(e)}")
