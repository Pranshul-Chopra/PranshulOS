# ── notifier.py ───────────────────────────────────────────────────────────────
# Fires Windows toast notifications at 11 PM for pending tasks.
# Runs in a background daemon thread — never blocks the main app.
#
# Schedule:
#   23:00 — main reminder listing all incomplete tasks
#   23:30 — final nudge if still undone

import threading
import time
from datetime import datetime, date


def _notify(title: str, message: str, timeout: int = 8, launch_url: str = "") -> None:
    """Fire a Windows toast. Prefers winotify (supports click-to-open-URL),
    falls back to plyer, then prints to console."""
    try:
        from winotify import Notification, audio
        toast = Notification(
            app_id="PranshulOS",
            title=title,
            msg=message,
            duration="short" if timeout <= 7 else "long",
            launch=launch_url or "",
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
        return
    except ImportError:
        pass  # winotify not installed — fall through to plyer
    except Exception as e:
        print(f"[notifier] winotify error: {e}")

    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="PranshulOS",
            timeout=timeout,
        )
    except ImportError:
        print(f"[notifier] plyer not installed — pip install plyer")
        print(f"[notifier] would show: {title} — {message}")
    except Exception as e:
        print(f"[notifier] error: {e}")


def _get_pending() -> list[str]:
    try:
        import db
        today = date.today().isoformat()
        tasks = db.get_tasks()
        return [t["text"] for t in tasks if not t.get("done") and t.get("date", today) <= today]
    except Exception as e:
        print(f"[notifier] failed to fetch tasks: {e}")
        return []


def _get_due_tickets() -> list[dict]:
    try:
        import db
        today = date.today().isoformat()
        return db.get_pending_tickets_due_on(today)
    except Exception as e:
        print(f"[notifier] failed to fetch due tickets: {e}")
        return []


def _build_message(tasks: list[str]) -> str:
    if not tasks:
        return ""
    if len(tasks) == 1:
        return f"Still open: {tasks[0]}"
    lines = "\n".join(f"• {t}" for t in tasks[:3])
    if len(tasks) > 3:
        lines += f"\n…and {len(tasks) - 3} more"
    return lines


def _fire_main() -> None:
    pending = _get_pending()
    if not pending:
        return
    count = len(pending)
    _notify(
        f"🔔 {count} task{'s' if count > 1 else ''} still pending",
        _build_message(pending),
        timeout=10,
    )
    print(f"[notifier] 11 PM reminder — {count} task(s)")


def _fire_nudge() -> None:
    pending = _get_pending()
    if not pending:
        return
    count = len(pending)
    _notify(
        f"⏰ Last call — {count} task{'s' if count > 1 else ''} unfinished",
        _build_message(pending),
        timeout=10,
    )
    print(f"[notifier] 11:30 PM nudge — {count} task(s)")


def _fire_due_ticket_reminder() -> None:
    due_tickets = _get_due_tickets()
    if not due_tickets:
        return
    lines = "\n".join(f"• {t['subject']}" for t in due_tickets[:5])
    if len(due_tickets) > 5:
        lines += f"\n…and {len(due_tickets) - 5} more"
    _notify(
        "📌 Tickets due today",
        lines,
        timeout=10,
    )
    print(f"[notifier] due reminder — {len(due_tickets)} ticket(s)")


def _prune_completed_tickets() -> None:
    try:
        import db
        removed = db.delete_done_tickets()
        if removed:
            print(f"[notifier] pruned {removed} completed ticket(s)")
    except Exception as e:
        print(f"[notifier] failed to prune completed tickets: {e}")


def _loop() -> None:
    fired: dict[str, bool] = {}
    print("[notifier] started — watching 23:00 and 23:30 daily")
    while True:
        try:
            now   = datetime.now()
            today = now.date().isoformat()
            hhmm  = now.hour * 100 + now.minute

            k1 = f"{today}_2300"
            k2 = f"{today}_2330"
            k3 = f"{today}_due"
            k4 = f"{today}_prune"

            if 2300 <= hhmm <= 2304 and not fired.get(k1):
                fired[k1] = True
                _fire_main()

            if 2330 <= hhmm <= 2334 and not fired.get(k2):
                fired[k2] = True
                _fire_nudge()

            if 0 <= hhmm <= 4 and not fired.get(k3):
                fired[k3] = True
                _fire_due_ticket_reminder()

            if now.weekday() == 6 and 0 <= hhmm <= 4 and not fired.get(k4):
                fired[k4] = True
                _prune_completed_tickets()

            # prune old keys
            for k in list(fired):
                if not k.startswith(today):
                    del fired[k]

        except Exception as e:
            print(f"[notifier] loop error: {e}")

        time.sleep(30)


def _fire_startup() -> None:
    """Fires once on app launch if there are pending tasks for today."""
    pending = _get_pending()
    if not pending:
        return
    count = len(pending)
    _notify(
        f"PranshulOS — {count} task{'s' if count > 1 else ''} pending today",
        _build_message(pending),
        timeout=8,
    )
    print(f"[notifier] startup reminder — {count} task(s)")


def start() -> None:
    # Fire startup reminder immediately (in a thread so it doesn't block launch)
    threading.Thread(target=_fire_startup, daemon=True, name="task-notifier-startup").start()
    # Then start the 11 PM loop
    threading.Thread(target=_loop, daemon=True, name="task-notifier").start()


def test_notification() -> None:
    _notify(
        "PranshulOS — Test",
        "Notifications are working! Task reminders fire at 11 PM.",
        timeout=6,
    )


RELEASES_PAGE = "https://pranshul-chopra.github.io/PranshulOS-/"

def notify_update_available(version: str, url: str) -> None:
    """Called by updater.py when a newer version is found on the manifest.
    Clicking the toast opens the releases page in the default browser."""
    _notify(
        f"🚀 PranshulOS v{version} is available",
        "Click to open the releases page.",
        timeout=10,
        launch_url=RELEASES_PAGE,
    )