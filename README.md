# Pulse — Stopwatch & Pomodoro Timer

A tiny, addictive productivity app built with **Flet (Python)** for the frontend, **FastAPI** for backend APIs, and **PostgreSQL** for data storage. Supports session tracking, history, and stats dashboards. Fully containerized backend with **Docker Compose**.

---

## Features

- Stopwatch and Pomodoro timer modes
- Session history logging
- Stats dashboard with line & pie charts
- Add notes to sessions
- Save and fetch sessions via FastAPI backend
- Postgres database (Dockerized)
- Desktop GUI with Flet
- Tiny but addictive interface

---

## Folder Structure

stopwatch-pomodoro/
├─ backend/
│ ├─ Dockerfile
│ ├─ requirements.txt
│ ├─ .env.example
│ └─ app/
│ ├─ init.py
│ ├─ main.py
│ ├─ database.py
│ ├─ models.py
│ ├─ schemas.py
│ └─ crud.py
├─ docker-compose.yml
└─ frontend/
├─ requirements.txt
└─ app.py

yaml
Copy code

---

## Prerequisites

- Python 3.11+ (for frontend)
- Docker & Docker Compose
- Git (optional)
- `pip` installed

---

## Setup & Run

### 1. Clone / prepare project
bash
git clone <repo-url> stopwatch-pomodoro
cd stopwatch-pomodoro
### 2. Configure backend environment
bash
Copy code
cp backend/.env.example backend/.env
#optionally edit backend/.env for custom credentials
### 3. Start Postgres + backend via Docker Compose
bash
Copy code
docker compose up --build -d
Check logs:

bash
Copy code
docker compose logs -f backend
Verify backend is running:

bash
Copy code
curl http://127.0.0.1:8000/sessions/
### 4. Run Flet frontend locally
bash
Copy code
cd frontend
python -m venv .venv
#activate venv
#Linux / macOS
source .venv/bin/activate
#Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
The desktop Flet GUI should open automatically.

### 5. Test end-to-end
Start stopwatch or Pomodoro in the GUI

Save a session

Fetch session history via API:

bash
Copy code
curl http://127.0.0.1:8000/sessions/
curl http://127.0.0.1:8000/stats/
Stop & Cleanup
Stop containers:

bash
Copy code
docker compose down
Remove volumes (wipes database):

bash
Copy code
docker compose down -v
Notes
Backend tables are auto-created using SQLAlchemy metadata.create_all
Frontend connects to http://127.0.0.1:8000 by default — edit frontend/app.py if needed
Ideal workflow: Dockerized backend + local Flet GUI

### Dependencies
Backend

FastAPI

Uvicorn

SQLAlchemy

asyncpg

Databases

Pydantic

python-dotenv

Frontend

Flet

Requests

Matplotlib

