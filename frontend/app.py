# frontend/app.py
import flet as ft
import requests
import threading
import time
from datetime import datetime, timedelta
import io
import matplotlib.pyplot as plt
import base64
import os

API = os.getenv("API_URL", "http://127.0.0.1:8000")

# ---------- Helpers ----------
def run_thread(fn, *a, **k):
    threading.Thread(target=fn, args=a, kwargs=k, daemon=True).start()

def seconds_to_hms(s: int):
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{sec:02d}"
    return f"{m:02d}:{sec:02d}"

# ---------- Charts ----------
def make_line_chart(sessions):
    # sessions: list of dicts with started_at & duration_seconds
    # build daily totals for last 14 days
    days = {}
    for i in range(14):
        d = (datetime.now().date() - timedelta(days=i)).isoformat()
        days[d] = 0
    for s in sessions:
        started = s["started_at"][:10]  # YYYY-MM-DD
        if started in days and s["duration_seconds"]:
            days[started] += s["duration_seconds"]
    dates = sorted(days.keys())
    values = [days[d]/60 for d in dates]  # minutes
    plt.figure(figsize=(8,2.4))
    plt.plot(dates, values, marker="o")
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")

def make_pie_chart(by_mode):
    labels = []
    values = []
    for b in by_mode:
        labels.append(b["mode"])
        values.append(b["cnt"])
    if not values:
        labels = ["none"]; values=[1]
    plt.figure(figsize=(3.5,3.5))
    plt.pie(values, labels=labels, autopct="%1.0f%%")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")

