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
  <title>Home &mdash; PranshulOS</title>
  <link rel="stylesheet" href="/static/fonts/ibmflex.css"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0c0c0c; --surface: #141414; --surface2: #1a1a1a;
      --border: #242424; --border2: #2e2e2e;
      --text: #e2e0db; --text2: #7a7872; --text3: #3e3d3a;
      --amber: #e8a84c; --amber-dim: #6b4d1c;
      --green: #5aab7f;
      --radius: 10px;
      --mono: 'IBM Plex Mono', monospace; --sans: 'IBM Plex Sans', sans-serif;
    }
    #home-root {
      display: flex; flex-direction: column;
      width: 100%; height: 100%;
      background: var(--bg); color: var(--text);
      font-family: var(--sans); font-size: 15px; line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }
    .home-top {
      flex-shrink: 0; padding: 28px 28px 20px;
      border-bottom: 1px solid var(--border);
    }
    .greeting { font-size: 22px; font-weight: 400; letter-spacing: -0.02em; color: var(--text); }
    .greeting em { color: var(--amber); font-style: normal; }
    .home-body {
      display: grid; grid-template-columns: 1fr 320px;
      flex: 1; min-height: 0; overflow: hidden;
    }
    .home-left {
      padding: 24px 24px 24px 28px;
      display: flex; flex-direction: column; gap: 24px;
      overflow-y: auto; border-right: 1px solid var(--border);
    }
    .section-label {
      font-family: var(--mono); font-size: 10px; font-weight: 500;
      color: var(--text3); letter-spacing: 0.07em;
      text-transform: uppercase; margin-bottom: 12px;
    }
    .launch-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
    .launch-btn {
      position: relative; padding: 16px 10px 14px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border2);
      color: var(--text); font-family: var(--sans); text-align: center; cursor: pointer;
      transition: background 0.14s, border-color 0.14s, transform 0.1s;
      display: flex; flex-direction: column; align-items: center; gap: 8px;
    }
    .launch-btn:hover { background: var(--surface2); border-color: var(--amber-dim); transform: translateY(-1px); }
    .launch-btn .icon { font-size: 20px; line-height: 1; }
    .launch-btn .label { font-size: 11px; color: var(--text2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
    .launch-btn .del-x {
      position: absolute; top: 5px; right: 5px; width: 16px; height: 16px;
      border-radius: 50%; background: #2a2a2a; border: 1px solid #3a3a3a;
      color: var(--text2); font-size: 10px; opacity: 0; transition: opacity 0.12s;
      display: flex; align-items: center; justify-content: center; z-index: 2; cursor: pointer;
    }
    .launch-btn:hover .del-x { opacity: 1; }
    .launch-btn .del-x:hover { background: #c0392b; border-color: #c0392b; color: #fff; }
    .add-btn {
      padding: 16px 10px 14px; border-radius: var(--radius);
      background: var(--surface); border: 1px dashed var(--border2);
      color: var(--text3); font-family: var(--sans); text-align: center; cursor: pointer;
      transition: background 0.14s, border-color 0.14s, transform 0.1s;
      display: flex; flex-direction: column; align-items: center; gap: 8px;
    }
    .add-btn:hover { background: var(--surface2); border-color: var(--amber-dim); transform: translateY(-1px); }
    .add-btn .add-bubble {
      width: 32px; height: 32px; border-radius: 50%; background: var(--amber);
      display: flex; align-items: center; justify-content: center; font-size: 18px; color: #0c0c0c;
    }
    .add-btn .label { font-size: 11px; color: var(--text3); }
    .cmd-bar {
      display: flex; gap: 8px; align-items: center;
      background: var(--surface); border: 1px solid var(--border2);
      border-radius: var(--radius); padding: 4px 4px 4px 14px; transition: border-color 0.15s;
    }
    .cmd-bar:focus-within { border-color: var(--amber-dim); }
    .cmd-input {
      flex: 1; background: transparent; border: none; outline: none;
      color: var(--text); font-family: var(--sans); font-size: 14px; padding: 7px 0;
    }
    .cmd-input::placeholder { color: var(--text3); }
    .cmd-go {
      padding: 7px 16px; border-radius: 7px; background: var(--amber); color: #0c0c0c;
      border: none; font-family: var(--sans); font-size: 13px; font-weight: 500; cursor: pointer;
    }
    .cmd-go:hover { opacity: 0.88; }
    .log {
      margin-top: 10px; padding: 11px 14px; border-radius: var(--radius);
      background: var(--surface); border: 1px solid var(--border);
      font-family: var(--mono); font-size: 12px; color: var(--text2); line-height: 1.8;
    }
    .log .entry.you { color: var(--text); }
    .log .entry.reply { color: var(--amber); }
    @keyframes fadein { from { opacity:0; transform: translateY(3px); } to { opacity:1; } }
    .log .entry { animation: fadein 0.18s ease; }
    .home-right {
      padding: 24px 20px; display: flex; flex-direction: column; gap: 14px; overflow-y: auto;
    }
    .glance-card { background: var(--surface); border: 1px solid var(--border2); border-radius: 10px; overflow: hidden; }
    .glance-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 11px 14px; border-bottom: 1px solid var(--border);
    }
    .glance-title { font-family: var(--mono); font-size: 10px; letter-spacing: 0.1em; color: var(--amber); text-transform: uppercase; font-weight: 600; }
    .glance-count { font-family: var(--mono); font-size: 10px; color: var(--text2); }
    .glance-count .done { color: var(--green); }
    .glance-item { display: flex; align-items: center; gap: 10px; padding: 9px 14px; border-bottom: 1px solid var(--border); }
    .glance-item:last-child { border-bottom: none; }
    .g-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
    .g-dot.pending { background: transparent; border: 1.5px solid var(--text2); }
    .g-dot.done    { background: var(--green); border: 1.5px solid var(--green); }
    .g-text { flex: 1; font-size: 12px; color: var(--text); line-height: 1.5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .glance-item.is-done .g-text { text-decoration: line-through; color: var(--text3); }
    .glance-subsection {
      padding: 6px 14px; font-family: var(--mono); font-size: 9px; letter-spacing: 0.1em;
      color: var(--text3); text-transform: uppercase;
      background: rgba(232,168,76,0.03); border-bottom: 1px solid var(--border); border-top: 1px solid var(--border);
    }
    .glance-empty { padding: 24px 14px; text-align: center; font-family: var(--mono); font-size: 11px; color: var(--text2); letter-spacing: 0.05em; line-height: 1.7; }
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0,0,0,0.7);
      display: flex; align-items: center; justify-content: center;
      z-index: 999; opacity: 0; pointer-events: none; transition: opacity 0.15s;
    }
    .modal-overlay.open { opacity: 1; pointer-events: all; }
    .modal { background: #181818; border: 1px solid var(--border2); border-radius: 14px; padding: 28px 28px 24px; width: 360px; max-width: calc(100vw - 48px); transform: translateY(8px); transition: transform 0.15s; }
    .modal-overlay.open .modal { transform: translateY(0); }
    .modal-title { font-size: 15px; font-weight: 500; color: var(--text); margin-bottom: 20px; }
    .field-label { font-family: var(--mono); font-size: 10px; color: var(--text3); letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px; }
    .field-group { margin-bottom: 14px; }
    .field-input { width: 100%; padding: 10px 13px; border-radius: 8px; background: var(--surface); border: 1px solid var(--border2); color: var(--text); font-family: var(--sans); font-size: 14px; outline: none; transition: border-color 0.14s; }
    .field-input:focus { border-color: var(--amber-dim); }
    .field-input::placeholder { color: var(--text3); }
    .modal-actions { display: flex; gap: 8px; margin-top: 20px; }
    .modal-cancel { flex: 1; padding: 9px; border-radius: 8px; border: 1px solid var(--border2); background: transparent; color: var(--text2); font-family: var(--sans); font-size: 13px; cursor: pointer; }
    .modal-cancel:hover { background: var(--surface2); }
    .modal-save { flex: 2; padding: 9px; border-radius: 8px; border: none; background: var(--amber); color: #0c0c0c; font-family: var(--sans); font-size: 13px; font-weight: 500; cursor: pointer; }
    .modal-save:hover { opacity: 0.88; }
  </style>
</head>
<body>
<div id="home-root">

  <div class="home-top">
    <div class="greeting">{{ greeting }}</div>
  </div>

  <div class="home-body">

    <div class="home-left">
      <div>
        <div class="section-label">Quick launch</div>
        <div class="launch-grid" id="launch-grid">
          <button class="launch-btn" onclick="launch('youtube')"><span class="icon">\U0001f3ac</span><span class="label">YouTube</span></button>
          <button class="launch-btn" onclick="launch('spotify')"><span class="icon">\U0001f3b5</span><span class="label">Spotify</span></button>
          <button class="launch-btn" onclick="launch('whatsapp')"><span class="icon">\U0001f4ac</span><span class="label">WhatsApp</span></button>
          <button class="launch-btn" onclick="launch('discord')"><span class="icon">\U0001f3ae</span><span class="label">Discord</span></button>
          <button class="launch-btn" onclick="launch('github')"><span class="icon">\U0001f419</span><span class="label">GitHub</span></button>
          <button class="launch-btn" onclick="launch('linkedin')"><span class="icon">\U0001f517</span><span class="label">LinkedIn</span></button>
          <button class="launch-btn" onclick="launch('gmail')"><span class="icon">\u2709\ufe0f</span><span class="label">Gmail</span></button>
          <button class="launch-btn" onclick="launch('reddit')"><span class="icon">\U0001f47d</span><span class="label">Reddit</span></button>
          <button class="add-btn" id="add-btn" onclick="openModal()"><span class="add-bubble">+</span><span class="label">Add</span></button>
        </div>
      </div>
      <div>
        <div class="section-label">Or just tell me</div>
        <div class="cmd-bar">
          <input class="cmd-input" id="inp" placeholder='try "bored", "github", "spotify"\u2026' onkeydown="if(event.key==='Enter') go()"/>
          <button class="cmd-go" onclick="go()">Go</button>
        </div>
        <div class="log" id="log"><span style="color:var(--text3)">\u2192 what do you need?</span></div>
      </div>
    </div>

    <div class="home-right">
      <div class="glance-card">
        <div class="glance-header">
          <span class="glance-title">\U0001f501 Routine</span>
          <span class="glance-count" id="routine-count"></span>
        </div>
        <div id="routine-glance-body"></div>
      </div>
      <div class="glance-card">
        <div class="glance-header">
          <span class="glance-title">\U0001f4cb Tasks</span>
          <span class="glance-count" id="tasks-count"></span>
        </div>
        <div id="tasks-glance-body"></div>
      </div>
    </div>

  </div>
</div>

<div class="modal-overlay" id="modal-overlay" onclick="overlayClick(event)">
  <div class="modal">
    <div class="modal-title">Add launcher</div>
    <div class="field-group"><div class="field-label">Name</div><input class="field-input" id="m-name" placeholder="e.g. Notion" maxlength="20"/></div>
    <div class="field-group"><div class="field-label">Icon</div><input class="field-input" id="m-icon" placeholder="\U0001f680" maxlength="4"/></div>
    <div class="field-group"><div class="field-label">URL</div><input class="field-input" id="m-url" placeholder="https://example.com"/></div>
    <div class="modal-actions">
      <button class="modal-cancel" onclick="closeModal()">Cancel</button>
      <button class="modal-save" onclick="saveCustom()">Add launcher</button>
    </div>
  </div>
</div>

<script>
function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}
async function launch(app) {
  try { await fetch('/launch/' + app); addLog('\u2192 opened ' + app, 'reply'); }
  catch(e) { addLog('\u2192 error', 'reply'); }
}
async function loadCustom() {
  try { renderCustom(await fetch('/api/launchers').then(r => r.json())); }
  catch(e) { console.error('loadCustom', e); }
}
function renderCustom(list) {
  const grid = document.getElementById('launch-grid');
  const add  = document.getElementById('add-btn');
  grid.querySelectorAll('.custom-btn').forEach(e => e.remove());
  list.forEach(item => {
    const btn = document.createElement('button');
    btn.className = 'launch-btn custom-btn';
    btn.innerHTML = `<span class="icon">${item.icon}</span><span class="label">${item.name}</span><span class="del-x">\xd7</span>`;
    btn.querySelector('.del-x').addEventListener('click', async e => {
      e.stopPropagation();
      await fetch('/api/launchers/' + item.id, {method:'DELETE'});
      addLog('\u2192 removed ' + item.name, 'reply');
      loadCustom();
    });
    btn.addEventListener('click', async e => {
      if (e.target.classList.contains('del-x')) return;
      try { await fetch('/launch/custom/' + item.id); addLog('\u2192 opened ' + item.name, 'reply'); }
      catch(e) { addLog('\u2192 error', 'reply'); }
    });
    grid.insertBefore(btn, add);
  });
}
async function loadRoutineGlance() {
  const body = document.getElementById('routine-glance-body');
  const cnt  = document.getElementById('routine-count');
  try {
    const items = await fetch('/api/routine?date=' + todayStr()).then(r => r.json());
    if (!items.length) { body.innerHTML = '<div class="glance-empty">NO ROUTINE ITEMS YET</div>'; cnt.innerHTML=''; return; }
    const done = items.filter(x=>x.checked).length;
    cnt.innerHTML = `<span class="done">${done}</span> / ${items.length}`;
    items.sort((a,b)=>(a.checked||0)-(b.checked||0)||a.position-b.position);
    body.innerHTML = '';
    items.forEach(item => {
      const d = document.createElement('div');
      d.className = 'glance-item' + (item.checked?' is-done':'');
      d.innerHTML = `<span class="g-dot ${item.checked?'done':'pending'}"></span><span class="g-text">${item.text}</span>`;
      body.appendChild(d);
    });
  } catch(e) { body.innerHTML='<div class="glance-empty">UNAVAILABLE</div>'; }
}
async function loadTasksGlance() {
  const body = document.getElementById('tasks-glance-body');
  const cnt  = document.getElementById('tasks-count');
  try {
    const data    = await fetch('/api/dashboard/state').then(r=>r.json());
    const today   = todayStr();
    const tasks   = data.tasks || [];
    const pending = tasks.filter(t=>!t.done && t.date===today);
    const done    = tasks.filter(t=> t.done && t.done_date===today);
    if (!pending.length && !done.length) { body.innerHTML='<div class="glance-empty">ALL CLEAR \u2014 NOTHING DUE TODAY</div>'; cnt.innerHTML=''; return; }
    cnt.innerHTML = `<span class="done">${done.length}</span> / ${pending.length+done.length}`;
    body.innerHTML = '';
    pending.forEach(t => {
      const d = document.createElement('div');
      d.className='glance-item';
      d.innerHTML=`<span class="g-dot pending"></span><span class="g-text">${t.text}</span>`;
      body.appendChild(d);
    });
    if (done.length) {
      body.innerHTML += '<div class="glance-subsection">Done</div>';
      done.forEach(t => {
        const d = document.createElement('div');
        d.className='glance-item is-done';
        d.innerHTML=`<span class="g-dot done"></span><span class="g-text">${t.text}</span>`;
        body.appendChild(d);
      });
    }
  } catch(e) { body.innerHTML='<div class="glance-empty">UNAVAILABLE</div>'; }
}
function addLog(msg, cls) {
  const log = document.getElementById('log'); if(!log) return;
  const e = document.createElement('div');
  e.className='entry '+cls; e.textContent=msg;
  log.innerHTML=''; log.appendChild(e);
}
async function go() {
  const inp = document.getElementById('inp');
  const q = inp.value.trim(); if(!q) return;
  addLog('\u2192 '+q,'you'); inp.value='';
  try {
    const d = await fetch('/api/trigger',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:q})}).then(r=>r.json());
    addLog('\u2192 '+(d.reply||d.result||'ok'),'reply');
  } catch(e) { addLog('\u2192 error','reply'); }
}
function openModal()    { document.getElementById('modal-overlay').classList.add('open'); }
function closeModal()   { document.getElementById('modal-overlay').classList.remove('open'); }
function overlayClick(e){ if(e.target===document.getElementById('modal-overlay')) closeModal(); }
async function saveCustom() {
  const name = document.getElementById('m-name').value.trim();
  const icon = document.getElementById('m-icon').value.trim() || '\U0001f517';
  const url  = document.getElementById('m-url').value.trim();
  if (!name || !url) return;
  try {
    await fetch('/api/launchers', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ name, icon, kind: 'url', target: url })});
    closeModal();
    ['m-name','m-icon','m-url'].forEach(id => document.getElementById(id).value = '');
    addLog('\u2192 added ' + name, 'reply');
    loadCustom();
  } catch(e) { addLog('\u2192 error saving launcher', 'reply'); }
}
window.__pageInit = function() {
  const root = document.getElementById('home-root');
  if (root && root.parentElement) {
    root.parentElement.style.cssText = 'display:flex;flex-direction:column;flex:1;min-height:0;height:100%;';
  }
  loadCustom();
  loadRoutineGlance();
  loadTasksGlance();
};
window.launch=launch; window.go=go;
window.openModal=openModal; window.closeModal=closeModal;
window.overlayClick=overlayClick; window.saveCustom=saveCustom;
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

