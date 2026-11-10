"""Deterministic safety rules. These run in code, not in the model, so they cannot be talked out of firing."""
import re

from . import config

F = re.I | re.S

PATTERNS = {
    # A notice/summons the user RECEIVED, or a hearing. (Wanting to SEND a notice does not match.)
    "court_notice": re.compile(
        r"\b(summons|court notice|hearing|cause list|ex[- ]?parte|bailable warrant)\b"
        r"|(received|got|served|came|arrived|मिला|आया).{0,40}\b(notice|summons)\b"
        r"|समन|सुनवाई|कोर्ट.{0,12}नोटिस|नोटिस (मिला|आया)|अदालत.{0,12}नोटिस", F),
    "criminal": re.compile(
        r"\b(FIR|police|arrest(ed)?|bail|criminal|chargesheet|cheque bounce|section 138|IPC|BNS)\b"
        r"|गिरफ्तार|पुलिस|एफआईआर|जमानत|आपराधिक", F),
    "ongoing_case": re.compile(
        r"(case|suit|petition)\s+(is\s+)?(already\s+)?(pending|filed|going on|ongoing)"
        r"|(already|has|have)\s+filed\s+(a\s+)?(case|suit|petition)"
        r"|मुकदमा|केस (चल|दायर)", F),
    "complex_matter": re.compile(
        r"\b(divorce|custody|maintenance|alimony|inheritance|partition|ancestral|property title|"
        r"constitutional|writ petition|adoption|domestic violence)\b"
        r"|तलाक|वसीयत|संपत्ति विवाद|गुजारा भत्ता", F),
    "emergency": re.compile(
        r"\b(threaten(ed|ing)?\s+(to\s+)?(kill|hurt|harm)|beat(ing)?\s+me|assault(ed)?|"
        r"physical(ly)?\s+(abuse|violence)|suicid\w*|kill myself|want to die|in danger)\b"
        r"|जान से मार|मारपीट|हिंसा|आत्महत्या|खतरे में", F),
}

ESCALATION_REASONS = {
    "court_notice": "You mention a court notice, summons or hearing. These carry deadlines that only someone who has read the actual document can confirm.",
    "criminal": "Criminal or police matters are outside what this tool can safely handle.",
    "ongoing_case": "There appears to be an ongoing or filed court case.",
    "complex_matter": "Family, property or constitutional matters are complex and outside this tool's scope.",
    "emergency": "There may be a risk to your safety.",
    "substantial_amount": "The amount involved is substantial.",
    "unsupported_category": "This kind of problem is outside the areas this tool covers.",
    "low_confidence": "The applicable legal position could not be confidently identified from verified sources.",
}


def scan(text):
    return [name for name, rx in PATTERNS.items() if rx.search(text or "")]


def reasons(flags, amount_inr=None, category=None, low_confidence=False):
    out = list(flags)
    if isinstance(amount_inr, (int, float)) and amount_inr >= config.SUBSTANTIAL_AMOUNT_INR:
        out.append("substantial_amount")
    if category == "out_of_scope":
        out.append("unsupported_category")
    if low_confidence:
        out.append("low_confidence")
    seen, uniq = set(), []
    for r in out:
        if r not in seen:
            seen.add(r)
            uniq.append(r)
    return [{"code": r, "reason": ESCALATION_REASONS[r]} for r in uniq if r in ESCALATION_REASONS]


# --- privacy: redact before text reaches the model, DB or logs ---
REDACT = [
    (re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}\b"), "[card number removed]"),
    (re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"), "[12-digit ID removed]"),
    (re.compile(r"\b(otp|pin|password|cvv)\b\s*(is|:)?\s*\S+", re.I), "[secret removed]"),
]


def redact(text):
    for rx, rep in REDACT:
        text = rx.sub(rep, text)
    return text
