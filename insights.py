# ── insights.py ───────────────────────────────────────────────────────────────
# Deterministic, rule-based productivity insight engine.
# No AI required. All logic is threshold-based and non-judgmental.

import sqlite3
from datetime import date as _date, timedelta
from pathlib import Path
from db import _conn, DB_PATH


# ── Helpers ───────────────────────────────────────────────────────────────────

def _date_range(days_back: int) -> list[str]:
    today = _date.today()
    return [(today - timedelta(days=i)).isoformat() for i in range(days_back)]


def _routine_total() -> int:
    """Total number of routine items (base + weekly combined per day)."""
    with _conn() as con:
        base = con.execute("SELECT COUNT(*) FROM routine_items").fetchone()[0]
    return base


def _routine_done_for_date(date_str: str) -> int:
    with _conn() as con:
        done = con.execute(
            "SELECT COUNT(*) FROM routine_checks WHERE date = ?", (date_str,)
        ).fetchone()[0]
        # Also count weekly checks for that date
        done_w = con.execute(
            "SELECT COUNT(*) FROM weekly_routine_checks WHERE date = ?", (date_str,)
        ).fetchone()[0]
    return done + done_w


def _weekly_total_for_date(date_str: str) -> int:
    """Weekly routine items scheduled for a given date's weekday."""
    from datetime import date as _d
    y, m, d = date_str.split("-")
    weekday = _d(int(y), int(m), int(d)).weekday()
    with _conn() as con:
        count = con.execute(
            "SELECT COUNT(*) FROM weekly_routine_items WHERE weekday = ?", (weekday,)
        ).fetchone()[0]
    return count


def _completion_pct(date_str: str) -> float | None:
    """Completion % for a date. None if no items exist."""
    total = _routine_total() + _weekly_total_for_date(date_str)
    if total == 0:
        return None
    done = _routine_done_for_date(date_str)
    return round((done / total) * 100, 1)


def _task_count_for_week(week_start: str) -> int:
    """Count dashboard tasks for a Mon-Sun week starting at week_start."""
    start = _date.fromisoformat(week_start)
    end = (start + timedelta(days=6)).isoformat()
    with _conn() as con:
        count = con.execute(
            "SELECT COUNT(*) FROM dashboard_tasks WHERE date BETWEEN ? AND ?",
            (week_start, end)
        ).fetchone()[0]
    return count


def _this_week_monday() -> str:
    today = _date.today()
    return (today - timedelta(days=today.weekday())).isoformat()


def _last_week_monday() -> str:
    this_mon = _date.fromisoformat(_this_week_monday())
    return (this_mon - timedelta(days=7)).isoformat()


# ── Streak ────────────────────────────────────────────────────────────────────

def _compute_streak() -> dict:
    """Return current_streak and longest_streak (days with ≥1 routine item done)."""
    total = _routine_total()
    if total == 0:
        return {"current": 0, "longest": 0}

    today = _date.today()
    current = 0
    longest = 0
    run = 0

    # Walk back up to 365 days
    for i in range(365):
        d = (today - timedelta(days=i)).isoformat()
        pct = _completion_pct(d)
        if pct is not None and pct > 0:
            run += 1
            if i == current:  # contiguous from today
                current = run
        else:
            if i < current + 1:
                current = run if i > 0 else 0
            longest = max(longest, run)
            run = 0

    longest = max(longest, run, current)
    return {"current": current, "longest": longest}


# ── Late completion pattern ───────────────────────────────────────────────────

def _late_completion_pattern() -> bool:
    """True if in the last 7 days most incomplete tasks were added late (time_end after 21:00)."""
    with _conn() as con:
        rows = con.execute(
            "SELECT time_end FROM dashboard_tasks WHERE done = 0 AND time_end IS NOT NULL "
            "AND date >= date('now', '-7 days')"
        ).fetchall()
    if not rows:
        return False
    late = sum(1 for r in rows if r[0] and r[0] >= "21:00")
    return late > len(rows) / 2


# ── Routine health per item ───────────────────────────────────────────────────

def _routine_item_health(item_id: int, item_text: str, days: int = 30) -> dict:
    """Compute health state for a single routine item."""
    dates = _date_range(days)
    checked_set: set[str] = set()

    with _conn() as con:
        rows = con.execute(
            "SELECT date FROM routine_checks WHERE item_id = ? AND date >= ?",
            (item_id, dates[-1])
        ).fetchall()
        checked_set = {r[0] for r in rows}

    if not dates:
        return {"state": "Stable", "streak": 0, "completion_pct": 0}

    completion = round(len(checked_set) / len(dates) * 100)

    # Streak: consecutive days ending today
    streak = 0
    for d in dates:  # dates[0] = today
        if d in checked_set:
            streak += 1
        else:
            break

    # Recent trend: last 7 vs prior 7
    recent_7 = [d for d in dates[:7]]
    prior_7 = [d for d in dates[7:14]]
    recent_pct = sum(1 for d in recent_7 if d in checked_set) / max(len(recent_7), 1)
    prior_pct = sum(1 for d in prior_7 if d in checked_set) / max(len(prior_7), 1)
    delta = recent_pct - prior_pct

    # Determine state
    if completion >= 85 and streak >= 5:
        state = "Healthy"
    elif delta > 0.2 and recent_pct >= 0.5:
        state = "Growing"
    elif delta < -0.25 and recent_pct < 0.5:
        state = "Declining"
    elif completion >= 50:
        state = "Stable"
    else:
        state = "Recovering"

    return {
        "id": item_id,
        "text": item_text,
        "state": state,
        "streak": streak,
        "completion_pct": completion,
    }


