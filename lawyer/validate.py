"""Citation validation. The model never gets the last word on a citation:
(1) it may only reference KB ids; (2) citations shown to the user are rebuilt from the KB by code;
(3) any section number or case citation left in free text that is not backed by a verified KB entry is removed."""
import re

from . import kb

SECTION_RX = re.compile(
    r"(?P<lead>\b(?:sections?|secs?\.?|s\.|धारा)\s*)(?P<num>\d+[A-Za-z]?(?:\([0-9a-zA-Z]+\))*)", re.I)
CASE_RXS = [  # order matters: most specific first
    re.compile(r"\(\d{4}\)\s*\d+\s*(?:SCC|SCR|CPJ)\b(?:\s*\d+)?"),
    re.compile(r"\b(?:AIR|SCC|SCR|CPJ|CTJ)\b\s*(?:\(\w+\)\s*)?\d{2,4}"),
    re.compile(r"\b[A-Z][\w.&'-]*(?: [A-Z][\w.&'-]*){0,4} (?:v\.?|vs\.?) [A-Z][\w.&'-]*(?: [A-Z][\w.&'-]*){0,4}"),
]
SEC_REMOVED = "[reference removed: could not be verified]"
CASE_REMOVED = "[case citation removed: this tool does not cite judgments]"


def allowed_sections(entries):
    """{section_token: [lowercase act keywords]} from entries whose section was actually checked."""
    out = {}
    for e in entries:
        for tok in kb.section_tokens(e.get("section")):
            out.setdefault(tok.lower(), []).append(e["act"].lower())
    return out


def _base(num):
    return re.sub(r"\(.*$", "", num).lower()


def scrub_text(text, entries):
    """Returns (clean_text, removed_list)."""
    if not isinstance(text, str):
        return text, []
    allowed = allowed_sections(entries)
    removed = []

    def fix(m):
        base = _base(m.group("num"))
        acts = allowed.get(base)
        if acts:
            window = text[max(0, m.start() - 200): m.end() + 200].lower()
            keys = [a.split(",")[0].split(" and ")[0] for a in acts]  # leading act name
            if len(set(acts)) == 1 or any(k[:18] in window for k in keys):
                return m.group(0)
        removed.append(m.group(0).strip())
        return SEC_REMOVED

    text = SECTION_RX.sub(fix, text)
    for rx in CASE_RXS:
        def casefix(m):
            removed.append(m.group(0))
            return CASE_REMOVED
        text = rx.sub(casefix, text)
    return text, removed


def scrub_obj(obj, entries, removed=None):
    """Walk any JSON-like structure, scrubbing every string."""
    removed = removed if removed is not None else []
    if isinstance(obj, str):
        clean, r = scrub_text(obj, entries)
        removed.extend(r)
        return clean
    if isinstance(obj, list):
        return [scrub_obj(x, entries, removed) for x in obj]
    if isinstance(obj, dict):
        return {k: scrub_obj(v, entries, removed) for k, v in obj.items()}
    return obj


def valid_ids(ids, entries):
    have = {e["id"] for e in entries}
    return [i for i in (ids or []) if i in have]


def check_user_cited_sections(user_text, entries):
    """If the user names 'Section N of <Act>', say whether we can verify it. Deterministic, no LLM.
    Returns list of {ref, verified, matches:[kb ids]}."""
    results = []
    allowed = allowed_sections(entries)
    for m in SECTION_RX.finditer(user_text or ""):
        base = _base(m.group("num"))
        window = user_text[max(0, m.start() - 120): m.end() + 120].lower()
        matches = []
        for e in entries:
            if base in {t.lower() for t in kb.section_tokens(e.get("section"))}:
                name = e["act"].lower().split(",")[0].split(" and ")[0][:18]
                if name in window:
                    matches.append(e["id"])
        ref = user_text[m.start(): m.end() + 60].strip().split("\n")[0]
        results.append({"ref": ref, "verified": bool(matches), "matches": matches})
    return results
