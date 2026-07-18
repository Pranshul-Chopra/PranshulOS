# ── routes.py ─────────────────────────────────────────────────────────────────
# Flask routes: Home, Dashboard, Docs.

import os
from flask import Blueprint, render_template, render_template_string, request, jsonify
from datetime import datetime as _dt, date as _date

import db

bp = Blueprint("main", __name__, template_folder="templates")

@bp.route("/")
def shell():
    return render_template("shell.html")



# ── Home ───────────────────────────────────────────────────────────────────────

_HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Home — PranshulOS</title>
  <link rel="stylesheet" href="/static/fonts/ibmflex.css"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0c0c0c; --surface: #141414; --surface2: #1a1a1a;
      --border: #242424; --border2: #2e2e2e;
      --text: #e2e0db; --text2: #7a7872; --text3: #3e3d3a;
      --amber: #e8a84c; --amber-dim: #6b4d1c; --amber-glow: rgba(232,168,76,0.06);
      --radius: 10px;
      --mono: 'IBM Plex Mono', monospace; --sans: 'IBM Plex Sans', sans-serif;
    }
    html, body {
      height: 100%; background: var(--bg); color: var(--text);
      font-family: var(--sans); -webkit-font-smoothing: antialiased;
      font-size: 15px; line-height: 1.6;
    }
    .shell { max-width: 600px; margin: 0 auto; padding: 52px 28px 40px; }

    .greeting {
      font-size: 26px; font-weight: 400; letter-spacing: -0.025em;
      margin-bottom: 8px; color: var(--text); line-height: 1.25;
    }
    .greeting em { color: var(--amber); font-style: normal; }
    .sub { font-size: 14px; color: var(--text2); margin-bottom: 44px; font-weight: 400; }

    .section-label {
      font-family: var(--mono); font-size: 10px; font-weight: 500;
      color: var(--text3); letter-spacing: 0.07em;
      text-transform: uppercase; margin-bottom: 14px;
    }

    /* ── Grid ── */
    .launch-grid {
      display: grid; grid-template-columns: repeat(4, 1fr);
      gap: 8px; margin-bottom: 36px;
    }

    /* ── Built-in launcher btn ── */
    .launch-btn {
      position: relative;
      padding: 18px 12px 16px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border2);
      color: var(--text); font-family: var(--sans);
      text-align: center; cursor: pointer;
      transition: background 0.14s, border-color 0.14s, transform 0.1s;
      display: flex; flex-direction: column; align-items: center; gap: 9px;
    }
    .launch-btn:hover {
      background: var(--surface2); border-color: var(--amber-dim);
      transform: translateY(-1px);
    }
    .launch-btn:active { transform: translateY(0); }
    .launch-btn .icon { font-size: 22px; line-height: 1; }
    .launch-btn .label {
      font-size: 12px; font-weight: 400; color: var(--text2);
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      max-width: 100%;
    }

    /* ── Delete button (appears on hover over custom launchers) ── */
    .launch-btn .del-x {
      position: absolute; top: 5px; right: 5px;
      width: 18px; height: 18px; border-radius: 50%;
      background: #2a2a2a; border: 1px solid #3a3a3a;
      color: var(--text2); font-size: 11px; line-height: 18px;
      text-align: center; cursor: pointer;
      opacity: 0; transition: opacity 0.12s;
      display: flex; align-items: center; justify-content: center;
      z-index: 2;
    }
    .launch-btn:hover .del-x { opacity: 1; }
    .launch-btn .del-x:hover { background: #c0392b; border-color: #c0392b; color: #fff; }

    /* ── Add button ── */
    .add-btn {
      padding: 18px 12px 16px; border-radius: var(--radius);
      background: var(--surface); border: 1px dashed var(--border2);
      color: var(--text3); font-family: var(--sans);
      text-align: center; cursor: pointer;
      transition: background 0.14s, border-color 0.14s, transform 0.1s;
      display: flex; flex-direction: column; align-items: center; gap: 9px;
    }
    .add-btn:hover {
      background: var(--surface2); border-color: var(--amber-dim);
      transform: translateY(-1px);
    }
    .add-btn:active { transform: translateY(0); }
    .add-btn .add-bubble {
      width: 36px; height: 36px; border-radius: 50%;
      background: var(--amber); display: flex; align-items: center;
      justify-content: center; font-size: 20px; line-height: 1;
      color: #0c0c0c; font-weight: 300; flex-shrink: 0;
    }
    .add-btn .label {
      font-size: 12px; font-weight: 400; color: var(--text3);
    }

    /* ── Modal overlay ── */
    .modal-overlay {
      position: fixed; inset: 0;
      background: rgba(0,0,0,0.7);
      display: flex; align-items: center; justify-content: center;
      z-index: 999; opacity: 0; pointer-events: none;
      transition: opacity 0.15s;
    }
    .modal-overlay.open { opacity: 1; pointer-events: all; }
    .modal {
      background: #181818; border: 1px solid var(--border2);
      border-radius: 14px; padding: 28px 28px 24px;
      width: 360px; max-width: calc(100vw - 48px);
      transform: translateY(8px); transition: transform 0.15s;
    }
    .modal-overlay.open .modal { transform: translateY(0); }
    .modal-title {
      font-size: 15px; font-weight: 500; color: var(--text);
      margin-bottom: 20px;
    }

    /* ── Modal fields ── */
    .field-label {
      font-family: var(--mono); font-size: 10px; color: var(--text3);
      letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px;
    }
    .field-group { margin-bottom: 14px; }
    .field-input {
      width: 100%; padding: 10px 13px; border-radius: 8px;
      background: var(--surface); border: 1px solid var(--border2);
      color: var(--text); font-family: var(--sans); font-size: 14px;
      outline: none; transition: border-color 0.14s;
    }
    .field-input:focus { border-color: var(--amber-dim); }
    .field-input::placeholder { color: var(--text3); }
    .field-hint {
      font-size: 11px; color: var(--text3); margin-top: 5px;
      font-family: var(--mono); line-height: 1.5;
    }

    /* ── Modal actions ── */
    .modal-actions {
      display: flex; gap: 8px; margin-top: 20px;
    }
    .modal-cancel {
      flex: 1; padding: 9px; border-radius: 8px; border: 1px solid var(--border2);
      background: transparent; color: var(--text2); font-family: var(--sans);
      font-size: 13px; cursor: pointer; transition: background 0.12s;
    }
    .modal-cancel:hover { background: var(--surface2); }
    .modal-save {
      flex: 2; padding: 9px; border-radius: 8px; border: none;
      background: var(--amber); color: #0c0c0c; font-family: var(--sans);
      font-size: 13px; font-weight: 500; cursor: pointer; transition: opacity 0.12s;
    }
    .modal-save:hover { opacity: 0.88; }

    /* ── Divider / cmd bar / log (unchanged) ── */
    .divider { height: 1px; background: var(--border); margin: 32px 0; }
    .cmd-bar {
      display: flex; gap: 8px; align-items: center;
      background: var(--surface); border: 1px solid var(--border2);
      border-radius: var(--radius); padding: 4px 4px 4px 16px;
      transition: border-color 0.15s;
    }
    .cmd-bar:focus-within { border-color: var(--amber-dim); }
    .cmd-input {
      flex: 1; background: transparent; border: none; outline: none;
      color: var(--text); font-family: var(--sans); font-size: 14px;
      padding: 8px 0; line-height: 1.4;
    }
    .cmd-input::placeholder { color: var(--text3); }
    .cmd-go {
      padding: 8px 18px; border-radius: 7px;
      background: var(--amber); color: #0c0c0c; border: none;
      font-family: var(--sans); font-size: 13px; font-weight: 500;
      cursor: pointer; transition: opacity 0.14s; white-space: nowrap; flex-shrink: 0;
    }
    .cmd-go:hover { opacity: 0.88; }
    .log {
      margin-top: 12px; padding: 13px 16px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border);
      font-family: var(--mono); font-size: 12px; color: var(--text2);
      min-height: 44px; line-height: 2;
    }
    .log .entry { animation: fadein 0.18s ease; }
    .log .entry.you { color: var(--text); }
    .log .entry.reply { color: var(--amber); }
    @keyframes fadein { from { opacity:0; transform: translateY(4px); } to { opacity:1; transform:none; } }
  </style>
