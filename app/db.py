from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, Time, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from app.settings import DATABASE_URL
from fastapi import Depends
from collections.abc import AsyncGenerator
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from datetime import date


class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    goals = relationship("Goal", back_populates="user_goal")

class PracticeSession(Base):
    __tablename__ = 'practice_session'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    date = Column(Date, default=date.today)
    start_time = Column(Time)
    end_time = Column(Time)
    duration = Column(Integer)
    notes = Column(Text, default="Enter notes here!")
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goal.id"), nullable=True)

    goal = relationship("Goal", back_populates="practice_session_entry")

class Goal(Base):
    __tablename__ = 'goal'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    title = Column(String(100))
    description = Column(Text, nullable=False, default="Enter description here!")
    complete = Column(Boolean, default=False)

    user_goal = relationship("User", back_populates="goals")
    practice_session_entry = relationship("PracticeSession", back_populates="goal")

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)