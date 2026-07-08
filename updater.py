"""
updater.py — PranshulOS
Lightweight, non-blocking version check against a hosted manifest.

This app is local-first and must work fully offline. The check below
NEVER blocks startup and NEVER raises — any failure (no internet, host
down, bad JSON) is swallowed silently and the app just runs normally.
"""
from pathlib import Path

# Bump this on every release you cut. Also bump the version string in
# your PyInstaller build / GitHub tag to match.
CURRENT_VERSION = "2.0.0"

# Raw JSON file living in your GitHub repo (or a GitHub Release asset URL).
# Example using a raw file on the main branch:
#   https://raw.githubusercontent.com/<you>/<repo>/main/version.json
MANIFEST_URL = "https://raw.githubusercontent.com/YOURUSER/PranshulOS/main/version.json"

_TIMEOUT_SECONDS = 2.5  # fail fast — don't let a slow network hold up the app


def _parse_version(v: str) -> tuple:
    try:
        return tuple(int(p) for p in v.strip().split("."))
    except Exception:
        return (0,)


def check_for_update() -> dict | None:
    """
    Returns a dict like {"version": "2.1.0", "url": "...", "notes": "..."}
    if a newer version is available, else None. Never raises.
    """
    try:
        import requests
    except ImportError:
        return None

    try:
        resp = requests.get(MANIFEST_URL, timeout=_TIMEOUT_SECONDS)
        if resp.status_code != 200:
            return None
        data = resp.json()
        latest = data.get("latest_version", "0.0.0")
        if _parse_version(latest) > _parse_version(CURRENT_VERSION):
            return {
                "version": latest,
                "url": data.get("download_url", ""),
                "notes": data.get("notes", ""),
            }
    except Exception:
        # Offline, DNS failure, malformed JSON, whatever — just skip silently.
        pass
    return None


def check_and_notify() -> None:
    """
    Runs the check in a background thread and fires a toast notification
    (via notifier.py's plyer wiring) if an update is found. Call this once
    at startup; it never blocks the caller.
    """
    import threading

    def _worker():
        result = check_for_update()
        if not result:
            return
        try:
            import notifier
            notifier.notify_update_available(result["version"], result["url"])
        except Exception:
            pass  # notification is a nice-to-have, never fatal

    threading.Thread(target=_worker, daemon=True).start()