</head>
<body>
<div class="shell">
  <div class="greeting">{{ greeting }}</div>
  <div class="sub">What do you want to open?</div>

  <div class="section-label">Quick launch</div>
  <div class="launch-grid" id="launch-grid">
    <!-- built-in launchers -->
    <button class="launch-btn" onclick="launch('youtube')">
      <span class="icon">🎬</span><span class="label">YouTube</span>
    </button>
    <button class="launch-btn" onclick="launch('spotify')">
      <span class="icon">🎵</span><span class="label">Spotify</span>
    </button>
    <button class="launch-btn" onclick="launch('whatsapp')">
      <span class="icon">💬</span><span class="label">WhatsApp</span>
    </button>
    <button class="launch-btn" onclick="launch('discord')">
      <span class="icon">🎮</span><span class="label">Discord</span>
    </button>
    <button class="launch-btn" onclick="launch('github')">
      <span class="icon">🐙</span><span class="label">GitHub</span>
    </button>
    <button class="launch-btn" onclick="launch('linkedin')">
      <span class="icon">🔗</span><span class="label">LinkedIn</span>
    </button>
    <button class="launch-btn" onclick="launch('gmail')">
      <span class="icon">✉️</span><span class="label">Gmail</span>
    </button>
    <button class="launch-btn" onclick="launch('reddit')">
      <span class="icon">👽</span><span class="label">Reddit</span>
    </button>
    <!-- custom launchers injected here by JS -->
    <!-- add button always last -->
    <button class="add-btn" id="add-btn" onclick="openModal()">
      <span class="add-bubble">+</span>
      <span class="label">Add</span>
    </button>
  </div>

  <div class="divider"></div>
  <div class="section-label">Or just tell me</div>
  <div class="cmd-bar">
    <input class="cmd-input" id="inp" placeholder='try "bored", "github", "spotify"…' onkeydown="if(event.key==='Enter') go()"/>
    <button class="cmd-go" onclick="go()">Go</button>
  </div>
  <div class="log" id="log"><span style="color:var(--text3)">→ what do you need?</span></div>
