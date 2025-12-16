from pydantic import BaseModel
from datetime import date, time
import uuid
from fastapi_users import schemas

class NewPracticeSession(BaseModel):
    date : date
    notes : str
    start_time : time
    end_time : time
    goals : str | None = None

class SavedPracticeSession(BaseModel):
    id : uuid.UUID
    date : date
    duration : int
    notes : str
    goals : str | None = None

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass