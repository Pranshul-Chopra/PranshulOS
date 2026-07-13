# ── db.py ─────────────────────────────────────────────────────────────────────
# SQLite database — tasks, goals, docs.
# No chat/memory tables.

import os
import sqlite3
import threading
from queue import Queue
from pathlib import Path


def _user_data_dir() -> Path:
    """
    Persistent, per-user, per-machine data directory — independent of wherever
    the app happens to be installed/extracted. This matters because a
    PyInstaller build's own folder can be replaced/reinstalled on update, and
    a --onefile build's __file__ lives in a temp dir that's wiped every run.
    """
    base = os.getenv("LOCALAPPDATA") or str(Path.home() / ".pranshulos")
    data_dir = Path(base) / "PranshulOS"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


DB_PATH = _user_data_dir() / "pranshulos.db"

# One-time migration: if an old DB sits next to this file (pre-LOCALAPPDATA
# builds) and nothing exists yet at the new location, move it over so
# existing installs (including yours) don't lose data on upgrade.
_legacy_path = Path(__file__).parent / "pranshulos.db"
if _legacy_path.exists() and not DB_PATH.exists():
    import shutil
    shutil.copy2(_legacy_path, DB_PATH)


SCHEMA_VERSION = 1


# ── Connection pool ────────────────────────────────────────────────────────────

class _Pool:
    def __init__(self, size: int = 3):
        self._q: Queue = Queue(maxsize=size)
        for _ in range(size):
            self._q.put(self._make())

    def _make(self) -> sqlite3.Connection:
        con = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=5.0)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA foreign_keys=ON")
        return con

    def get(self) -> sqlite3.Connection:
        return self._q.get(timeout=5.0)

    def put(self, con: sqlite3.Connection) -> None:
        try:
            self._q.put(con, block=False)
        except Exception:
            try: con.close()
            except Exception: pass

_pool = _Pool()


class _Conn:
    def __init__(self):
        self.con = None

    def __enter__(self):
        self.con = _pool.get()
        return self.con

    def __exit__(self, exc_type, *_):
        if self.con:
            try:
                if exc_type: self.con.rollback()
                else:        self.con.commit()
            except Exception: pass
            _pool.put(self.con)

def _conn() -> _Conn:
    return _Conn()


# ── Schema ─────────────────────────────────────────────────────────────────────

def _get_schema_version(con: sqlite3.Connection) -> int:
    con.execute("CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT)")
    row = con.execute("SELECT value FROM schema_meta WHERE key = 'version'").fetchone()
    return int(row["value"]) if row else 0


def _set_schema_version(con: sqlite3.Connection, version: int) -> None:
    con.execute(
        "INSERT INTO schema_meta (key, value) VALUES ('version', ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (str(version),)
    )


def _run_migrations(con: sqlite3.Connection) -> None:
    """
    Add future schema changes here as sequential steps, e.g.:

        current = _get_schema_version(con)
        if current < 2:
            con.execute("ALTER TABLE dashboard_tasks ADD COLUMN priority INTEGER DEFAULT 0")
        if current < 3:
            ...

    Then bump SCHEMA_VERSION at the top of this file. CREATE TABLE IF NOT
    EXISTS below already handles brand-new installs safely — this is only
    for changes to tables that already exist on someone's machine.
    """
    current = _get_schema_version(con)
    if current < SCHEMA_VERSION:
        _set_schema_version(con, SCHEMA_VERSION)


def init_db() -> None:
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS dashboard_tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                text        TEXT    NOT NULL,
                date        TEXT    NOT NULL,
                done        INTEGER NOT NULL DEFAULT 0,
                done_date   TEXT,
                stacked     INTEGER NOT NULL DEFAULT 0,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS dashboard_goals (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                text        TEXT    NOT NULL,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_tasks_date
                ON dashboard_tasks(date);

            CREATE TABLE IF NOT EXISTS docs (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                title      TEXT NOT NULL DEFAULT 'Untitled',
                content    TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
        _run_migrations(con)


# ── Tasks ──────────────────────────────────────────────────────────────────────

def get_tasks() -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM dashboard_tasks ORDER BY created_at ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def add_task(text: str, date: str) -> dict:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO dashboard_tasks (text, date) VALUES (?, ?)", (text, date)
        )
        row = con.execute(
            "SELECT * FROM dashboard_tasks WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return dict(row)


def update_task(task_id: int, **fields) -> dict | None:
    allowed = {"done", "done_date", "stacked", "text"}
    updates = {k: v for k, v in fields.items() if k in allowed}
    if not updates:
        return None
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [task_id]
    with _conn() as con:
        con.execute(f"UPDATE dashboard_tasks SET {set_clause} WHERE id = ?", values)
        row = con.execute(
            "SELECT * FROM dashboard_tasks WHERE id = ?", (task_id,)
        ).fetchone()
    return dict(row) if row else None


def delete_task(task_id: int) -> bool:
    with _conn() as con:
        cur = con.execute("DELETE FROM dashboard_tasks WHERE id = ?", (task_id,))
    return cur.rowcount > 0


def rollover_tasks(today: str) -> None:
    """Remove done tasks from previous days; mark old pending as stacked."""
    with _conn() as con:
        con.execute(
            "DELETE FROM dashboard_tasks WHERE done = 1 AND done_date != ?", (today,)
        )
        con.execute(
            """UPDATE dashboard_tasks SET stacked = 1
               WHERE done = 0 AND stacked = 0 AND date < ?""",
            (today,)
        )


# ── Goals ──────────────────────────────────────────────────────────────────────

def get_goals() -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM dashboard_goals ORDER BY created_at ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def add_goal(text: str) -> dict:
    with _conn() as con:
        cur = con.execute("INSERT INTO dashboard_goals (text) VALUES (?)", (text,))
        row = con.execute(
            "SELECT * FROM dashboard_goals WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
    return dict(row)


def delete_goal(goal_id: int) -> bool:
    with _conn() as con:
        cur = con.execute("DELETE FROM dashboard_goals WHERE id = ?", (goal_id,))
    return cur.rowcount > 0


# ── Docs ───────────────────────────────────────────────────────────────────────

def get_all_docs() -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT id, title, content, created_at, updated_at FROM docs ORDER BY updated_at DESC"
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["content"] = (d.get("content") or "")[:120]
        result.append(d)
    return result


def get_doc(doc_id: int) -> dict | None:
    with _conn() as con:
        row = con.execute("SELECT * FROM docs WHERE id = ?", (doc_id,)).fetchone()
    return dict(row) if row else None


def create_doc(title: str = "Untitled") -> dict:
    with _conn() as con:
        cur = con.execute("INSERT INTO docs (title, content) VALUES (?, '')", (title,))
        row = con.execute("SELECT * FROM docs WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def update_doc(doc_id: int, title: str | None = None, content: str | None = None) -> dict | None:
    fields, vals = [], []
    if title   is not None: fields.append("title = ?");              vals.append(title)
    if content is not None: fields.append("content = ?");            vals.append(content)
    if not fields:
        return get_doc(doc_id)
    fields.append("updated_at = datetime('now')")
    vals.append(doc_id)
    with _conn() as con:
        con.execute(f"UPDATE docs SET {', '.join(fields)} WHERE id = ?", vals)
        row = con.execute("SELECT * FROM docs WHERE id = ?", (doc_id,)).fetchone()
    return dict(row) if row else None


def delete_doc(doc_id: int) -> bool:
    with _conn() as con:
        cur = con.execute("DELETE FROM docs WHERE id = ?", (doc_id,))
    return cur.rowcount > 0