</div>

<!-- ── Add launcher modal ── -->
<div class="modal-overlay" id="modal-overlay" onclick="overlayClick(event)">
  <div class="modal">
    <div class="modal-title">Add launcher</div>

    <div class="field-group">
      <div class="field-label">Name</div>
      <input class="field-input" id="m-name" placeholder="e.g. Notion" maxlength="20"/>
    </div>

    <div class="field-group">
      <div class="field-label">Icon</div>
      <input class="field-input" id="m-icon" placeholder="🚀" maxlength="4"/>
    </div>

    <div class="field-group">
      <div class="field-label">URL</div>
      <input class="field-input" id="m-url" placeholder="https://example.com"/>
    </div>

    <div class="modal-actions">
      <button class="modal-cancel" onclick="closeModal()">Cancel</button>
      <button class="modal-save" onclick="saveCustom()">Add launcher</button>
    </div>
  </div>
</div>

<script>
// ── Built-in launchers ────────────────────────────────────────────────────────
async function launch(appName) {
  try {
    await fetch('/launch/' + appName);
    addLog('→ opened ' + appName, 'reply');
  } catch(e) {
    addLog('→ error opening ' + appName, 'reply');
  }
}

// ── Custom launchers ──────────────────────────────────────────────────────────
async function loadCustom() {
  try {
    const res  = await fetch('/api/launchers');
    const list = await res.json();
    renderCustom(list);
  } catch(e) { console.error('loadCustom', e); }
}