def get_routine_health() -> list[dict]:
    """Return health data for all routine items."""
    with _conn() as con:
        items = con.execute(
            "SELECT id, text FROM routine_items ORDER BY position ASC"
        ).fetchall()
    return [_routine_item_health(r["id"], r["text"]) for r in items]


# ── Weekly summary ────────────────────────────────────────────────────────────

def get_weekly_summary() -> dict:
    """Summary for the current Mon-Sun week."""
    mon = _this_week_monday()
    start = _date.fromisoformat(mon)
    today = _date.today()

    days_data = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i in range(7):
        d = (start + timedelta(days=i)).isoformat()
        if d > today.isoformat():
            break
        pct = _completion_pct(d)
        days_data.append({"day": day_names[i], "date": d, "pct": pct or 0})

    if not days_data:
        return {}

    pcts = [d["pct"] for d in days_data if d["pct"] > 0]
    weekly_avg = round(sum(pcts) / len(pcts)) if pcts else 0
    best = max(days_data, key=lambda x: x["pct"])
    worst = min(days_data, key=lambda x: x["pct"])

    # Trend vs last week
    last_mon = _last_week_monday()
    last_start = _date.fromisoformat(last_mon)
    last_pcts = []
    for i in range(7):
        d = (last_start + timedelta(days=i)).isoformat()
        p = _completion_pct(d)
        if p is not None:
            last_pcts.append(p)

    last_avg = round(sum(last_pcts) / len(last_pcts)) if last_pcts else None
    trend = None
    if last_avg is not None and weekly_avg > 0:
        trend = weekly_avg - last_avg

    # Task count vs last week
    this_tasks = _task_count_for_week(mon)
    last_tasks = _task_count_for_week(last_mon)

    return {
        "days": days_data,
        "weekly_avg": weekly_avg,
        "best_day": best,
        "worst_day": worst,
        "trend": trend,
        "this_week_tasks": this_tasks,
        "last_week_tasks": last_tasks,
    }


# ── Greeting insights ─────────────────────────────────────────────────────────

def get_greeting_insights() -> dict:
    """Insights shown on the home page greeting panel."""
    today = _date.today().isoformat()
    yesterday = (_date.today() - timedelta(days=1)).isoformat()

    yesterday_pct = _completion_pct(yesterday)
    streak = _compute_streak()
    weekly = get_weekly_summary()
    late_pattern = _late_completion_pattern()

    insights: list[str] = []

    # Yesterday completion
    if yesterday_pct is not None:
        insights.append({"type": "yesterday", "pct": yesterday_pct,
                         "label": f"Yesterday: {int(yesterday_pct)}% completed."})

    # Streak
    if streak["current"] >= 3:
        insights.append({
            "type": "streak",
            "days": streak["current"],
            "label": f"You've been consistent for {streak['current']} days."
        })

    # Late tasks pattern
    if late_pattern:
        insights.append({
            "type": "late",
            "label": "Most unfinished tasks happen after 9 PM."
        })

    # Workload this week vs last
    if weekly.get("this_week_tasks") and weekly.get("last_week_tasks"):
        tw = weekly["this_week_tasks"]
        lw = weekly["last_week_tasks"]
        if lw > 0:
            delta_pct = ((tw - lw) / lw) * 100
            if delta_pct >= 30:
                insights.append({
                    "type": "workload",
                    "label": "This week is considerably busier than usual."
                })
            elif delta_pct >= 10:
                insights.append({
                    "type": "workload",
                    "label": "This week is slightly heavier than average."
                })

    # Trend
    if weekly.get("trend") is not None:
        t = weekly["trend"]
        if t >= 5:
            insights.append({"type": "trend_up", "label": f"You're up {int(t)}% from last week."})
        elif t <= -25:
            insights.append({"type": "trend_down",
                              "label": "Looks like this week slowed down. Consider a lighter load next week."})

    # Strong consistency rule
    if yesterday_pct is not None and yesterday_pct >= 90:
        # Check 7-day
        past_7 = [_completion_pct((_date.today() - timedelta(days=i)).isoformat()) for i in range(1, 8)]
        past_7 = [p for p in past_7 if p is not None]
        if past_7 and all(p >= 90 for p in past_7):
            insights.append({"type": "habit", "label": "You're building a healthy habit. Keep it going."})

    return {
        "insights": insights[:4],  # cap to 4 for the greeting panel
        "streak": streak,
    }


# ── Full insights payload ──────────────────────────────────────────────────────

def get_all_insights() -> dict:
    """Combined payload used by the /api/insights endpoint."""
    return {
        "greeting": get_greeting_insights(),
        "weekly": get_weekly_summary(),
        "routine_health": get_routine_health(),
    }