# Suppress the console window flash on Windows for every subprocess call.
_CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0

def _open_url(url: str) -> None:
    """Open a URL in the user's existing default browser (new tab, not new process).
    Uses Windows 'start' shell command so the browser reuses its running instance
    instead of spawning a fresh one — avoids RAM spikes from webbrowser.open().
    CREATE_NO_WINDOW suppresses the terminal flash that previously appeared on
    every shortcut click."""
    try:
        _sp.Popen(
            ["cmd", "/c", "start", "", url],
            stdout=_sp.DEVNULL,
            stderr=_sp.DEVNULL,
            creationflags=_CREATE_NO_WINDOW,
        )
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
        try:
            _sp.Popen(
                ["cmd", "/c", "start", "", launcher["target"]],
                stdout=_sp.DEVNULL,
                stderr=_sp.DEVNULL,
                creationflags=_CREATE_NO_WINDOW,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"status": "ok", "opened": launcher["target"]})


@bp.route("/api/ping")
def ping():
    """Electron polls this to know Flask is ready before opening the window."""
    return jsonify({"status": "ok"})


# ── Routine ────────────────────────────────────────────────────────────────────

@bp.route("/routine")
def routine_page():
    if request.args.get("fragment"):
        from flask import render_template_string
        import re
        html = render_template_string(_ROUTINE_HTML)
        styles = re.findall(r"<style[^>]*>.*?</style>", html, re.DOTALL)
        m = re.search(r"<body[^>]*>(.*)</body>", html, re.DOTALL)
        body = m.group(1) if m else html
        return "\n".join(styles) + "\n" + body
    from flask import render_template_string
    return render_template_string(_ROUTINE_HTML)


