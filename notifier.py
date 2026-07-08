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


def _notify(title: str, message: str, timeout: int = 8) -> None:
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

            if 2300 <= hhmm <= 2304 and not fired.get(k1):
                fired[k1] = True
                _fire_main()

            if 2330 <= hhmm <= 2334 and not fired.get(k2):
                fired[k2] = True
                _fire_nudge()

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


def notify_update_available(version: str, url: str) -> None:
    """Called by updater.py when a newer version is found on the manifest."""
    _notify(
        f"🚀 PranshulOS v{version} is available",
        f"Click to download: {url}" if url else "A new version is available.",
        timeout=10,
    )
