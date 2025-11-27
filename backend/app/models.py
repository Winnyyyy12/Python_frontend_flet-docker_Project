# backend/app/models.py
from sqlalchemy import Column, Integer, String, DateTime, Interval, Float, Boolean, Text
from .database import Base
import datetime
from sqlalchemy.sql import func

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    mode = Column(String, nullable=False)  # "stopwatch" or "pomodoro"
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)  # whole session duration in seconds
    note = Column(Text, default="")
    # For pomodoro: work_length, break_length, cycles stored as integers (minutes/cycles)
    work_minutes = Column(Integer, nullable=True)
    break_minutes = Column(Integer, nullable=True)
    cycles = Column(Integer, nullable=True)
    completed = Column(Boolean, default=False)
