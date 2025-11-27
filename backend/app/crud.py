# backend/app/crud.py
from .database import database
from .schemas import SessionCreate
from typing import List
from datetime import datetime

TABLE = "sessions"

async def create_session(payload: dict) -> dict:
    query = """
    INSERT INTO sessions (mode, started_at, ended_at, duration_seconds, note, work_minutes, break_minutes, cycles, completed)
    VALUES (:mode, :started_at, :ended_at, :duration_seconds, :note, :work_minutes, :break_minutes, :cycles, :completed)
    RETURNING *
    """
    row = await database.fetch_one(query=query, values=payload)
    return dict(row)

async def list_sessions(limit: int = 100):
    query = "SELECT * FROM sessions ORDER BY started_at DESC LIMIT :limit"
    rows = await database.fetch_all(query=query, values={"limit": limit})
    return [dict(r) for r in rows]

async def get_stats():
    # Returns aggregated stats for charts
    # total sessions, total time, sessions by mode
    q_tot = "SELECT COUNT(*)::int AS total_sessions, COALESCE(SUM(duration_seconds),0)::int AS total_seconds FROM sessions"
    r_tot = await database.fetch_one(q_tot)
    q_by_mode = "SELECT mode, COUNT(*)::int AS cnt, COALESCE(SUM(duration_seconds),0)::int AS total_seconds FROM sessions GROUP BY mode"
    rows = await database.fetch_all(q_by_mode)
    return {
        "total_sessions": int(r_tot["total_sessions"]),
        "total_seconds": int(r_tot["total_seconds"]),
        "by_mode": [dict(x) for x in rows]
    }