@bp.route("/api/routine", methods=["GET"])
def api_get_routine():
    date = request.args.get("date") or _date.today().isoformat()
    return jsonify(db.get_routine_items(date))


@bp.route("/api/routine/items", methods=["POST"])
def api_add_routine_item():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text required"}), 400
    return jsonify(db.add_routine_item(text)), 201


@bp.route("/api/routine/items/<int:item_id>", methods=["DELETE"])
def api_delete_routine_item(item_id):
    if db.delete_routine_item(item_id):
        return jsonify({"ok": True})
    return jsonify({"error": "not found"}), 404


@bp.route("/api/routine/check", methods=["POST"])
def api_set_routine_check():
    data    = request.get_json(silent=True) or {}
    item_id = data.get("item_id")
    date    = (data.get("date") or _date.today().isoformat()).strip()
    checked = bool(data.get("checked", True))
    if not item_id:
        return jsonify({"error": "item_id required"}), 400
    db.set_routine_check(int(item_id), date, checked)
    return jsonify({"ok": True})


@bp.route("/api/routine/progress", methods=["GET"])
def api_routine_progress():
    date = request.args.get("date") or _date.today().isoformat()
    return jsonify(db.get_routine_progress(date))


# ── Routine page template ──────────────────────────────────────────────────────

