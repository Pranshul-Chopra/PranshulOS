# ── routes.py ─────────────────────────────────────────────────────────────────
# Flask routes: Home, Dashboard, Docs.

import os
from flask import Blueprint, render_template, render_template_string, request, jsonify
from datetime import datetime as _dt, date as _date

import db

bp = Blueprint("main", __name__, template_folder="templates")


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
      --bg: #0c0c0c; --surface: #141414; --surface2: #1c1c1c;
      --border: #272727; --border2: #333;
      --text: #e8e6e1; --text2: #8a8880; --text3: #4a4845;
      --amber: #e8a84c; --amber-dim: #7a5820; --amber-glow: rgba(232,168,76,0.08);
      --radius: 12px;
      --mono: 'IBM Plex Mono', monospace; --sans: 'IBM Plex Sans', sans-serif;
    }
    html, body { height: 100%; background: var(--bg); color: var(--text); font-family: var(--sans); -webkit-font-smoothing: antialiased; }
    .shell { max-width: 640px; margin: 0 auto; padding: 48px 24px 32px; }
    .greeting { font-size: 24px; font-weight: 300; letter-spacing: -0.02em; margin-bottom: 6px; }
    .greeting em { color: var(--amber); font-style: normal; }
    .sub { font-size: 13px; color: var(--text3); font-family: var(--mono); margin-bottom: 36px; letter-spacing: 0.04em; }
    .section-label { font-family: var(--mono); font-size: 10px; font-weight: 500; color: var(--text3); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 12px; }
    .launch-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 32px; }
    .launch-btn {
      padding: 16px 18px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border2);
      color: var(--text); font-family: var(--sans); font-size: 14px;
      text-align: left; cursor: pointer; transition: all 0.15s;
      display: flex; align-items: center; gap: 10px;
    }
    .launch-btn:hover { background: var(--surface2); border-color: var(--amber-dim); }
    .launch-btn .icon { font-size: 18px; }
    .launch-btn .label { font-weight: 400; }
    .launch-btn .desc { font-size: 11px; color: var(--text3); margin-top: 2px; font-family: var(--mono); }
    .divider { height: 1px; background: var(--border); margin: 28px 0; }
    .input-row { display: flex; gap: 10px; }
    .input-box {
      flex: 1; padding: 12px 16px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border2);
      color: var(--text); font-family: var(--sans); font-size: 14px; outline: none;
      transition: border-color 0.15s;
    }
    .input-box:focus { border-color: var(--amber-dim); }
    .input-box::placeholder { color: var(--text3); }
    .go-btn {
      padding: 12px 24px; border-radius: var(--radius);
      background: var(--amber); color: #0c0c0c; border: none;
      font-family: var(--sans); font-size: 14px; font-weight: 500;
      cursor: pointer; transition: opacity 0.15s;
    }
    .go-btn:hover { opacity: 0.85; }
    .log {
      margin-top: 16px; padding: 14px 16px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border);
      font-family: var(--mono); font-size: 12px; color: var(--text2);
      min-height: 48px; line-height: 1.8;
    }
    .log .entry { animation: fadein 0.2s ease; }
    .log .entry.you { color: var(--text); }
    .log .entry.reply { color: var(--amber); }
    @keyframes fadein { from { opacity:0; transform: translateY(3px); } to { opacity:1; transform:none; } }
  </style>
</head>
<body>
<div class="shell">
  <div class="greeting">{{ greeting }}</div>
  <div class="sub">what do you want to do?</div>

  <div class="section-label">Quick Launch</div>
  <div class="launch-grid">
    <button class="launch-btn" onclick="launch('open_youtube')">
      <span class="icon">🎬</span>
      <div><div class="label">YouTube</div><div class="desc">Watch something</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_spotify')">
      <span class="icon">🎵</span>
      <div><div class="label">Spotify</div><div class="desc">Music</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_whatsapp')">
      <span class="icon">💬</span>
      <div><div class="label">WhatsApp</div><div class="desc">Web messages</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_discord')">
      <span class="icon">🎮</span>
      <div><div class="label">Discord</div><div class="desc">Open web app</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_github')">
      <span class="icon">🐙</span>
      <div><div class="label">GitHub</div><div class="desc">Open dashboard</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_linkedin')">
      <span class="icon">🔗</span>
      <div><div class="label">LinkedIn</div><div class="desc">Your profile</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_gmail')">
      <span class="icon">✉️</span>
      <div><div class="label">Gmail</div><div class="desc">Inbox</div></div>
    </button>
    <button class="launch-btn" onclick="launch('open_reddit')">
      <span class="icon">👽</span>
      <div><div class="label">Reddit</div><div class="desc">Browse</div></div>
    </button>
  </div>

  <div class="divider"></div>
  <div class="section-label">Or just tell me</div>
  <div class="input-row">
    <input class="input-box" id="inp" placeholder='e.g. "bored" or "github"…' onkeydown="if(event.key==='Enter') go()"/>
    <button class="go-btn" onclick="go()">Go</button>
  </div>
  <div class="log" id="log"><span style="color:var(--text3)">→ hey! what do you need?</span></div>
</div>
<script>
async function launch(fn) {
  const result = await window.pywebview.api[fn]();
  addLog('→ ' + (result || 'done!'), 'reply');
}
async function go() {
  const inp = document.getElementById('inp');
  const text = inp.value.trim();
  if (!text) return;
  addLog('You: ' + text, 'you');
  inp.value = '';
  const result = await window.pywebview.api.check_trigger(text);
  addLog(result ? '→ ' + result : "→ Didn't catch that. Try 'bored', 'github', 'spotify'…", 'reply');
}
function addLog(text, cls) {
  const log = document.getElementById('log');
  if (log.children.length === 0 || log.querySelector('span')) log.innerHTML = '';
  const el = document.createElement('div');
  el.className = 'entry ' + cls;
  el.textContent = text;
  log.appendChild(el);
  log.scrollTop = log.scrollHeight;
}
</script>
</body>
</html>"""


@bp.route("/home")
def home():
    h = _dt.now().hour
    if h < 12:   greeting = "Good morning, Pranshul ☀️"
    elif h < 17: greeting = "Good afternoon, Pranshul 🌤"
    else:        greeting = "Good evening, Pranshul 🌙"
    return render_template_string(_HOME_HTML, greeting=greeting)


# ── Dashboard ──────────────────────────────────────────────────────────────────

@bp.route("/dashboard")
def dashboard():
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
