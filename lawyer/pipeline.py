"""Orchestration. The model does language understanding and drafting; code does classification
bookkeeping, missing-information detection, retrieval, citation validation and safety decisions.

Per message:  redact -> safety scan -> [LLM] analyze -> code: merge case + missing slots
              -> choose mode (emergency | urgent | out_of_scope | citation_check | ask | guidance | followup)
              -> [LLM] reply/guidance -> code: validate citations, rebuild citations from KB, add escalation.
"""
import json
import re
from datetime import date

from . import config, db, kb, llm, prompts, safety, texts, validate

LANG_NAME = {"en": "English", "hi": "Hindi (Devanagari script)"}
URGENT_FLAGS = {"court_notice", "criminal", "ongoing_case"}
SUPPORTED = ("tenant", "consumer", "employment")
EMPTY = (None, "", "null", "unknown", "n/a", "not provided", "not stated", "not mentioned")

GUIDANCE_READY = {
    "en": "I have prepared guidance based on what you shared. Open the Guidance tab to see your options, the verified legal references, and the documents I can draft. Please read the uncertainties section too.",
    "hi": "आपके बताए तथ्यों के आधार पर मैंने मार्गदर्शन तैयार किया है। अपने विकल्प, सत्यापित कानूनी संदर्भ और मेरे द्वारा तैयार किए जा सकने वाले दस्तावेज़ देखने के लिए Guidance टैब खोलें। कृपया अनिश्चितताओं वाला भाग भी पढ़ें।",
}
CITATION_INTRO = {
    "en": "Here is what I can confirm on this topic from my curated official-source entries:",
    "hi": "इस विषय पर मेरे चुने हुए आधिकारिक-स्रोत वाले प्रविष्टियों से मैं यह पुष्टि कर सकता हूँ (मूल पाठ अंग्रेज़ी में):",
}
CITATION_OUTRO = {
    "en": "If you tell me what happened (who, when, how much, and where in India), I can look at your actual situation.",
    "hi": "यदि आप बताएँ कि क्या हुआ (कौन, कब, कितनी राशि, और भारत में कहाँ), तो मैं आपकी वास्तविक स्थिति देख सकता हूँ।",
}


def _lang(case):
    return case.get("language") if case.get("language") in ("en", "hi") else "en"


def slim(case):
    keys = ("category", "title", "summary", "slots", "amount_inr", "parties", "timeline", "evidence",
            "facts_provided", "ai_interpretations")
    return {k: case.get(k) for k in keys}


def missing_slots(case):
    cat = case.get("category")
    if cat not in SUPPORTED:
        return []
    return [{"key": k, "question": d} for k, d in prompts.slots_for(cat).items()
            if case.get("slots", {}).get(k) in EMPTY]


# ---------------------------------------------------------------- LLM steps
def _analyze(case, hist, trace):
    transcript = "\n".join(("USER: " if m["role"] == "user" else "ASSISTANT: ") + m["content"] for m in hist)
    content = "EXISTING_CASE:\n" + json.dumps(slim(case), ensure_ascii=False) + "\n\nCONVERSATION:\n" + transcript
    parsed, raw = llm.complete_json(prompts.analyze_system(), [{"role": "user", "content": content}])
    trace.append({"step": "analyze", "raw_llm_output": raw})
    return parsed


def _merge(case, a, lang_pref):
    cat = a.get("category")
    if cat in prompts.CATEGORIES:
        if not (cat == "unclear" and case.get("category") in SUPPORTED):
            case["category"] = cat
    for k, v in (a.get("slots") or {}).items():
        if v not in EMPTY and str(v).strip().lower() not in EMPTY:
            case["slots"][k] = str(v).strip()
    for k in ("title", "summary"):
        if isinstance(a.get(k), str) and a[k].strip():
            case[k] = a[k].strip()
    amt = a.get("amount_inr")
    if isinstance(amt, (int, float)) and not isinstance(amt, bool):
        case["amount_inr"] = amt
    for k in ("parties", "timeline", "evidence", "facts_provided", "ai_interpretations"):
        if isinstance(a.get(k), list) and a[k]:
            case[k] = a[k]
    if lang_pref in ("en", "hi"):
        case["language"] = lang_pref
    elif a.get("language") in ("en", "hi"):
        case["language"] = a["language"]
    elif case.get("language") not in ("en", "hi"):
        case["language"] = "en"


