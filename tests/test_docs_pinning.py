import tempfile
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import db


def setup_module():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    db.DB_PATH = Path(tmp.name)
    db._pool = db._Pool()
    db.init_db()


def teardown_module():
    try:
        db.DB_PATH.unlink(missing_ok=True)
    except Exception:
        pass


def test_docs_can_be_pinned_and_sorted_first():
    first = db.create_doc("First")
    second = db.create_doc("Second")

    db.update_doc(first["id"], pinned=True)
    docs = db.get_all_docs()

    assert any(doc["id"] == first["id"] and doc["pinned"] is True for doc in docs)
    assert docs[0]["id"] == first["id"]
    assert docs[1]["id"] == second["id"]