# ---------- App ----------
def main(page: ft.Page):
    page.title = "Pulse — Stopwatch & Pomodoro"
    page.window_width = 900
    page.window_height = 700
    page.padding = 16

    # State
    running = {"running": False, "start_ts": None, "elapsed": 0}
    laps = []
    current_pomodoro = {"running": False, "mode": "work", "cycle": 0, "work_minutes":25, "break_minutes":5, "cycles":4}

    # UI elements
    timer_text = ft.Text("00:00", size=48, weight=ft.FontWeight.W_600)
    mode_chip = ft.Text("Mode: Stopwatch", size=12)
    laps_list = ft.ListView(expand=1, spacing=6)
    history_list = ft.ListView(expand=1, spacing=6, width=380)

    # Dashboard images (placeholders)
    line_img = ft.Image(width=520, height=160)
    pie_img = ft.Image(width=200, height=160)

    # ----------------- Stopwatch functions -----------------
    def tick():
        while True:
            if running["running"]:
                now = time.time()
                running["elapsed"] = int(now - running["start_ts"])
                timer_text.value = seconds_to_hms(running["elapsed"])
                page.update()
            time.sleep(0.2)

    def start_stopwatch(e):
        if not running["running"]:
            running["running"] = True
            running["start_ts"] = time.time() - running["elapsed"]
        else:
            running["running"] = False
        page.update()

    def reset_stopwatch(e):
        running["running"] = False
        running["elapsed"] = 0
        laps.clear()
        timer_text.value = "00:00"
        page.update()

    def lap_stopwatch(e):
        if running["running"]:
            laps.insert(0, {"label": f"Lap {len(laps)+1}", "seconds": running["elapsed"]})
            refresh_laps()

    def refresh_laps():
        laps_list.controls.clear()
        for l in laps:
            laps_list.controls.append(ft.Card(content=ft.Container(ft.Row([ft.Text(l["label"]), ft.Text(seconds_to_hms(l["seconds"]))], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=8)))
        page.update()

    def save_stopwatch_session(e):
        # Persist current elapsed as a session (stopwatch mode)
        payload = {
            "mode": "stopwatch",
            "started_at": None,
            "ended_at": None,
            "duration_seconds": running["elapsed"],
            "note": "manual save"
        }
        def job():
            try:
                requests.post(f"{API}/sessions/", json=payload, timeout=8)
                fetch_history()
                fetch_stats()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
                page.snack_bar.open = True
                page.update()
        run_thread(job)

    # ----------------- Pomodoro functions -----------------
    pom_timer_label = ft.Text("Work: 25:00", size=28)
    pom_control_btn = ft.ElevatedButton("Start Pomodoro")
    pom_session_seconds = {"remaining": current_pomodoro["work_minutes"]*60}

    def pom_tick():
        while True:
            if current_pomodoro["running"]:
                if pom_session_seconds["remaining"] > 0:
                    pom_session_seconds["remaining"] -= 1
                    mins = pom_session_seconds["remaining"]//60
                    secs = pom_session_seconds["remaining"]%60
                    pom_timer_label.value = f"{'Work' if current_pomodoro['mode']=='work' else 'Break'}: {mins:02d}:{secs:02d}"
                    page.update()
                else:
                    # cycle complete (switch)
                    if current_pomodoro["mode"] == "work":
                        # save work session
                        payload = {
                            "mode": "pomodoro",
                            "duration_seconds": current_pomodoro["work_minutes"]*60,
                            "work_minutes": current_pomodoro["work_minutes"],
                            "break_minutes": current_pomodoro["break_minutes"],
                            "cycles": current_pomodoro["cycles"],
                            "note": "pomodoro work"
                        }
                        run_thread(lambda: requests.post(f"{API}/sessions/", json=payload))
                        current_pomodoro["mode"] = "break"
                        pom_session_seconds["remaining"] = current_pomodoro["break_minutes"]*60
                    else:
                        current_pomodoro["mode"] = "work"
                        current_pomodoro["cycle"] += 1
                        if current_pomodoro["cycle"] >= current_pomodoro["cycles"]:
                            # finished all cycles
                            current_pomodoro["running"] = False
                            pom_session_seconds["remaining"] = 0
                            pom_timer_label.value = "Done"
                            run_thread(fetch_history)
                            run_thread(fetch_stats)
                            page.update()
                            continue
                        pom_session_seconds["remaining"] = current_pomodoro["work_minutes"]*60
                    page.update()
            time.sleep(1)

    def toggle_pomodoro(e):
        if not current_pomodoro["running"]:
            # start a new pomodoro cycle
            current_pomodoro["running"] = True
            current_pomodoro["mode"] = "work"
            current_pomodoro["cycle"] = 0
            pom_session_seconds["remaining"] = current_pomodoro["work_minutes"]*60
            pom_control_btn.text = "Stop Pomodoro"
        else:
            current_pomodoro["running"] = False
            pom_control_btn.text = "Start Pomodoro"
        page.update()

    # ----------------- History & Stats -----------------
    import requests

    def fetch_history():
        try:
            r = requests.get(f"{API}/sessions/")
            r.raise_for_status()
            data = r.json()
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(str(ex)))
            page.snack_bar.open = True
            page.update()
            return
        history_list.controls.clear()
        for s in data:
            dur = s["duration_seconds"] or 0
            started = s["started_at"][:19].replace("T", " ") if s.get("started_at") else "-"
            history_list.controls.append(
                ft.Card(content=ft.Container(ft.Column([
                    ft.Row([ft.Text(f"{s['mode'].capitalize()}"), ft.Text(f"{dur//60}m {dur%60}s")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(started, size=10),
                    ft.Text(s.get("note") or "", size=10)
                ]), padding=8))
            )
        page.update()
        # refresh charts
        run_thread(lambda: refresh_charts(data))

    def fetch_stats():
        try:
            r = requests.get(f"{API}/stats/")
            r.raise_for_status()
            stats = r.json()
        except Exception as ex:
            return
        # pie chart from stats['by_mode']
        pie_b64 = make_pie_chart(stats.get("by_mode", []))
        pie_img.src_base64 = pie_b64
        page.update()

    def refresh_charts(sessions):
        line_b64 = make_line_chart(sessions)
        line_img.src_base64 = line_b64
        pie_b64 = make_pie_chart([{"mode":s["mode"], "cnt":1} for s in sessions])  # simple fallback
        pie_img.src_base64 = pie_b64
        page.update()

    # ----------------- Build UI -----------------
    # Left column: timer, controls, laps
    left = ft.Column([
        ft.Text("Pulse", size=26, weight=ft.FontWeight.BOLD),
        mode_chip,
        timer_text,
        ft.Row([
            ft.ElevatedButton("Start/Stop", on_click=start_stopwatch),
            ft.ElevatedButton("Lap", on_click=lap_stopwatch),
            ft.ElevatedButton("Reset", on_click=reset_stopwatch),
            ft.ElevatedButton("Save Session", on_click=save_stopwatch_session)
        ], spacing=8),
        ft.Divider(),
        ft.Text("Laps", size=14),
        ft.Container(laps_list, expand=True, height=200),
    ], spacing=12, expand=True)

    # Center: Pomodoro
    center = ft.Column([
        ft.Text("Pomodoro", size=20, weight=ft.FontWeight.W_600),
        pom_timer_label,
        ft.Row([
            ft.ElevatedButton("Start/Stop Pomodoro", on_click=toggle_pomodoro),
            ft.ElevatedButton("Fetch History", on_click=lambda e: run_thread(fetch_history))
        ]),
        ft.Row([
            ft.Text("Work (min)"), ft.TextField(value=str(current_pomodoro["work_minutes"]), width=60, on_change=lambda e: set_work(e)),
            ft.Text("Break (min)"), ft.TextField(value=str(current_pomodoro["break_minutes"]), width=60, on_change=lambda e: set_break(e)),
            ft.Text("Cycles"), ft.TextField(value=str(current_pomodoro["cycles"]), width=60, on_change=lambda e: set_cycles(e)),
        ], spacing=8)
    ], spacing=8, width=340)

    def set_work(e):
        try:
            v = int(e.control.value)
            current_pomodoro["work_minutes"] = v
        except:
            pass

    def set_break(e):
        try:
            v = int(e.control.value)
            current_pomodoro["break_minutes"] = v
        except:
            pass

    def set_cycles(e):
        try:
            v = int(e.control.value)
            current_pomodoro["cycles"] = v
        except:
            pass

    # right: history + charts
    right = ft.Column([
        ft.Text("History", size=18),
        history_list,
        ft.Divider(),
        ft.Text("Stats", size=18),
        line_img,
        pie_img
    ], spacing=8, expand=True)

    page.add(ft.Row([left, center, right], alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
    page.update()

    # Start background tickers
    run_thread(tick)
    run_thread(pom_tick)
    run_thread(fetch_history)
    run_thread(fetch_stats)

ft.app(target=main)
