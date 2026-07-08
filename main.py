"""
main.py — PranshulOS entry point.
Starts Flask in a background thread, then launches pywebview.
"""
import threading
import time
import sys
import os

# Add this folder to path so flat imports work
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
import db
import routes
import notifier
import updater
from shell import launch


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(routes.bp)
    return app


def start_flask():
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    # Init DB
    db.init_db()

    # Start Flask
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(1.2)   # let Flask bind

    # Start 11 PM task notifier
    notifier.start()

    # Check for a newer version (non-blocking, fails silently offline)
    updater.check_and_notify()

    # Launch window
    launch()
