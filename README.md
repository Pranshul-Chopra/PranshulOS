# PranshulOS

A local-first, Windows desktop productivity shell — built with Flask, pywebview, and SQLite. No cloud, no server, no account required. Everything runs and stays on your machine.

## What it does

- **Home** — quick-launch tiles and a natural-language command bar ("bored", "github", "spotify"...) that opens the general web apps you actually use
- **Dashboard** — daily tasks and longer-term goals, with automatic day-to-day rollover for anything left unfinished
- **Docs** — a lightweight local notes/writing space
- **Notifications** — Windows toast reminders for pending tasks (11 PM + 11:30 PM nudge), and a background check for new app versions

## Why v2.0 looks different from earlier builds

Earlier versions of this project experimented with an embedded AI chatbot (local LLM via Ollama) and a "Screen Assist" feature that captured your screen and fed it to a vision model for contextual help. Both were removed in this release. Reasoning:

- **Structural integrity** — bolting a chat interface, a memory/retrieval pipeline, and a vision pipeline onto what's fundamentally a lightweight desktop shell turned a ~1,000-line app into something with far more moving parts than its actual job required. Every new feature increased the surface area for bugs unrelated to the app's core purpose.
- **Maintainability** — a chatbot with memory retrieval, tool routing, and streaming responses is a genuinely different category of software than a task/dashboard app. Maintaining both well, alone, meant neither got the attention it deserved.
- **Server/runtime cost** — running a local LLM well means real GPU/CPU overhead on every launch, even for people who just want to check their task list. That's a heavy default cost to impose on every user for a feature only some of them would use.
- **Local-first philosophy** — this project's actual value is being simple, fast, and entirely yours. AI chat and screen capture features pulled it toward being a different product entirely. Cutting them was a decision to do fewer things well rather than many things adequately.

The AI-assisted concepts explored here may return later as a **separate, standalone project** (not bundled into a task manager), where they can be designed and maintained properly on their own terms.

## What changed in v2.0 specifically

- Removed all local desktop-app launchers (Outlook, work-mode shortcuts, direct Steam/Warframe launches, etc.) in favor of plain web links for general-purpose apps (YouTube, Spotify, Discord, GitHub, LinkedIn, Gmail, Reddit, WhatsApp, Twitch, Roblox, ChatGPT)
- Fixed hardcoded, machine-specific file paths so the app actually runs on machines other than the original dev machine
- Moved the SQLite database to `%LOCALAPPDATA%`, so user data survives reinstalls and future updates instead of living next to replaceable app code
- Added a lightweight, non-blocking update checker — the app pings a version manifest on startup and shows a toast if a newer release is available, and fails silently if you're offline
- Packaged as a standalone Windows executable (PyInstaller) — no Python installation required to run it

## Installation

1. Go to [Releases](../../releases) and download the latest `PranshulOS-vX.X.X.zip`
2. Extract it anywhere
3. Double-click `Launch PranshulOS.bat`

First launch may trigger a Windows SmartScreen warning since the executable isn't code-signed — click **"More info" → "Run anyway"**.

## Tech stack

- **Backend:** Flask (local-only, bound to `127.0.0.1`)
- **Shell:** pywebview (native window, no Electron/Chromium overhead)
- **Storage:** SQLite, stored in `%LOCALAPPDATA%\PranshulOS`
- **Notifications:** plyer (native Windows toasts)
- **Packaging:** PyInstaller (`--onedir` build)

## Development

```bash
pip install -r requirements.txt
python main.py
```

To build a distributable executable:
```bash
pip install pyinstaller
pyinstaller PranshulOS.spec
```

## License

Personal project — license terms TBD.
