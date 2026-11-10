"""SQLite storage. Cases and messages are stored locally, can be deleted by the user, and auto-expire."""
import json
import sqlite3
import time
import uuid
from pathlib import Path

from . import config


def _conn():
    Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY, created REAL, updated REAL, data TEXT);
        CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT, role TEXT, content TEXT, ts REAL);
        CREATE INDEX IF NOT EXISTS idx_msg_case ON messages(case_id);
        """)
        cutoff = time.time() - config.RETENTION_DAYS * 86400
        ids = [r["id"] for r in c.execute("SELECT id FROM cases WHERE updated < ?", (cutoff,))]
        for i in ids:
            c.execute("DELETE FROM messages WHERE case_id=?", (i,))
            c.execute("DELETE FROM cases WHERE id=?", (i,))


def new_case(language="auto"):
    case = {"id": uuid.uuid4().hex, "language": language, "category": "unclear", "title": "", "summary": "",
            "slots": {}, "amount_inr": None, "parties": [], "timeline": [], "evidence": [],
            "facts_provided": [], "ai_interpretations": [], "flags": [], "followup_rounds": 0,
            "guidance_done": False}
    save_case(case)
    return case


def save_case(case):
    now = time.time()
    with _conn() as c:
        c.execute("INSERT INTO cases(id,created,updated,data) VALUES(?,?,?,?) "
                  "ON CONFLICT(id) DO UPDATE SET updated=excluded.updated, data=excluded.data",
                  (case["id"], now, now, json.dumps(case, ensure_ascii=False)))


def get_case(case_id):
    if not case_id:
        return None
    with _conn() as c:
        r = c.execute("SELECT data FROM cases WHERE id=?", (case_id,)).fetchone()
    return json.loads(r["data"]) if r else None


def add_message(case_id, role, content):
    with _conn() as c:
        c.execute("INSERT INTO messages(case_id,role,content,ts) VALUES(?,?,?,?)", (case_id, role, content, time.time()))


def get_messages(case_id, limit=14):
    with _conn() as c:
        rows = c.execute("SELECT role,content FROM messages WHERE case_id=? ORDER BY id DESC LIMIT ?",
                         (case_id, limit)).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def delete_case(case_id):
    with _conn() as c:
        c.execute("DELETE FROM messages WHERE case_id=?", (case_id,))
        c.execute("DELETE FROM cases WHERE id=?", (case_id,))
