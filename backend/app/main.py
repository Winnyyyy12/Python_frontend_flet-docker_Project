# backend/app/main.py
from fastapi import FastAPI, HTTPException
from .database import database, engine, metadata
from . import models, crud, schemas
import asyncio
from typing import List
import os

# create tables (sync) if not exist
metadata.create_all(bind=engine)

app = FastAPI(title="Stopwatch-Pomodoro API")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/sessions/", response_model=schemas.SessionRead)
async def create_session(payload: schemas.SessionCreate):
    d = payload.dict()
    # ensure started_at defaults to now if not provided
    if d.get("started_at") is None:
        d["started_at"] = None  # database default handles it
    row = await crud.create_session(d)
    return row

@app.get("/sessions/", response_model=List[schemas.SessionRead])
async def list_sessions(limit: int = 200):
    return await crud.list_sessions(limit=limit)

@app.get("/stats/")
async def stats():
    return await crud.get_stats()
