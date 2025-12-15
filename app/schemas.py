from pydantic import BaseModel
from pydantic_extra_types.pendulum_dt import DateTime
import uuid

class NewPracticeSession(BaseModel):
    # id : uuid.UUID
    # date : DateTime
    duration : int
    notes : str
    goals : str | None = None

class SavedPracticeSession(BaseModel):
    id : uuid.UUID
    # date : DateTime
    duration : int
    notes : str
    goals : str | None = None