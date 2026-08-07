import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db


def _reset_tickets():
    with db._conn() as con:
        con.execute("DELETE FROM tickets")
        con.execute("DELETE FROM sqlite_sequence WHERE name='tickets'")


def setup_module():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db.DB_PATH = Path(tmp.name)
    db._pool = db._Pool()
    db.init_db()


def setup_function():
    _reset_tickets()


def teardown_function():
    _reset_tickets()


def teardown_module():
    try:
        db.DB_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def test_tickets_can_be_created_and_moved_between_columns():
    ticket = db.create_ticket("Ship release", "Prepare rollout", "p0")
    assert ticket["done"] == 0

    updated = db.update_ticket(ticket["id"], done=True)
    assert updated["done"] == 1

    all_tickets = db.get_all_tickets()
    assert any(item["id"] == ticket["id"] and item["done"] == 1 for item in all_tickets)


def test_done_tickets_can_be_pruned_and_due_tickets_can_be_found():
    due_ticket = db.create_ticket("Review design", "Check the mocks", "p1", "2026-08-04")
    done_ticket = db.create_ticket("Archive notes", "Done already", "p2")
    db.update_ticket(done_ticket["id"], done=True)

    pruned = db.delete_done_tickets()
    due = db.get_pending_tickets_due_on("2026-08-04")

    assert pruned == 1
    assert any(item["id"] == due_ticket["id"] for item in due)
    assert not any(item["id"] == done_ticket["id"] for item in db.get_all_tickets())


def test_ticket_template_uses_page_lifecycle_cleanup_for_listeners():
    template_path = Path(__file__).resolve().parents[1] / "templates" / "tickets.html"
    template = template_path.read_text(encoding="utf-8")

    assert "window.__pageInit = function" in template
    assert "window.__pageDestroy = function" in template
    assert "function registerPageListener" in template
    assert "pageListeners.forEach" in template
