# PranshulOS

A local-first, Windows desktop productivity shell — built with Flask, Electron, and SQLite. No cloud, no server, no account required. Everything runs and stays on your machine.

## What it does

- **Home** — a configurable quick-launch grid and a natural-language command bar ("bored", "github", "spotify"...) that opens the web apps you actually use. Add your own launchers with a name, icon, and URL — they persist across sessions and can be removed any time.
- **Dashboard** — daily tasks and longer-term goals, with automatic day-to-day rollover for anything left unfinished
- **Docs** — a lightweight local notes/writing space with a document list view and full editor
- **Persistent sidebar** — navigate between Home, Dashboard, and Docs at any time without losing context
- **Notifications** — Windows toast reminders for pending tasks (11 PM + 11:30 PM nudge), and a background check for new app versions

## What changed in v2.2

- **Configurable launchers** — the quick-launch grid on the home page now supports user-defined launchers. Click the `+` tile, give it a name, an emoji icon, and a URL. Custom launchers are stored in the local SQLite database and appear alongside the built-in ones. Hover any custom launcher to reveal a delete button.
- **Sidebar cleanup** — the Apps section (hardcoded launcher buttons in the sidebar) has been removed. The sidebar is now navigation-only: Home, Dashboard, Docs. This keeps the panel clean and reserves space for future pages.
- **Home page redesign** — launcher grid changed from a 2-column list to a 4-column icon grid. Font sizes increased, letter-spacing reduced, subtitle and nav labels switched from monospace to sans-serif. The command bar is now a single integrated input pill.
- **RAM fix (BUG-2026-002)** — launcher clicks previously called `webbrowser.open()`, which spawns a fresh browser process (300–600 MB) on every click. Replaced with `cmd /c start`, which routes the URL to the already-running browser as a new tab. RAM impact per launch is now negligible.

## What changed in v2.1

- **Migrated from pywebview to Electron** — pywebview's Windows backend requires a fragile pythonnet/.NET bridge that consistently broke under PyInstaller packaging. Electron uses bundled Chromium with no .NET dependency, making the packaged app reliable on any Windows machine.
- **Proper Windows installer** — ships as an NSIS installer (`PranshulOS Setup 2.1.0.exe`) that creates Desktop and Start Menu shortcuts automatically. No zip extraction, no bat files, no manual setup.
- **Persistent sidebar navigation** — single-page shell with a fixed left sidebar; page content swaps in the right panel without full page reloads.
- **Docs redesigned** — list-first view showing all documents as cards with content previews. Click a card to open the full editor. "← back" returns to the list.
- **Flask routes replace JS bridge** — all app-launcher actions previously handled by `window.pywebview.api` are now clean Flask endpoints (`/launch/<app>`).

## Why v2.0 looks different from earlier builds

Earlier versions experimented with an embedded AI chatbot (local LLM via Ollama) and a "Screen Assist" feature that captured your screen and fed it to a vision model. Both were removed in v2.0:

- **Structural integrity** — bolting a chat interface, memory pipeline, and vision pipeline onto a lightweight desktop shell turned a ~1,000-line app into something with far more moving parts than its actual job required.
- **Maintainability** — a chatbot with memory retrieval, tool routing, and streaming responses is a genuinely different category of software than a task/dashboard app. Maintaining both well, alone, meant neither got the attention it deserved.
- **Runtime cost** — running a local LLM means real GPU/CPU overhead on every launch, even for users who just want to check their task list.
- **Local-first philosophy** — this project's value is being simple, fast, and entirely yours. The AI features pulled it toward being a different product. Cutting them was a decision to do fewer things well.

The AI concepts explored here may return as a separate standalone project, where they can be designed and maintained properly on their own terms.

## What changed in v2.0

- Removed local desktop-app launchers in favor of plain web links for general-purpose apps
- Fixed hardcoded, machine-specific file paths
- Moved the SQLite database to `%LOCALAPPDATA%` so user data survives reinstalls
- Added a lightweight, non-blocking update checker

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
# Requires: Python 3.13 venv (venv313) + Node.js

py -3.13 -m venv venv313
venv313\Scripts\activate
pip install -r requirements.txt pyinstaller pyinstaller-hooks-contrib
mkdir static
cd electron && npm install && cd ..

$env:CSC_IDENTITY_AUTO_DISCOVERY="false"
.\build.bat
# Output: release\PranshulOS Setup X.X.X.exe
```

## License

Personal project — license terms TBD.