def _reply_ask(case, missing, user_text, trace):
    lang = _lang(case)
    if case.get("category") in SUPPORTED:
        needs = [m["question"] for m in missing][:6]
    else:
        needs = ["What happened and who the other party is (landlord, seller/company, employer, other)",
                 "Where in India this happened (state and city)",
                 "What outcome the user wants",
                 "Any key dates, amounts and documents"]
    content = json.dumps({"category": case.get("category"), "summary": case.get("summary"),
                          "facts_provided": case.get("facts_provided"), "missing_information": needs,
                          "user_latest_message": user_text}, ensure_ascii=False)
    raw = llm.complete(prompts.ask_system(LANG_NAME[lang]), [{"role": "user", "content": content}])
    trace.append({"step": "ask", "raw_llm_output": raw})
    return validate.scrub_text(raw, [])[0].strip()


def _reply_urgent(case, user_text, hist, trace):
    lang = _lang(case)
    raw = llm.complete(prompts.urgent_system(LANG_NAME[lang]), hist[-6:] or [{"role": "user", "content": user_text}])
    trace.append({"step": "urgent", "raw_llm_output": raw})
    return validate.scrub_text(raw, [])[0].strip() + "\n\n" + texts.URGENT_BLOCK[lang]


def _guidance(case, missing, user_text, trace):
    lang = _lang(case)
    entries = kb.retrieve(case["category"])
    payload = {"case": slim(case), "missing_information": [m["question"] for m in missing],
               "kb": kb.for_model(entries), "user_latest_message": user_text,
               "today": date.today().isoformat()}
    g, raw = llm.complete_json(prompts.guidance_system(LANG_NAME[lang]),
                               [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}])
    trace.append({"step": "guidance", "raw_llm_output": raw})

    verified_entries = [e for e in entries if e.get("section")]
    removed = []
    used_ids = []
    for field in ("rights", "remedies"):
        clean_items = []
        for item in (g.get(field) or []):
            if isinstance(item, str):
                item = {"text": item, "kind": "general_information", "kb_ids": []}
            ids = validate.valid_ids(item.get("kb_ids"), entries)
            item["kb_ids"] = ids
            item["supported"] = bool(ids)  # UI flags points with no verified-source backing
            if item.get("kind") not in ("general_information", "interpretation", "case_specific"):
                item["kind"] = "interpretation"
            if not ids and item["kind"] == "case_specific":
                item["kind"] = "interpretation"
            used_ids += ids
            clean_items.append(item)
        g[field] = clean_items
    g = validate.scrub_obj(g, verified_entries, removed)

    seen = []
    for i in used_ids:
        if i not in seen:
            seen.append(i)
    citations = [kb.citation(kb.load()[i]) for i in seen]
    low_conf = not citations
    reasons = safety.reasons(case.get("flags", []), case.get("amount_inr"), case.get("category"), low_conf)
    g["advocate_recommended"] = bool(g.get("advocate_recommended")) or bool(reasons)
    g["advocate_reasons_system"] = reasons
    g["citations"] = citations
    g["removed_references"] = removed
    g["missing_information"] = [m["question"] for m in missing]
    g["disclaimer"] = texts.DISCLAIMER[lang]
    return g


def _followup(case, user_text, hist, trace):
    lang = _lang(case)
    entries = kb.retrieve(case["category"])
    system = (f"You answer a follow-up question from a person in India about their own case. Reply in {LANG_NAME[lang]}, under 150 words. "
              "Use ONLY the KB entries given for legal points; if KB does not cover the question, say verified sources were not available "
              "for that and suggest an advocate. Never write section numbers, case names, fees or deadlines that are not in a KB entry's own text. "
              "Never promise outcomes. Do not invent facts about the user.")
    payload = {"case": slim(case), "kb": kb.for_model(entries), "history": hist[-6:], "question": user_text}
    raw = llm.complete(system, [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}])
    trace.append({"step": "followup", "raw_llm_output": raw})
    return validate.scrub_text(raw, [e for e in entries if e.get("section")])[0].strip()


# ---------------------------------------------------------------- public API
def view(case):
    c = dict(case)
    c["missing_information"] = missing_slots(case)
    c["escalation"] = safety.reasons(case.get("flags", []), case.get("amount_inr"), case.get("category"))
    c["documents_available"] = prompts.DOC_TYPES_FOR_CATEGORY.get(case.get("category"), [])
    return c


