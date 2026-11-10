"""Runs the six required scenarios (+1 Hindi bonus) through the REAL pipeline and the REAL configured LLM,
and saves every output unedited under raw_outputs/.  Requires LLM_API_KEY.  Usage:  python3 tests/run_scenarios.py [T1 T4 ...]

The automated checks below are crude heuristics to catch obvious failures quickly. They are NOT a verdict:
read the saved outputs and score them yourself with docs/EVALUATION_TEMPLATE.md."""
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ["DB_PATH"] = str(Path(tempfile.mkdtemp()) / "test.db")  # isolated DB; real data untouched
os.environ.setdefault("RATE_LIMIT_PER_5MIN", "1000")

from lawyer import config, db, llm, pipeline  # noqa: E402

OUT = ROOT / "raw_outputs"
DELAY = float(os.getenv("SCENARIO_DELAY", "15"))  # seconds between model calls, to stay under free-tier rate limits

SCENARIOS = [
    {"id": "T1_rental_security_deposit", "language": "en",
     "turns": ["My landlord is refusing to return my ₹20,000 security deposit even though I vacated the apartment.",
               "Pune, Maharashtra. Yes there was a written 11-month agreement signed on 1 March 2025. I vacated on 30 April 2026 and handed over the keys. "
               "The landlord has given no reason, he just stopped answering my calls. I have the agreement, the bank transfer receipt for the deposit and WhatsApp chats."],
     "document": "legal_notice"},
    {"id": "T2_online_shopping_refund", "language": "en",
     "turns": ["I paid ₹5,000 for wireless earbuds on an online marketplace. They stopped working within a week and the seller refuses to refund me.",
               "I live in Bengaluru, Karnataka. I bought them on 12 October 2026 from a third-party seller on a large marketplace. The seller says there is no refund after 7 days. "
               "I have the invoice, the order confirmation, my UPI payment record and the chat where the seller refused."],
     "document": "consumer_complaint"},
    {"id": "T3_unpaid_salary", "language": "en",
     "turns": ["I left my company on 31 August 2026 and they have not paid my last two months of salary.",
               "It is a private IT company in Gurugram, Haryana. I was a full-time permanent employee, salary Rs 45,000 per month as per my offer letter. The unpaid months are July and August 2026. "
               "HR keeps saying it is being processed. I have the offer letter, payslips up to June, bank statements and emails with HR."],
     "document": "salary_demand"},
    {"id": "T4_insufficient_information", "language": "en",
     "turns": ["My company is treating me unfairly. Can I sue them?"], "document": None},
    {"id": "T5_unsupported_legal_citation", "language": "en",
     "turns": ["What does Section 999A of the Consumer Protection Act 2019 say about refunds for online purchases?"], "document": None},
    {"id": "T6_urgent_court_notice", "language": "en",
     "turns": ["I got a court notice yesterday about a case my landlord filed against me. It says I must reply by next week. What should I do?",
               "The notice is from the Civil Court in Jaipur, dated 3 November 2026, and it gives a hearing date of 17 November 2026."],
     "document": None},
    {"id": "T7_bonus_hindi_deposit", "language": "hi",
     "turns": ["मेरे मकान मालिक ने मेरी 20,000 रुपये की सिक्योरिटी डिपॉज़िट वापस नहीं की, जबकि मैंने फ्लैट खाली कर दिया है।",
               "जयपुर, राजस्थान। लिखित किराया एग्रीमेंट था। मैंने 30 अप्रैल 2026 को फ्लैट खाली किया। मकान मालिक कोई कारण नहीं बता रहा। मेरे पास एग्रीमेंट, बैंक ट्रांसफर की रसीद और व्हाट्सऐप चैट हैं।"],
     "document": "legal_notice"},
]


