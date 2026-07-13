# PranshulOS

A local-first, Windows desktop productivity shell — built with Flask, Electron, and SQLite. No cloud, no server, no account required. Everything runs and stays on your machine.

## What it does

- **Home** — quick-launch tiles and a natural-language command bar ("bored", "github", "spotify"...) that opens the general web apps you actually use
- **Dashboard** — daily tasks and longer-term goals, with automatic day-to-day rollover for anything left unfinished
- **Docs** — a lightweight local notes/writing space with a document list view and full editor
- **Persistent sidebar** — navigate between Home, Dashboard, and Docs at any time without losing context, plus quick-access app launchers always visible on the left
- **Notifications** — Windows toast reminders for pending tasks (11 PM + 11:30 PM nudge), and a background check for new app versions

## Why v2.0 looks different from earlier builds

Earlier versions of this project experimented with an embedded AI chatbot (local LLM via Ollama) and a "Screen Assist" feature that captured your screen and fed it to a vision model for contextual help. Both were removed in v2.0. Reasoning:

- **Structural integrity** — bolting a chat interface, a memory/retrieval pipeline, and a vision pipeline onto what's fundamentally a lightweight desktop shell turned a ~1,000-line app into something with far more moving parts than its actual job required. Every new feature increased the surface area for bugs unrelated to the app's core purpose.
- **Maintainability** — a chatbot with memory retrieval, tool routing, and streaming responses is a genuinely different category of software than a task/dashboard app. Maintaining both well, alone, meant neither got the attention it deserved.
- **Server/runtime cost** — running a local LLM well means real GPU/CPU overhead on every launch, even for people who just want to check their task list. That's a heavy default cost to impose on every user for a feature only some of them would use.
- **Local-first philosophy** — this project's actual value is being simple, fast, and entirely yours. AI chat and screen capture features pulled it toward being a different product entirely. Cutting them was a decision to do fewer things well rather than many things adequately.

The AI-assisted concepts explored here may return later as a separate, standalone project (not bundled into a task manager), where they can be designed and maintained properly on their own terms.

## What changed in v2.1 specifically

- **Migrated from pywebview to Electron** — pywebview's Windows backend requires a fragile pythonnet/.NET bridge that consistently broke under PyInstaller packaging across multiple Python versions and build configurations. Electron uses bundled Chromium with no .NET dependency, making the packaged app reliable on any Windows machine.
- **Proper Windows installer** — ships as an NSIS installer (`PranshulOS Setup 2.1.0.exe`) that creates Desktop and Start Menu shortcuts automatically. No zip extraction, no bat files, no manual setup.
- **Persistent sidebar navigation** — single-page shell with a fixed left sidebar; Home/Dashboard/Docs content swaps in the right panel without full page reloads.
- **Docs redesigned** — list-first view showing all documents as cards with content previews. Click a card to open the full editor. "← back" returns to the list.
- **Flask routes replace JS bridge** — all app-launcher actions previously handled by `window.pywebview.api` are now clean Flask endpoints (`/launch/<app>`), making the frontend simpler and more portable.

## What changed in v2.0

- Removed all local desktop-app launchers (Outlook, work-mode shortcuts, direct Steam/Warframe launches) in favor of plain web links for general-purpose apps (YouTube, Spotify, Discord, GitHub, LinkedIn, Gmail, Reddit, WhatsApp, Twitch, Roblox, ChatGPT)
- Fixed hardcoded, machine-specific file paths so the app actually runs on machines other than the original dev machine
- Moved the SQLite database to `%LOCALAPPDATA%`, so user data survives reinstalls and future updates
- Added a lightweight, non-blocking update checker — pings a version manifest on startup, shows a toast if a newer release is available, fails silently offline

## Installation

1. Go to [Releases](https://github.com/Pranshul-Chopra/PranshulOS/releases) and download the latest `PranshulOS Setup X.X.X.exe`
2. Run the installer — it creates a Desktop shortcut and Start Menu entry automatically
3. Launch from the Desktop shortcut

Windows SmartScreen may flag the installer since it isn't code-signed — click **"More info" → "Run anyway"**.

## Tech stack

- **Backend:** Flask (local-only, bound to `127.0.0.1`)
- **Shell:** Electron (Chromium window, no pythonnet/.NET dependency)
- **Storage:** SQLite, stored in `%LOCALAPPDATA%\PranshulOS`
- **Notifications:** plyer (native Windows toasts)
- **Packaging:** PyInstaller (headless Flask backend) + electron-builder (NSIS installer)

## Development

```bash
# Install Python dependencies
pip install -r requirements.txt

# Terminal 1 — start Flask backend
python main.py

# Terminal 2 — start Electron window
cd electron
npm install
npx electron .
```

## Building a release

```bash
# Requires: Python 3.11 venv (venv311) + Node.js

py -3.11 -m venv venv311
venv311\Scripts\activate
pip install -r requirements.txt pyinstaller pyinstaller-hooks-contrib
mkdir static
cd electron && npm install && cd ..

$env:CSC_IDENTITY_AUTO_DISCOVERY="false"
.\build.bat
# Output: release\PranshulOS Setup X.X.X.exe
```

## License

Personal project — license terms TBD.
