from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, Time, Text, Date, event
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped
from app.settings import DATABASE_URL
from fastapi import Depends
from collections.abc import AsyncGenerator
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from datetime import date, timedelta


class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    goals: Mapped["Goal"] = relationship(back_populates="user_goal")

class PracticeSession(Base):
    __tablename__ = 'practice_session'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    date = Column(Date, default=date.today)
    start_time = Column(Time)
    end_time = Column(Time)
    duration = Column(Integer)
    notes = Column(Text, default="Enter notes here!")
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goal.id", ondelete="CASCADE"), nullable=True)

    goal: Mapped["Goal"] = relationship(back_populates="practice_session_entry")

    def calculate_session_duration(self):
        start_delta = timedelta(
            hours=self.start_time.hour,
            minutes=self.start_time.minute
            )
        
        end_delta = timedelta(
            hours=self.end_time.hour,
            minutes=self.end_time.minute
        )

        diff = end_delta - start_delta 
        total_duration = diff.seconds / 60

        self.duration = total_duration
        
class Goal(Base):
    __tablename__ = 'goal'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(100))
    description = Column(Text, nullable=False, default="Enter description here!")
    complete = Column(Boolean, default=False)

    user_goal: Mapped["User"] = relationship(back_populates="goals")
    practice_session_entry: Mapped["PracticeSession"] = relationship(back_populates="goal")

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

@event.listens_for(PracticeSession, 'before_update')
@event.listens_for(PracticeSession, 'before_insert')
def before_insert_practice_session(mapper, connection, target: PracticeSession):
   target.calculate_session_duration()