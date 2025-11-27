# backend/app/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionCreate(BaseModel):
    mode: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    note: Optional[str] = ""
    work_minutes: Optional[int] = None
    break_minutes: Optional[int] = None
    cycles: Optional[int] = None
    completed: Optional[bool] = False

class SessionRead(SessionCreate):
    id: int
    class Config:
        orm_mode = True