function renderCustom(list) {
  const grid   = document.getElementById('launch-grid');
  const addBtn = document.getElementById('add-btn');
  // remove old custom buttons (keep built-ins + add-btn)
  grid.querySelectorAll('.custom-btn').forEach(el => el.remove());
  // inject before add-btn
  list.forEach(item => {
    const btn = document.createElement('button');
    btn.className = 'launch-btn custom-btn';
    btn.innerHTML = `
      <span class="icon">${item.icon}</span>
      <span class="label">${item.name}</span>
      <span class="del-x" title="Remove">×</span>
    `;
    btn.querySelector('.del-x').addEventListener('click', async (e) => {
      e.stopPropagation();
      await fetch('/api/launchers/' + item.id, { method: 'DELETE' });
      addLog('→ removed ' + item.name, 'reply');
      loadCustom();
    });
    btn.addEventListener('click', async () => {
      try {
        await fetch('/launch/custom/' + item.id);
        addLog('→ opened ' + item.name, 'reply');
      } catch(e) {
        addLog('→ error opening ' + item.name, 'reply');
      }
    });
    grid.insertBefore(btn, addBtn);
  });
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function openModal() {
  document.getElementById('m-name').value = '';
  document.getElementById('m-icon').value = '';
  document.getElementById('m-url').value  = '';
  document.getElementById('modal-overlay').classList.add('open');
  setTimeout(() => document.getElementById('m-name').focus(), 120);
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}

function overlayClick(e) {
  if (e.target === document.getElementById('modal-overlay')) closeModal();
}


async function saveCustom() {
  const name   = document.getElementById('m-name').value.trim();
  const icon   = document.getElementById('m-icon').value.trim() || '🚀';
  const target = document.getElementById('m-url').value.trim();

  if (!name)   { document.getElementById('m-name').focus(); return; }
  if (!target) { document.getElementById('m-url').focus();  return; }

  try {
    const res = await fetch('/api/launchers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, kind: 'url', target, icon })
    });
    if (res.ok) {
      closeModal();
      addLog('→ added ' + name, 'reply');
      loadCustom();
    }
  } catch(e) {
    addLog('→ error saving launcher', 'reply');
  }
}

// close on Escape
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
  if (e.key === 'Enter' && document.getElementById('modal-overlay').classList.contains('open')) {
    saveCustom();
  }
});

