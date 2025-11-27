# backend/app/utils.py
from datetime import datetime, timezone

def now_utc():
    return datetime.now(timezone.utc)