def handle_message(case_id, user_text, lang_pref="auto", force_guidance=False, trace=None):
    trace = trace if trace is not None else []
    case = db.get_case(case_id) or db.new_case(lang_pref)
    if lang_pref in ("en", "hi"):
        case["language"] = lang_pref
    text = safety.redact((user_text or "").strip()[: config.MAX_INPUT_CHARS])
    db.add_message(case["id"], "user", text)
    hist = db.get_messages(case["id"], limit=14)

    flags = safety.scan(text)
    case["flags"] = sorted(set(case.get("flags", [])) | set(flags))

    prev_slots = dict(case.get("slots", {}))
    a = _analyze(case, hist, trace)
    _merge(case, a, lang_pref)
    lang = _lang(case)
    missing = missing_slots(case)
    cat = case.get("category")
    force = force_guidance or bool(a.get("asks_for_guidance_now"))
    new_info = case.get("slots", {}) != prev_slots

    # user-cited sections: check deterministically
    cited = validate.check_user_cited_sections(text, list(kb.load().values()))
    unverified = [c for c in cited if not c["verified"]]

    guidance = None
    extra_citations = []
    if "emergency" in case["flags"] and "emergency" in flags:
        mode, reply = "emergency", texts.EMERGENCY[lang]
    elif set(case["flags"]) & URGENT_FLAGS:
        mode, reply = "urgent", _reply_urgent(case, text, hist, trace)
    elif "complex_matter" in flags or cat == "out_of_scope":
        mode, reply = "out_of_scope", texts.OUT_OF_SCOPE[lang]
    elif unverified:
        mode = "citation_check"
        entries = [e for e in kb.retrieve(cat) if e["category"] == cat] if cat in SUPPORTED else []
        entries = [e for e in entries if e["verification"] in ("verified", "secondary_verified")][:3]
        extra_citations = [kb.citation(e) for e in entries]
        parts = [texts.UNVERIFIED_SECTION_NOTICE[lang].format(ref=unverified[0]["ref"])]
        if entries:
            bullets = [f"- {e['act']}" + (f", Section {e['section']}" if e.get("section") else "") + f": {e['summary']}"
                       for e in entries]
            parts.append(CITATION_INTRO[lang] + "\n" + "\n".join(bullets))
        parts.append(CITATION_OUTRO[lang])
        reply = "\n\n".join(parts)
    elif cat in SUPPORTED and case.get("guidance_done") and not new_info and not force:
        mode, reply = "followup", _followup(case, text, hist, trace)
    elif cat in SUPPORTED and (not missing or force or case.get("followup_rounds", 0) >= config.MAX_FOLLOWUP_ROUNDS):
        mode = "guidance"
        guidance = _guidance(case, missing, text, trace)
        case["guidance"], case["guidance_done"] = guidance, True
        reply = guidance.get("problem", "") + "\n\n" + GUIDANCE_READY[lang]
    else:
        mode = "ask"
        case["followup_rounds"] = case.get("followup_rounds", 0) + 1
        reply = _reply_ask(case, missing, text, trace)

    db.add_message(case["id"], "assistant", reply)
    db.save_case(case)
    return {"case_id": case["id"], "mode": mode, "reply": reply, "guidance": guidance,
            "citations": extra_citations, "wants_document": a.get("wants_document"),
            "case": view(case), "flags_this_turn": flags}


def generate_document(case_id, doc_type, language=None, trace=None):
    trace = trace if trace is not None else []
    case = db.get_case(case_id)
    if not case:
        raise ValueError("Case not found")
    cat = case.get("category")
    if cat not in SUPPORTED:
        raise ValueError("Documents can be drafted only for supported case categories")
    if doc_type not in prompts.DOC_TYPES_FOR_CATEGORY.get(cat, []):
        raise ValueError("This document type is not available for this case category")
    lang = language if language in ("en", "hi") else _lang(case)
    entries = kb.retrieve(cat)
    payload = {"case": slim(case), "missing_information": [m["question"] for m in missing_slots(case)],
               "kb": kb.for_model(entries), "today": date.today().isoformat()}
    d, raw = llm.complete_json(prompts.document_system(LANG_NAME[lang], prompts.DOC_TYPES[doc_type]),
                               [{"role": "user", "content": json.dumps(payload, ensure_ascii=False)}])
    trace.append({"step": "document", "raw_llm_output": raw})
    removed = []
    body = validate.scrub_obj(str(d.get("body", "")), [e for e in entries if e.get("section")], removed)
    ids = validate.valid_ids(d.get("kb_ids_used"), entries)
    ph = []
    for p in re.findall(r"\[[^\[\]\n]{2,80}\]", body):
        if not p.startswith(("[reference removed", "[case citation removed")) and p not in ph:
            ph.append(p)
    return {"title": d.get("title") or prompts.DOC_TYPES[doc_type], "body": body,
            "banner": texts.DOC_BANNER[lang], "placeholders": ph,
            "notes_for_user": validate.scrub_obj(d.get("notes_for_user") or [], [], removed),
            "citations": [kb.citation(kb.load()[i]) for i in ids], "removed_references": removed,
            "language": lang, "doc_type": doc_type}