// ── Command bar ───────────────────────────────────────────────────────────────
async function go() {
  const inp  = document.getElementById('inp');
  const text = inp.value.trim();
  if (!text) return;
  addLog('you: ' + text, 'you');
  inp.value = '';
  try {
    const res  = await fetch('/api/trigger', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    addLog(data.result ? '→ ' + data.result : "→ didn't catch that — try 'bored', 'github', 'discord'…", 'reply');
  } catch(e) {
    addLog('→ error', 'reply');
  }
}

function addLog(text, cls) {
  const log = document.getElementById('log');
  if (log.querySelector('span')) log.innerHTML = '';
  const el = document.createElement('div');
  el.className = 'entry ' + cls;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}

// ── Expose to window (required for inline onclick inside SPA eval scope) ──────
window.__pageInit   = function() { loadCustom(); };
window.launch       = launch;
window.go           = go;
window.openModal    = openModal;
window.closeModal   = closeModal;
window.overlayClick = overlayClick;
window.saveCustom   = saveCustom;
</script>
</body>
</html>"""


@bp.route("/home")
def home():
    h = _dt.now().hour
    if h < 12:   greeting = "Good morning ☀️"
    elif h < 17: greeting = "Good afternoon 🌤"
    else:        greeting = "Good evening 🌙"
    html = render_template_string(_HOME_HTML, greeting=greeting)
    if request.args.get("fragment"):
        # Extract just the body content for SPA navigation
        import re
        styles = re.findall(r"<style[^>]*>.*?</style>", html, re.DOTALL)
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL)
        body = m.group(1) if m else html
        return "\n".join(styles) + "\n" + body
    return html


# ── Dashboard ──────────────────────────────────────────────────────────────────

@bp.route("/dashboard")
def dashboard():
    if request.args.get("fragment"):
        html = render_template("dashboard.html")
        import re
        styles = re.findall(r"<style[^>]*>.*?</style>", html, re.DOTALL)
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL)
        body = m.group(1) if m else html
        return "\n".join(styles) + "\n" + body
    return render_template("dashboard.html")


@bp.route("/api/dashboard/state", methods=["GET"])
def dashboard_state():
    today = _date.today().isoformat()
    db.rollover_tasks(today)
    return jsonify({"tasks": db.get_tasks(), "goals": db.get_goals()})


@bp.route("/api/dashboard/tasks", methods=["POST"])
def create_task():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    date = (data.get("date") or _date.today().isoformat()).strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    return jsonify(db.add_task(text, date)), 201


@bp.route("/api/dashboard/tasks/<int:task_id>", methods=["PATCH"])
def patch_task(task_id):
    data   = request.get_json(silent=True) or {}
    result = db.update_task(task_id, **data)
    if not result:
        return jsonify({"error": "not found"}), 404
    return jsonify(result)


@bp.route("/api/dashboard/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    if db.delete_task(task_id):
        return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


@bp.route("/api/dashboard/goals", methods=["POST"])
def create_goal():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    return jsonify(db.add_goal(text)), 201


@bp.route("/api/dashboard/goals/<int:goal_id>", methods=["DELETE"])
def remove_goal(goal_id):
    if db.delete_goal(goal_id):
        return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


# ── Docs ───────────────────────────────────────────────────────────────────────

@bp.route("/docs")
def docs_page():
    if request.args.get("fragment"):
        html = render_template("docs.html")
        import re
        styles = re.findall(r"<style[^>]*>.*?</style>", html, re.DOTALL)
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL)
        body = m.group(1) if m else html
        return "\n".join(styles) + "\n" + body
    return render_template("docs.html")


@bp.route("/api/docs", methods=["GET"])
def api_get_docs():
    return jsonify(db.get_all_docs())


@bp.route("/api/docs", methods=["POST"])
def api_create_doc():
    data  = request.get_json(silent=True) or {}
    title = data.get("title", "Untitled").strip() or "Untitled"
    return jsonify(db.create_doc(title)), 201


@bp.route("/api/docs/<int:doc_id>", methods=["GET"])
def api_get_doc(doc_id):
    doc = db.get_doc(doc_id)
    if not doc:
        return jsonify({"error": "Not found"}), 404
    return jsonify(doc)


@bp.route("/api/docs/<int:doc_id>", methods=["PATCH"])
def api_update_doc(doc_id):
    data    = request.get_json(silent=True) or {}
    title   = data.get("title")
    content = data.get("content")
    doc = db.update_doc(doc_id, title=title, content=content)
    if not doc:
        return jsonify({"error": "Not found"}), 404
    return jsonify(doc)


@bp.route("/api/docs/<int:doc_id>", methods=["DELETE"])
def api_delete_doc(doc_id):
    if db.delete_doc(doc_id):
        return jsonify({"ok": True})
    return jsonify({"error": "Not found"}), 404


# ── Launch ─────────────────────────────────────────────────────────────────────
# Replaces the pywebview JS API (window.pywebview.api.open_X).
# HTML calls fetch('/launch/youtube') etc. Flask opens the URL in the
# system default browser via webbrowser.open().

import subprocess as _sp

def _open_url(url: str) -> None:
    """Open a URL in the user's existing default browser (new tab, not new process).
    Uses Windows 'start' shell command so the browser reuses its running instance
    instead of spawning a fresh one — avoids RAM spikes from webbrowser.open()."""
    try:
        _sp.Popen(["cmd", "/c", "start", "", url],
                  stdout=_sp.DEVNULL,
                  stderr=_sp.DEVNULL)
    except Exception as e:
        print(f"[launch] failed to open {url}: {e}")

_LAUNCH_URLS = {
    "youtube":       "https://youtube.com",
    "spotify":       "https://open.spotify.com",
    "whatsapp":      "https://web.whatsapp.com",
    "discord":       "https://discord.com/app",
    "github":        "https://github.com",
    "linkedin":      "https://www.linkedin.com",
    "gmail":         "https://mail.google.com",
    "reddit":        "https://www.reddit.com",
    "instagram":     "https://www.instagram.com",
    "twitch":        "https://twitch.tv",
    "roblox":        "https://www.roblox.com",
    "steam":         "https://store.steampowered.com",
    "warframe":      "https://warframe.market",
    "chatgpt":       "https://chatgpt.com",
    "drive":         "https://drive.google.com",
}

_TRIGGER_MAP = {
    "drive":         "drive",
    "reddit":        "reddit",
    "chatgpt":       "chatgpt",
    "open chatgpt":  "chatgpt",
    "youtube":       "youtube",
    "bored":         "youtube",
    "not feeling":   "youtube",
    "too lazy":      "youtube",
    "chill":         "youtube",
    "linkedin":      "linkedin",
    "github":        "github",
    "git":           "github",
    "whatsapp":      "whatsapp",
    "check messages":"whatsapp",
    "discord":       "discord",
    "twitch":        "twitch",
    "streaming":     "twitch",
    "roblox":        "roblox",
    "steam":         "steam",
    "play games":    "steam",
    "warframe":      "warframe",
    "spotify":       "spotify",
    "music":         "spotify",
    "instagram":     "instagram",
    "gmail":         "gmail",
    "open mail":     "gmail",
}


@bp.route("/launch/<app_name>")
def launch_app(app_name):
    url = _LAUNCH_URLS.get(app_name)
    if url:
        _open_url(url)
        return jsonify({"status": "ok", "opened": url})
    return jsonify({"status": "error", "message": "unknown app"}), 404


@bp.route("/api/trigger", methods=["POST"])
def trigger():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").lower().strip()
    results, fired = [], set()
    for keyword, app_name in _TRIGGER_MAP.items():
        if keyword in text and app_name not in fired:
            url = _LAUNCH_URLS.get(app_name)
            if url:
                _open_url(url)
                results.append(f"Opened {app_name}")
                fired.add(app_name)
    return jsonify({
        "result": " · ".join(results) if results else None
    })


@bp.route("/api/launchers", methods=["GET"])
def get_launchers():
    return jsonify(db.get_launchers())


@bp.route("/api/launchers", methods=["POST"])
def create_launcher():
    data   = request.get_json(silent=True) or {}
    name   = (data.get("name") or "").strip()
    kind   = (data.get("kind") or "").strip()
    target = (data.get("target") or "").strip()
    icon   = (data.get("icon") or "🚀").strip()
    if not name or kind not in ("url", "path") or not target:
        return jsonify({"error": "name, kind (url|path), and target are required"}), 400
    return jsonify(db.add_launcher(name, kind, target, icon)), 201


@bp.route("/api/launchers/<int:launcher_id>", methods=["DELETE"])
def remove_launcher(launcher_id):
    if db.delete_launcher(launcher_id):
        return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


@bp.route("/launch/custom/<int:launcher_id>")
def launch_custom(launcher_id):
    launchers = db.get_launchers()
    launcher  = next((l for l in launchers if l["id"] == launcher_id), None)
    if not launcher:
        return jsonify({"error": "not found"}), 404
    if launcher["kind"] == "url":
        _open_url(launcher["target"])
    else:
        import subprocess as _sp2
        try:
            _sp2.Popen(["cmd", "/c", "start", "", launcher["target"]],
                       stdout=_sp2.DEVNULL, stderr=_sp2.DEVNULL)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "ok", "opened": launcher["target"]})


@bp.route("/api/ping")
def ping():
    """Electron polls this to know Flask is ready before opening the window."""
    return jsonify({"status": "ok"})