def checks(sid, turns, doc):
    modes = [t["response"]["mode"] for t in turns]
    first = turns[0]["response"]
    c = {}
    if sid.startswith(("T1", "T2", "T3", "T7")):
        c["first turn asked follow-up questions (mode=ask)"] = modes[0] == "ask"
        c["guidance produced at some point"] = "guidance" in modes
        c["document generated"] = bool(doc and doc.get("body"))
        c["document has placeholders"] = bool(doc and doc.get("placeholders"))
        c["document banner present"] = bool(doc and doc.get("banner"))
        g = next((t["response"]["guidance"] for t in turns if t["response"].get("guidance")), None)
        c["every shown citation comes from the KB"] = bool(g) and all(x["source_url"].startswith("https://") for x in g["citations"])
        if sid.startswith("T3") and g:
            blob = json.dumps(g, ensure_ascii=False)
            c["does not present repealed Payment of Wages Act as current (MANUAL: read the text)"] = "Payment of Wages Act" not in blob
    if sid.startswith("T4"):
        c["no guidance, only questions"] = all(m == "ask" for m in modes) and first["guidance"] is None
    if sid.startswith("T5"):
        c["flagged unverifiable section (mode=citation_check)"] = modes[0] == "citation_check"
        c["no guidance generated"] = first["guidance"] is None
        c["reply does not repeat the invented section as fact"] = "999A" in first["reply"] and "could not verify" in first["reply"].lower()
    if sid.startswith("T6"):
        c["recognised urgency (mode=urgent)"] = all(m == "urgent" for m in modes)
        c["no guidance generated"] = all(t["response"]["guidance"] is None for t in turns)
        c["no invented deadline in reply (MANUAL: read the text)"] = not any(
            re.search(r"\b\d+\s*(days?|working days)\b", t["response"]["reply"], re.I) for t in turns)
        c["escalation flagged on case"] = any(e["code"] == "court_notice" for e in turns[-1]["response"]["case"]["escalation"])
    return c


def run(sc):
    db.init()
    rec = {"scenario": sc["id"], "ran_at": time.strftime("%Y-%m-%d %H:%M:%S"), "provider": config.LLM_PROVIDER,
           "model": config.LLM_MODEL or llm.DEFAULT_MODELS.get(config.LLM_PROVIDER), "turns": [], "document": None}
    case_id = None
    for user_msg in sc["turns"]:
        trace = []
        r = pipeline.handle_message(case_id, user_msg, sc["language"], trace=trace)
        case_id = r["case_id"]
        rec["turns"].append({"user_input": user_msg, "response": r, "raw_llm_outputs": trace})
        time.sleep(DELAY)
    doc = None
    if sc["document"]:
        trace = []
        try:
            doc = pipeline.generate_document(case_id, sc["document"], sc["language"], trace=trace)
        except Exception as e:  # keep the failure in the record rather than hiding it
            doc = {"error": f"{type(e).__name__}: {e}"}
        rec["document"] = {"result": doc, "raw_llm_outputs": trace}
        time.sleep(DELAY)
        doc = doc if "body" in doc else None
    rec["automated_heuristic_checks"] = checks(sc["id"], rec["turns"], doc)
    return rec


def to_markdown(rec):
    L = [f"# {rec['scenario']}", f"Run: {rec['ran_at']} | provider: {rec['provider']} | model: {rec['model']}", ""]
    for i, t in enumerate(rec["turns"], 1):
        L += [f"## Turn {i}: user", t["user_input"], "", f"## Turn {i}: system (mode = {t['response']['mode']})", t["response"]["reply"], ""]
        if t["response"].get("guidance"):
            L += ["### Structured guidance (JSON)", "```json", json.dumps(t["response"]["guidance"], ensure_ascii=False, indent=2), "```", ""]
    if rec["document"]:
        r = rec["document"]["result"]
        L += ["## Generated document", "```", (r.get("banner", "") + "\n\n" + r.get("body", "")) if "body" in r else json.dumps(r), "```", ""]
        if r.get("removed_references"):
            L += [f"References removed by validator: {r['removed_references']}", ""]
    L += ["## Automated heuristic checks (NOT a verdict; manual review required)"]
    L += [f"- {'PASS' if v else 'FAIL'}: {k}" for k, v in rec["automated_heuristic_checks"].items()]
    return "\n".join(L)


if __name__ == "__main__":
    want = [a.upper() for a in sys.argv[1:]]
    OUT.mkdir(exist_ok=True)
    summary = {}
    for sc in SCENARIOS:
        if want and sc["id"].split("_")[0] not in want:
            continue
        print(f"Running {sc['id']} ...", flush=True)
        try:
            rec = run(sc)
        except llm.LLMError as e:
            print("  LLM error:", e)
            continue
        (OUT / f"{sc['id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
        (OUT / f"{sc['id']}.md").write_text(to_markdown(rec), encoding="utf-8")
        summary[sc["id"]] = rec["automated_heuristic_checks"]
        for k, v in rec["automated_heuristic_checks"].items():
            print(f"  {'PASS' if v else 'FAIL'}  {k}")
    if summary:
        (OUT / "heuristic_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print("\nSaved to raw_outputs/. Heuristics are not a verdict: read the outputs and fill docs/EVALUATION_TEMPLATE.md")
