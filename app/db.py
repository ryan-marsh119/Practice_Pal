from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, Time, Text, Date
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from app.settings import DATABASE_URL, SECRET_KEY
from fastapi import Depends
from collections.abc import AsyncGenerator
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from datetime import date


class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

class PracticeSession(Base):
    __tablename__ = 'practice_session'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4)
    date = Column(Date, default=date.today)
    start_time = Column(Time)
    end_time = Column(Time)
    duration = Column(Integer)
    notes = Column(Text)
    goals = Column(Text, nullable=True)

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