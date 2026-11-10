"""Knowledge-base loading and retrieval. Retrieval is plain code (by category), not LLM-driven."""
import json
from functools import lru_cache

from .config import ROOT


@lru_cache(maxsize=1)
def load():
    data = json.loads((ROOT / "kb" / "knowledge_base.json").read_text(encoding="utf-8"))
    return {e["id"]: e for e in data["entries"]}


def retrieve(category):
    """Entries for the category plus general ones."""
    return [e for e in load().values() if e["category"] in (category, "general")]


def for_model(entries):
    """What the model is allowed to see. Unchecked section numbers are never included."""
    return [{"id": e["id"], "act": e["act"], "section": e.get("section"), "title": e["title"],
             "summary": e["summary"], "verification": e["verification"],
             "jurisdiction_note": e.get("jurisdiction_note", "")} for e in entries]


def citation(e):
    return {"id": e["id"], "act": e["act"], "section": e.get("section"), "title": e["title"],
            "source_url": e["source_url"], "source_type": e["source_type"],
            "verification": e["verification"], "checked_on": e["checked_on"],
            "jurisdiction_note": e.get("jurisdiction_note", "")}


def section_tokens(section):
    """'34, 47, 58' -> {'34','47','58'}"""
    if not section:
        return set()
    return {s.strip() for s in str(section).split(",") if s.strip()}
