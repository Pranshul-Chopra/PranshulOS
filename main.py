"""
main.py — PranshulOS entry point.
Flask runs as a plain HTTP server on localhost:5000.
The window is handled by Electron (electron/main.js).
When running in dev mode (python main.py directly), Flask serves normally
and you can open http://localhost:5000/home in any browser.
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
import db
import routes
import notifier
import updater


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.register_blueprint(routes.bp)
    return app


def start_flask():
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    db.init_db()

    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Give Flask a moment to bind before notifier/updater fire
    time.sleep(1.0)

    notifier.start()
    updater.check_and_notify()

    # Keep the process alive — Electron manages the window lifecycle.
    # In dev mode (no Electron), Flask runs until you Ctrl+C.
    print("PranshulOS Flask server running at http://127.0.0.1:5000/home")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down.")