_ROUTINE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <title>Routine — PranshulOS</title>
  <link rel="stylesheet" href="/static/fonts/ibmflex.css"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #0c0c0c; --surface: #141414; --surface2: #1c1c1c;
      --border: #272727; --border2: #333;
      --text: #e8e6e1; --text2: #8a8880; --text3: #4a4845;
      --amber: #e8a84c; --amber-dim: #7a5820;
      --amber-faint: rgba(232,168,76,0.07); --amber-faint2: rgba(232,168,76,0.14);
      --green: #5aab7f; --green-faint: rgba(90,171,127,0.10);
      --mono: 'IBM Plex Mono', monospace; --sans: 'IBM Plex Sans', sans-serif;
      --r: 10px;
    }
    html, body { height: 100%; background: var(--bg); color: var(--text);
      font-family: var(--sans); -webkit-font-smoothing: antialiased; }

    .page { max-width: 560px; margin: 0 auto; padding: 36px 28px 60px; }

    /* ── header ── */
    .page-header { margin-bottom: 30px; }
    .page-title {
      font-family: var(--mono); font-size: 11px; letter-spacing: 0.13em;
      color: var(--text3); text-transform: uppercase; margin-bottom: 6px;
    }
    .page-sub { font-size: 22px; font-weight: 400; color: var(--text); letter-spacing: -0.02em; }
    .page-date { font-family: var(--mono); font-size: 11px; color: var(--text2); margin-top: 4px; }

    /* ── progress bar ── */
    .progress-wrap { margin-bottom: 28px; }
    .progress-label {
      display: flex; justify-content: space-between;
      font-family: var(--mono); font-size: 10px; color: var(--text3);
      letter-spacing: 0.08em; margin-bottom: 7px;
    }
    .progress-label .done-label { color: var(--green); }
    .progress-bar {
      height: 3px; background: var(--border2); border-radius: 2px; overflow: hidden;
    }
    .progress-fill {
      height: 100%; background: var(--green); border-radius: 2px;
      transition: width 0.35s ease;
    }

    /* ── add row ── */
    .add-row { display: flex; gap: 8px; margin-bottom: 20px; }
    .add-input {
      flex: 1; background: var(--surface); border: 1px solid var(--border2);
      border-radius: 8px; padding: 9px 13px;
      font-family: var(--sans); font-size: 13px; color: var(--text);
      outline: none; transition: border-color 0.15s;
    }
    .add-input:focus { border-color: var(--amber-dim); }
    .add-input::placeholder { color: var(--text3); }
    .add-btn-primary {
      background: var(--amber-faint2); border: 1px solid var(--amber-dim);
      border-radius: 8px; padding: 9px 16px;
      font-family: var(--mono); font-size: 11px; color: var(--amber);
      cursor: pointer; letter-spacing: 0.06em; white-space: nowrap;
      transition: background 0.15s;
    }
    .add-btn-primary:hover { background: rgba(232,168,76,0.22); }

    /* ── section labels ── */
    .sec-label {
      font-family: var(--mono); font-size: 10px; letter-spacing: 0.12em;
      color: var(--text3); text-transform: uppercase; margin-bottom: 10px;
    }

    /* ── routine list ── */
    .routine-list { display: flex; flex-direction: column; gap: 6px; margin-bottom: 28px; }
    .routine-item {
      display: flex; align-items: center; gap: 11px;
      padding: 11px 13px;
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 8px; transition: border-color 0.15s, background 0.15s;
    }
    .routine-item.checked {
      background: var(--green-faint); border-color: rgba(90,171,127,0.2);
    }
    .routine-item.checked .ri-text { color: var(--text3); text-decoration: line-through; }

    /* checkbox */
    .ri-check {
      width: 17px; height: 17px; border-radius: 50%;
      border: 1.5px solid var(--border2); flex-shrink: 0; cursor: pointer;
      display: flex; align-items: center; justify-content: center;
      transition: all 0.15s;
    }
    .ri-check.checked { border-color: var(--green); background: var(--green-faint); }
    .ri-check.checked::after {
      content:''; width: 7px; height: 5px;
      border-left: 1.5px solid var(--green); border-bottom: 1.5px solid var(--green);
      transform: rotate(-45deg) translateY(-1px); display: block;
    }
    .ri-text { flex: 1; font-size: 13px; color: var(--text); line-height: 1.4; }
    .ri-del {
      background: none; border: none; color: transparent; cursor: pointer;
      font-size: 15px; padding: 2px 4px; border-radius: 4px;
      transition: color 0.1s; flex-shrink: 0;
    }
    .routine-item:hover .ri-del { color: var(--text3); }
    .ri-del:hover { color: #c87070 !important; }

    /* ── empty state ── */
    .empty {
      padding: 28px 12px; text-align: center;
      font-family: var(--mono); font-size: 11px; color: var(--text3);
      letter-spacing: 0.06em; border: 1px dashed var(--border); border-radius: 8px;
    }

    /* ── all-done card ── */
    .all-done {
      display: none; padding: 16px 18px;
      background: var(--green-faint); border: 1px solid rgba(90,171,127,0.25);
      border-radius: 8px;
      font-family: var(--mono); font-size: 11px; color: var(--green);
      letter-spacing: 0.07em; text-align: center; margin-top: -10px; margin-bottom: 20px;
    }
    .all-done.visible { display: block; }

    /* ── template hint ── */
    .template-hint {
      font-family: var(--mono); font-size: 10px; color: var(--text3);
      letter-spacing: 0.06em; margin-top: 6px; line-height: 1.7;
    }
  </style>
</head>
<body>
<div class="page">
  <div class="page-header">
    <div class="page-title">Daily Routine</div>
    <div class="page-sub">Routine Checklist</div>
    <div class="page-date" id="r-date"></div>
  </div>

  <div class="progress-wrap" id="progress-wrap" style="display:none">
    <div class="progress-label">
      <span>DAILY PROGRESS</span>
      <span class="done-label" id="progress-text">0 / 0</span>
    </div>
    <div class="progress-bar"><div class="progress-fill" id="progress-fill" style="width:0%"></div></div>
  </div>

  <div class="all-done" id="all-done">✓ ALL DONE — GREAT WORK TODAY</div>

  <div class="sec-label" id="sec-checklist" style="display:none">TODAY'S CHECKLIST</div>
  <div class="routine-list" id="routine-list"></div>

  <div class="sec-label">ADD ROUTINE ITEM</div>
  <div class="add-row">
    <input class="add-input" id="r-inp" placeholder="e.g. Morning stretch, Read 20 pages…"
      onkeydown="if(event.key==='Enter') addItem()"/>
    <button class="add-btn-primary" onclick="addItem()">+ ADD</button>
  </div>
  <div class="template-hint">
    Items added here become part of your daily template — they appear every day
    with fresh checkboxes. Checks reset at midnight; the template never does.
  </div>
</div>

<script>
let _items = [];
let _today = '';

function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function fmtToday() {
  return new Date().toLocaleDateString('en-US',
    { weekday:'long', month:'long', day:'numeric' });
}

async function api(method, path, body) {
  const opts = { method, headers:{'Content-Type':'application/json'} };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(path, opts);
  return r.json();
}

async function load() {
  _today = todayStr();
  document.getElementById('r-date').textContent = fmtToday();
  try {
    _items = await api('GET', '/api/routine?date=' + _today);
  } catch(e) { _items = []; }
  render();
}

async function addItem() {
  const inp = document.getElementById('r-inp');
  const text = inp.value.trim();
  if (!text) return;
  try {
    const item = await api('POST', '/api/routine/items', { text });
    item.checked = 0;
    _items.push(item);
    inp.value = '';
    render();
  } catch(e) { console.error('addItem', e); }
}

async function toggleItem(id) {
  const item = _items.find(x => x.id === id);
  if (!item) return;
  const newChecked = !item.checked;
  item.checked = newChecked ? 1 : 0;
  render();
  try {
    await api('POST', '/api/routine/check', { item_id: id, date: _today, checked: newChecked });
  } catch(e) {
    // revert on failure
    item.checked = newChecked ? 0 : 1;
    render();
  }
}

async function deleteItem(id) {
  _items = _items.filter(x => x.id !== id);
  render();
  try {
    await api('DELETE', `/api/routine/items/${id}`);
  } catch(e) { console.error('deleteItem', e); }
}

function render() {
  const list = document.getElementById('routine-list');
  const wrap = document.getElementById('progress-wrap');
  const fill = document.getElementById('progress-fill');
  const ptext = document.getElementById('progress-text');
  const secLabel = document.getElementById('sec-checklist');
  const allDone = document.getElementById('all-done');
  if (!list) return;

  list.innerHTML = '';

  const total = _items.length;
  const done  = _items.filter(x => x.checked).length;

  if (total === 0) {
    const em = document.createElement('div');
    em.className = 'empty';
    em.textContent = 'NO ITEMS YET — ADD YOUR FIRST ROUTINE ITEM BELOW';
    list.appendChild(em);
    wrap.style.display = 'none';
    secLabel.style.display = 'none';
    allDone.classList.remove('visible');
  } else {
    wrap.style.display = '';
    secLabel.style.display = '';
    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
    fill.style.width = pct + '%';
    ptext.textContent = `${done} / ${total}`;
    allDone.classList.toggle('visible', done === total && total > 0);

    _items.forEach(item => {
      const div = document.createElement('div');
      div.className = 'routine-item' + (item.checked ? ' checked' : '');

      const chk = document.createElement('div');
      chk.className = 'ri-check' + (item.checked ? ' checked' : '');
      chk.onclick = () => toggleItem(item.id);
      div.appendChild(chk);

      const txt = document.createElement('div');
      txt.className = 'ri-text';
      txt.textContent = item.text;
      div.appendChild(txt);

      const del = document.createElement('button');
      del.className = 'ri-del';
      del.textContent = '×';
      del.title = 'Remove from template';
      del.onclick = () => deleteItem(item.id);
      div.appendChild(del);

      list.appendChild(div);
    });
  }
}

// ── Expose to window ──────────────────────────────────────────────────────────
window.addItem    = addItem;
window.__pageInit = function() { load(); };
</script>
</body>
</html>"""
