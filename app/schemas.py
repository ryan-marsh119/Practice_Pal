from pydantic import BaseModel, UUID4
from datetime import date, time
# import uuid
from fastapi_users import schemas

class NewGoal(BaseModel):
    title: str
    description : str
    
class SavedGoal(BaseModel):
    id: UUID4
    user_id : UUID4
    title: str
    description : str
    complete : bool

class UpdateGoal(BaseModel):
    id: UUID4 | None = None
    user_id: UUID4 | None = None
    title: str | None = None
    description: str | None = None
    complete: bool | None = None

class NewPracticeSession(BaseModel):
    date : date
    notes : str
    start_time : time
    end_time : time
    goal_id : UUID4

class SavedPracticeSession(BaseModel):
    id : UUID4
    date : date
    start_time: time
    end_time: time
    duration : int
    notes : str
    goal_id: int

class UserRead(schemas.BaseUser[UUID4]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass