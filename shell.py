"""
shell.py — PranshulOS
pywebview window, JS API, sidebar injection.

All actions here open general websites in the default browser.
No local app shortcuts, no machine-specific paths — this makes the
app portable across any Windows machine, not just the dev machine.
"""
import webview

FLASK_HOME = "http://127.0.0.1:5000/home"


# ── API ────────────────────────────────────────────────────────────────────────

class PranshulAPI:
    """Each method opens a general-purpose website. Kept intentionally simple
    and machine-agnostic: no os.startfile, no hardcoded shortcut paths."""

    def _open(self, url: str, message: str) -> str:
        import webbrowser
        webbrowser.open(url)
        return message

    def open_drive(self):
        return self._open("https://drive.google.com/drive/u/0/home", "Opened Google Drive")

    def open_spotify(self):
        return self._open("https://open.spotify.com", "Opened Spotify")

    def open_youtube(self):
        return self._open("https://youtube.com", "Opened YouTube")

    def open_linkedin(self):
        return self._open("https://www.linkedin.com", "Opening LinkedIn...")

    def open_github(self):
        return self._open("https://github.com", "Opening GitHub...")

    def open_whatsapp(self):
        return self._open("https://web.whatsapp.com", "Opening WhatsApp...")

    def open_discord(self):
        return self._open("https://discord.com/app", "Opening Discord...")

    def open_twitch(self):
        return self._open("https://twitch.tv", "Opening Twitch...")

    def open_roblox(self):
        return self._open("https://www.roblox.com", "Opening Roblox...")

    def open_steam(self):
        return self._open("https://store.steampowered.com", "Opened Steam")

    def open_warframe_market(self):
        return self._open("https://warframe.market/", "Opening Warframe Market...")

    def chill(self):
        return self._open("https://youtube.com", "Opened YouTube — chill time 🎬")

    def chatgpt_ai(self):
        return self._open("https://chatgpt.com", "Opening ChatGPT...")

    def open_instagram(self):
        return self._open("https://www.instagram.com", "Opening Instagram...")

    def open_gmail(self):
        return self._open("https://mail.google.com", "Opening Gmail...")

    def open_reddit(self):
        return self._open("https://www.reddit.com", "Opened Reddit")

    def test_notification(self):
        """Fire a test toast to verify plyer works."""
        try:
            import notifier
            notifier.test_notification()
            return "Test notification sent!"
        except Exception as e:
            return f"Error: {e}"

    def check_trigger(self, text: str):
        t = text.lower().strip()
        triggers = [
            (["drive"],                                                self.open_drive),
            (["reddit"],                                               self.open_reddit),
            (["chatgpt", "open chatgpt", "open the ai"],                self.chatgpt_ai),
            (["youtube", "bored", "not feeling", "too lazy", "chill"],  self.chill),
            (["update my profile", "update profile", "linkedin"],      self.open_linkedin),
            (["push the code", "create a repo", "add to repo", "github", "git"], self.open_github),
            (["whatsapp", "check messages", "check whatsapp"],         self.open_whatsapp),
            (["discord", "check discord"],                             self.open_discord),
            (["twitch", "watch streams", "streaming"],                 self.open_twitch),
            (["roblox", "play roblox"],                                self.open_roblox),
            (["steam", "play games", "check games"],                   self.open_steam),
            (["warframe market", "check prices for prime", "check prices for mod", "check prices for mods"], self.open_warframe_market),
            (["spotify", "music"],                                     self.open_spotify),
            (["instagram"],                                            self.open_instagram),
            (["gmail", "open my mail", "open mail"],                   self.open_gmail),
        ]
        results, fired = [], set()
        for keywords, fn in triggers:
            if any(kw in t for kw in keywords) and fn.__name__ not in fired:
                try:
                    msg = fn()
                    if msg: results.append(msg)
                    fired.add(fn.__name__)
                except Exception as e:
                    results.append(f"Error: {e}")
        return " · ".join(results) if results else None


# ── Sidebar (injected into every page) ────────────────────────────────────────

INJECT_JS = """
(function() {
  if (document.getElementById('pos-sidebar')) return;
  const style = document.createElement('style');
  style.textContent = `
    #pos-sidebar {
      position: fixed; top: 0; left: 0; width: 180px; height: 100vh;
      background: #0e0e0e; border-right: 1px solid #222;
      display: flex; flex-direction: column;
      font-family: 'IBM Plex Mono', 'Courier New', monospace;
      z-index: 99999; box-sizing: border-box;
    }
    #pos-sidebar .pos-logo {
      padding: 20px 16px 14px; font-size: 11px; font-weight: 700;
      letter-spacing: 0.15em; color: #e8a84c; border-bottom: 1px solid #222;
    }
    #pos-sidebar .pos-nav { padding: 12px 10px; flex: 1; overflow-y: auto; }
    #pos-sidebar .pos-nav-btn {
      display: block; width: 100%; padding: 9px 14px; margin-bottom: 3px;
      border-radius: 8px; border: none; background: transparent; color: #4a4845;
      font-family: inherit; font-size: 13px; text-align: left; cursor: pointer;
      transition: all 0.15s;
    }
    #pos-sidebar .pos-nav-btn:hover  { background: #1c1c1c; color: #8a8880; }
    #pos-sidebar .pos-nav-btn.active { background: #1c1c1c; color: #e8a84c; }
    #pos-sidebar .pos-section {
      padding: 14px 14px 4px; font-size: 9px; letter-spacing: 0.12em;
      color: #2e2e2e; text-transform: uppercase;
    }
    #pos-sidebar .pos-ver {
      padding: 12px 16px; font-size: 9px; color: #2e2e2e;
      border-top: 1px solid #1a1a1a;
    }
    body { margin-left: 180px !important; }
  `;
  document.head.appendChild(style);

  const sb = document.createElement('div');
  sb.id = 'pos-sidebar';
  sb.innerHTML = `
    <div class="pos-logo">FLUIDCB</div>
    <div class="pos-nav">
      <div class="pos-section">Navigate</div>
      <button class="pos-nav-btn" id="btn-home" onclick="window.location.href='/home'">🏠 Home</button>
      <button class="pos-nav-btn" id="btn-dash" onclick="window.location.href='/dashboard'">📋 Dashboard</button>
      <button class="pos-nav-btn" id="btn-docs" onclick="window.location.href='/docs'">📝 Docs</button>
      <div class="pos-section">Apps</div>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_youtube()">🎬 YouTube</button>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_spotify()">🎵 Spotify</button>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_whatsapp()">💬 WhatsApp</button>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_discord()">🎮 Discord</button>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_github()">🐙 GitHub</button>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_linkedin()">🔗 LinkedIn</button>
      <button class="pos-nav-btn" onclick="window.pywebview.api.open_gmail()">✉️ Gmail</button>
    </div>
    <div class="pos-ver">v2.0 · pranshulos</div>
  `;

  const path = window.location.pathname;
  document.body.prepend(sb);
  document.getElementById('btn-home').className = 'pos-nav-btn' + (path === '/home' ? ' active' : '');
  document.getElementById('btn-dash').className = 'pos-nav-btn' + (path === '/dashboard' ? ' active' : '');
  document.getElementById('btn-docs').className = 'pos-nav-btn' + (path === '/docs' ? ' active' : '');
})();
"""


# ── App ────────────────────────────────────────────────────────────────────────

class PranshulOS:
    def __init__(self):
        self.api    = PranshulAPI()
        self.window = webview.create_window(
            "PranshulOS",
            url=FLASK_HOME,
            js_api=self.api,
            width=1100, height=720,
            min_size=(860, 560),
            background_color="#0c0c0c",
        )
        self.window.events.loaded += self._on_load

    def _on_load(self):
        self.window.evaluate_js(INJECT_JS)

    def run(self):
        webview.start(debug=False)


def launch():
    app = PranshulOS()
    app.run()
