"""Streamlit version of Nyaya Sahayak (for Streamlit Community Cloud). Same backend as server.py:
lawyer/pipeline.py does all the work, so safety rules, knowledge base and citation checks are identical.
Run locally:  pip install streamlit  &&  streamlit run streamlit_app.py
Secrets (LLM_API_KEY etc.) come from Streamlit's Secrets settings, never from the repo."""
import html
import os
import tempfile

import streamlit as st

# Map Streamlit secrets to environment variables BEFORE importing the backend (it reads env at import time).
for _k in ("LLM_PROVIDER", "LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL", "LLM_JSON_MODE", "LLM_TIMEOUT"):
    try:
        if _k in st.secrets:
            os.environ.setdefault(_k, str(st.secrets[_k]))
    except Exception:  # noqa: BLE001  (no secrets file when running locally with .env)
        pass
os.environ.setdefault("DB_PATH", os.path.join(tempfile.gettempdir(), "nyaya_sahayak.db"))

from lawyer import config, db, llm, pipeline, prompts, texts  # noqa: E402

MAX_MESSAGES_PER_SESSION = 60  # simple cost guard (the stdlib server has per-IP rate limiting instead)

T = {
    "en": {
        "title": "Nyaya Sahayak", "sub": "Plain-language legal help for rent deposits, consumer refunds and unpaid salary in India. General information, not a lawyer.",
        "chat": "Chat", "case": "Case file", "guid": "Guidance", "docs": "Documents",
        "ph": "Describe what happened, in English or Hindi...", "welcome": "Tell me what happened, in your own words. I will ask a few questions, then build your case file. I am an AI, not a lawyer.",
        "force": "Get guidance now", "delete": "Delete this case", "lang": "Language", "thinking": "Thinking...",
        "empty_case": "Your case file builds here as you describe the problem.", "empty_guid": "Guidance appears once I have enough facts, or press 'Get guidance now' in the sidebar.",
        "summary": "Summary", "category": "Category", "location": "Location", "amount": "Amount", "parties": "Parties", "timeline": "Timeline",
        "told": "What you told me", "missing": "Still missing", "ai": "My readings (possible, not verified facts)", "evidence": "Evidence you have",
        "problem": "What the problem appears to be", "rights": "Rights and protections that may apply", "remedies": "Possible remedies",
        "steps": "Practical next steps", "keep": "Keep these as evidence", "unc": "What is uncertain", "refs": "Verified references",
        "adv": "Speak to a qualified advocate", "adv_no": "Consider an advocate if the other side refuses or the amount grows.",
        "unsup": "No verified source entry backs this point", "src": "Official source", "checked": "Checked", "no_sec": "section not cited",
        "removed": "References the system removed because they could not be verified:",
        "doc_head": "Draft a document", "doc_type": "Document type", "doc_lang": "Draft language", "gen": "Generate draft",
        "doc_empty": "Documents become available once your case category is clear.", "edit": "Edit before downloading",
        "dl_txt": "Download .txt", "dl_html": "Download for PDF (open it, then Ctrl+P > Save as PDF)", "ph2": "Placeholders to fill in", "notes": "Check before sending",
        "limit": "Session message limit reached. Please start a new session later.", "nokey": "The AI is not configured. The app owner must set LLM_API_KEY in Secrets.",
        "cats": {"tenant": "Rent / deposit", "consumer": "Consumer", "employment": "Salary / employment", "out_of_scope": "Outside scope", "unclear": "Not yet clear"},
        "kinds": {"general_information": "General information", "interpretation": "Interpretation", "case_specific": "Based on your facts"},
        "verif": {"verified": "Verified in statute text", "secondary_verified": "Confirmed in secondary sources; check official page", "single_secondary": "Single secondary source; provisional",
                  "general_principle": "General principle; no section claimed", "pending_section": "Section number not verified, so none is shown"},
        "docs_names": {"legal_notice": "Legal notice (deposit)", "consumer_complaint": "Consumer complaint", "refund_request": "Refund request",
                       "salary_demand": "Salary demand letter", "reply_to_notice": "Reply to a notice", "grievance_application": "Grievance application"},
    },
    "hi": {
        "title": "न्याय सहायक", "sub": "भारत में किराये की जमा राशि, उपभोक्ता रिफंड और बकाया वेतन के लिए सरल भाषा में कानूनी मदद। सामान्य जानकारी, वकील नहीं।",
        "chat": "बातचीत", "case": "केस फ़ाइल", "guid": "मार्गदर्शन", "docs": "दस्तावेज़",
        "ph": "क्या हुआ, हिंदी या अंग्रेज़ी में बताइए...", "welcome": "क्या हुआ, अपने शब्दों में बताइए। मैं कुछ सवाल पूछूँगा, फिर आपकी केस फ़ाइल बनाऊँगा। मैं AI हूँ, वकील नहीं।",
        "force": "अभी मार्गदर्शन दें", "delete": "यह केस हटाएँ", "lang": "भाषा", "thinking": "सोच रहा हूँ...",
        "empty_case": "जैसे-जैसे आप समस्या बताएँगे, केस फ़ाइल यहाँ बनेगी।", "empty_guid": "पर्याप्त तथ्य मिलने पर, या साइडबार में 'अभी मार्गदर्शन दें' दबाने पर, मार्गदर्शन दिखेगा।",
        "summary": "सारांश", "category": "श्रेणी", "location": "स्थान", "amount": "राशि", "parties": "पक्ष", "timeline": "घटनाक्रम",
        "told": "आपने जो बताया", "missing": "अभी कमी", "ai": "मेरी समझ (संभावित, सत्यापित तथ्य नहीं)", "evidence": "आपके पास सबूत",
        "problem": "समस्या क्या लगती है", "rights": "लागू हो सकने वाले अधिकार और सुरक्षा", "remedies": "संभावित उपाय",
        "steps": "व्यावहारिक अगले कदम", "keep": "इन्हें सबूत के रूप में संभालकर रखें", "unc": "क्या अनिश्चित है", "refs": "सत्यापित संदर्भ",
        "adv": "योग्य अधिवक्ता से बात करें", "adv_no": "यदि दूसरा पक्ष मना करे या राशि बढ़े तो अधिवक्ता पर विचार करें।",
        "unsup": "इस बिंदु के लिए कोई सत्यापित स्रोत प्रविष्टि नहीं है", "src": "आधिकारिक स्रोत", "checked": "जाँचा गया", "no_sec": "धारा नहीं दी गई",
        "removed": "सिस्टम ने ये संदर्भ हटाए क्योंकि इन्हें सत्यापित नहीं किया जा सका:",
        "doc_head": "दस्तावेज़ का मसौदा बनाएँ", "doc_type": "दस्तावेज़ का प्रकार", "doc_lang": "मसौदे की भाषा", "gen": "मसौदा बनाएँ",
        "doc_empty": "केस की श्रेणी स्पष्ट होने पर दस्तावेज़ उपलब्ध होंगे।", "edit": "डाउनलोड से पहले संपादित करें",
        "dl_txt": ".txt डाउनलोड", "dl_html": "PDF के लिए डाउनलोड (खोलें, फिर Ctrl+P > Save as PDF)", "ph2": "भरने के लिए स्थान", "notes": "भेजने से पहले जाँचें",
        "limit": "इस सत्र की संदेश सीमा पूरी हो गई। कृपया बाद में नया सत्र शुरू करें।", "nokey": "AI कॉन्फ़िगर नहीं है। ऐप मालिक को Secrets में LLM_API_KEY सेट करनी होगी।",
        "cats": {"tenant": "किराया / जमा राशि", "consumer": "उपभोक्ता", "employment": "वेतन / रोज़गार", "out_of_scope": "दायरे से बाहर", "unclear": "अभी स्पष्ट नहीं"},
        "kinds": {"general_information": "सामान्य जानकारी", "interpretation": "व्याख्या", "case_specific": "आपके तथ्यों पर आधारित"},
        "verif": {"verified": "कानून के पाठ में सत्यापित", "secondary_verified": "द्वितीयक स्रोतों में पुष्ट; आधिकारिक पेज जाँचें", "single_secondary": "एक द्वितीयक स्रोत; अस्थायी",
                  "general_principle": "सामान्य सिद्धांत; कोई धारा नहीं बताई", "pending_section": "धारा संख्या सत्यापित नहीं, इसलिए नहीं दिखाई गई"},
        "docs_names": {"legal_notice": "कानूनी नोटिस (जमा राशि)", "consumer_complaint": "उपभोक्ता शिकायत", "refund_request": "रिफंड अनुरोध",
                       "salary_demand": "वेतन माँग पत्र", "reply_to_notice": "नोटिस का उत्तर", "grievance_application": "शिकायत आवेदन"},
    },
}


@st.cache_resource
def _init():
    db.init()
    return True


T["en"].update({
    "chips": ["Not a lawyer", "Only verified sources are cited", "English + हिन्दी"],
    "steps": ["Describe", "Answer questions", "Guidance", "Draft letter"],
    "cover": "What this can help with today",
    "cards": [("Rent and deposits", "Deposit not returned, unexplained deductions, agreement disputes."),
              ("Consumer refunds", "Defective products, online refunds, service complaints."),
              ("Unpaid salary", "Unpaid or delayed pay, deductions, pay after leaving a job.")],
    "try": "Or tap an example to start:",
    "examples": ["My landlord is refusing to return my ₹20,000 security deposit even though I vacated the apartment.",
                 "I paid ₹5,000 for earbuds online. They stopped working in a week and the seller refuses a refund.",
                 "My company has not paid my last two months of salary after I left."],
    "example_labels": ["Deposit not returned", "Refund refused", "Salary unpaid"],
    "m_cat": "Category", "m_loc": "Location", "m_amt": "Amount",
})
T["hi"].update({
    "chips": ["वकील नहीं", "केवल सत्यापित स्रोत", "English + हिन्दी"],
    "steps": ["बताइए", "सवालों के जवाब", "मार्गदर्शन", "पत्र का मसौदा"],
    "cover": "आज यह किसमें मदद कर सकता है",
    "cards": [("किराया और जमा राशि", "जमा राशि वापस न मिलना, बिना कारण कटौती, एग्रीमेंट विवाद।"),
              ("उपभोक्ता रिफंड", "खराब सामान, ऑनलाइन रिफंड, सेवा शिकायतें।"),
              ("बकाया वेतन", "बकाया या देर से वेतन, कटौती, नौकरी छोड़ने के बाद का वेतन।")],
    "try": "या शुरू करने के लिए कोई उदाहरण चुनें:",
    "examples": ["मेरे मकान मालिक ने मेरी 20,000 रुपये की सिक्योरिटी डिपॉज़िट वापस नहीं की, जबकि मैंने फ्लैट खाली कर दिया है।",
                 "मैंने ऑनलाइन 5,000 रुपये के ईयरबड्स खरीदे। एक हफ्ते में खराब हो गए और विक्रेता रिफंड नहीं दे रहा।",
                 "नौकरी छोड़ने के बाद कंपनी ने मेरी पिछले दो महीने की सैलरी नहीं दी।"],
    "example_labels": ["जमा राशि नहीं मिली", "रिफंड से इनकार", "वेतन बकाया"],
    "m_cat": "श्रेणी", "m_loc": "स्थान", "m_amt": "राशि",
})

CSS = """
<style>
.stApp{background:#f2f5f3}
h1,h2,h3,h4{font-family:Georgia,'Iowan Old Style',Palatino,serif !important;color:#12231f;letter-spacing:-.01em}
footer,#MainMenu{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.6rem;max-width:860px}
.hero{background:#12231f;color:#fff;border-radius:12px;padding:22px 24px;margin-bottom:14px}
.hero h1{color:#fff !important;font-size:2.1rem;margin:0 0 4px 0}
.hero p{color:#c9d8d3;margin:0 0 12px 0;font-size:1.02rem}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{border:1px solid #3b5a52;color:#e4f2ee;border-radius:999px;padding:2px 12px;font-size:.82rem}
.stepper{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 12px 0}
.step{border:1px solid #cbd6d1;background:#fff;color:#4a5c56;border-radius:999px;padding:3px 13px;font-size:.84rem}
.step.done{background:#e4f2ee;color:#0a4f44;border-color:#9fd0c4}
.step.on{background:#0e6b5c;color:#fff;border-color:#0e6b5c;font-weight:600}
.card{background:#fff;border:1px solid #cbd6d1;border-left:5px solid #0e6b5c;border-radius:6px;padding:10px 14px;margin:8px 0}
.card.cat{border-left-color:#0e6b5c;min-height:96px}
.card.warn{border-left-color:#a8620a;background:#fbf1e2}
.card.seal{border-left-color:#a32a2a;background:#fbeaea}
.card h4{margin:0 0 4px 0;font-size:1.02rem}
.card p{margin:0;color:#4a5c56;font-size:.93rem}
.tag{display:inline-block;font-size:.74rem;border:1px solid #cbd6d1;background:#fff;border-radius:999px;padding:0 9px;margin:6px 6px 0 0;color:#4a5c56}
.tag.ok{background:#e4f2ee;border-color:#9fd0c4;color:#0a4f44}
.tag.mid{background:#fbf1e2;border-color:#e3c590;color:#7a4607}
.tag.bad{background:#fbeaea;border-color:#e1a5a5;color:#8a1f1f}
[data-testid="stChatMessage"]{background:#fff;border:1px solid #cbd6d1;border-radius:10px;padding:.5rem .9rem}
[data-testid="stSidebar"]{background:#e4ebe7}
.stButton>button{border-radius:8px;border:1.5px solid #0e6b5c;font-weight:600}
.disc{color:#4a5c56;font-size:.82rem;border-top:1px solid #cbd6d1;padding-top:10px;margin-top:18px}
</style>
"""

VERIF_CLASS = {"verified": "ok", "secondary_verified": "ok", "single_secondary": "mid", "general_principle": "mid", "pending_section": "bad"}


def esc(t):
    return html.escape(str(t))


def ss():
    s = st.session_state
    for k, v in (("case_id", None), ("chat", []), ("guidance", None), ("doc", None), ("extra", None),
                 ("error", None), ("count", 0), ("view", "chat"), ("lang", "auto"), ("pending", None)):
        if k not in s:
            s[k] = v
    return s


def ui_lang(s, case):
    if s.lang in ("en", "hi"):
        return s.lang
    return "hi" if case and case.get("language") == "hi" else "en"


def hero(x):
    chips = "".join(f'<span class="chip">{esc(c)}</span>' for c in x["chips"])
    st.markdown(f'<div class="hero"><h1>⚖️ {esc(x["title"])}</h1><p>{esc(x["sub"])}</p><div class="chips">{chips}</div></div>', unsafe_allow_html=True)


def stepper(s, x):
    stage = 3 if s.doc else 2 if s.guidance else 1 if s.case_id else 0
    out = []
    for i, label in enumerate(x["steps"]):
        cls = "on" if i == stage else "done" if i < stage else ""
        out.append(f'<span class="step {cls}">{i + 1}. {esc(label)}</span>')
    st.markdown('<div class="stepper">' + "".join(out) + "</div>", unsafe_allow_html=True)


def cite_card(r, x):
    sec = f", Section {esc(r['section'])}" if r.get("section") else f" <span style='color:#4a5c56'>({esc(x['no_sec'])})</span>"
    tagc = VERIF_CLASS.get(r["verification"], "")
    note = f"<p>{esc(r['jurisdiction_note'])}</p>" if r.get("jurisdiction_note") else ""
    st.markdown(
        f'<div class="card"><h4>{esc(r["act"])}{sec}</h4><p>{esc(r["title"])}</p>{note}'
        f'<span class="tag {tagc}">{esc(x["verif"].get(r["verification"], r["verification"]))}</span>'
        f'<span class="tag">{esc(x["checked"])} {esc(r["checked_on"])}</span>'
        f'<span class="tag"><a href="{esc(r["source_url"])}" target="_blank" rel="noopener noreferrer">{esc(x["src"])}</a></span></div>',
        unsafe_allow_html=True)


def bullets(items):
    for i in items or []:
        st.markdown(f"- {i}")


def items_block(items, x):
    for i in items or []:
        tags = f'<span class="tag">{esc(x["kinds"].get(i.get("kind"), i.get("kind", "")))}</span>'
        if i.get("supported") is False:
            tags += f'<span class="tag bad">{esc(x["unsup"])}</span>'
        if i.get("kb_ids"):
            tags += f'<span class="tag ok">{esc(", ".join(i["kb_ids"]))}</span>'
        st.markdown(f'<div class="card"><p style="color:#12231f">{esc(i["text"])}</p>{tags}</div>', unsafe_allow_html=True)


def alert_card(title, lines, kind="seal"):
    body = "".join(f"<li>{esc(l)}</li>" for l in lines)
    st.markdown(f'<div class="card {kind}"><h4>{esc(title)}</h4><ul style="margin:4px 0 0 18px;padding:0">{body}</ul></div>', unsafe_allow_html=True)


def start_example(text):
    st.session_state.pending = text


def process(s, text, force=False):
    if not config.LLM_API_KEY:
        s.error = "nokey"
        return
    if s.count >= MAX_MESSAGES_PER_SESSION:
        s.error = "limit"
        return
    s.count += 1
    s.error = None
    s.chat.append(("user", text, ""))
    try:
        r = pipeline.handle_message(s.case_id, text, s.lang, force)
    except llm.LLMError as e:
        s.error = f"The AI service could not complete this step. {e}"
        return
    except Exception as e:  # noqa: BLE001
        s.error = f"Something went wrong ({type(e).__name__}). Please try again."
        return
    s.case_id = r["case_id"]
    s.chat.append(("assistant", r["reply"], r["mode"]))
    s.extra = r.get("citations") if r["mode"] == "citation_check" else None
    if r.get("guidance"):
        s.guidance = r["guidance"]
        s.view = "guid"


def view_chat(s, x):
    if not s.chat:
        st.markdown(f"#### {x['cover']}")
        cols = st.columns(3)
        for col, (t, d) in zip(cols, x["cards"]):
            col.markdown(f'<div class="card cat"><h4>{esc(t)}</h4><p>{esc(d)}</p></div>', unsafe_allow_html=True)
        with st.chat_message("assistant"):
            st.markdown(x["welcome"])
        st.caption(x["try"])
        cols = st.columns(3)
        for n, (col, label) in enumerate(zip(cols, x["example_labels"])):
            col.button(label, key=f"ex{n}", on_click=start_example, args=(x["examples"][n],))
    for role, text, mode in s.chat:
        with st.chat_message(role):
            if mode in ("urgent", "emergency", "out_of_scope"):
                st.warning(text)
            else:
                st.markdown(text)


def view_case(c, x):
    if not c or not c.get("summary"):
        st.info(x["empty_case"])
        return
    st.subheader(c.get("title") or x["case"])
    st.write(c["summary"])
    amt = f"Rs {int(c['amount_inr']):,}" if isinstance(c.get("amount_inr"), (int, float)) else "-"
    m1, m2, m3 = st.columns(3)
    m1.metric(x["m_cat"], x["cats"].get(c["category"], c["category"]))
    m2.metric(x["m_loc"], (c.get("slots") or {}).get("location", "-"))
    m3.metric(x["m_amt"], amt)
    if c.get("escalation"):
        alert_card(x["adv"], [e["reason"] for e in c["escalation"]], "seal")
    if c.get("parties"):
        st.markdown(f"**{x['parties']}**")
        bullets([p.get("role", "") + (": " + p["name"] if p.get("name") else "") for p in c["parties"]])
    if c.get("timeline"):
        st.markdown(f"**{x['timeline']}**")
        bullets([f"**{e.get('date') or '?'}**: {e.get('event')}" for e in c["timeline"]])
    if c.get("facts_provided"):
        st.success(f"**{x['told']}**\n\n" + "\n".join(f"- {i}" for i in c["facts_provided"]))
    if c.get("evidence"):
        st.markdown(f"**{x['evidence']}**")
        bullets(c["evidence"])
    if c.get("missing_information"):
        alert_card(x["missing"], [m["question"] for m in c["missing_information"]], "warn")
    if c.get("ai_interpretations"):
        st.info(f"**{x['ai']}**\n\n" + "\n".join(f"- {i}" for i in c["ai_interpretations"]))


def view_guidance(s, x):
    g = s.guidance
    if not g:
        st.info(x["empty_guid"])
        for r in s.extra or []:
            cite_card(r, x)
        return
    if g.get("advocate_recommended"):
        reasons = list(g.get("advocate_reasons") or []) + [r["reason"] for r in g.get("advocate_reasons_system") or []]
        alert_card(x["adv"], reasons, "seal")
    else:
        st.write(x["adv_no"])
    st.markdown(f"#### {x['problem']}")
    st.write(g.get("problem", ""))
    st.markdown(f"#### {x['rights']}")
    items_block(g.get("rights"), x)
    st.markdown(f"#### {x['remedies']}")
    items_block(g.get("remedies"), x)
    st.markdown(f"#### {x['steps']}")
    bullets(g.get("next_steps"))
    st.markdown(f"#### {x['keep']}")
    bullets(g.get("evidence_to_preserve"))
    unc = (g.get("uncertainties") or []) + (g.get("missing_information") or [])
    alert_card(x["unc"], unc or ["-"], "warn")
    st.markdown(f"#### {x['refs']}")
    for r in g.get("citations") or []:
        cite_card(r, x)
    if g.get("removed_references"):
        st.error(x["removed"] + " " + "; ".join(g["removed_references"]))


def doc_html(d, body):
    return ("<!doctype html><meta charset='utf-8'><title>" + html.escape(d["title"]) + "</title>"
            "<style>body{font:14pt/1.5 'Noto Sans Devanagari','Nirmala UI',Georgia,serif;margin:2cm}"
            "pre{white-space:pre-wrap;font:inherit}.b{border:1.5px solid #a32a2a;padding:8px;margin-bottom:16px;font:11pt sans-serif}</style>"
            "<div class='b'>" + html.escape(d["banner"]) + "</div><pre>" + html.escape(body) + "</pre>")


def view_docs(s, c, x, lang):
    types = (c or {}).get("documents_available") or []
    if not types:
        st.info(x["doc_empty"])
        return
    st.markdown(f"#### {x['doc_head']}")
    dtype = st.selectbox(x["doc_type"], types, format_func=lambda k: x["docs_names"].get(k, k), key="doc_type_sel")
    dlang = st.selectbox(x["doc_lang"], ["en", "hi"], index=0 if lang == "en" else 1,
                         format_func=lambda k: "English" if k == "en" else "हिन्दी", key="doc_lang_sel")
    if st.button(x["gen"], type="primary", key="gen_btn"):
        with st.spinner(x["thinking"]):
            try:
                d = pipeline.generate_document(s.case_id, dtype, dlang)
                s.doc = d
                s["doc_body"] = d["body"]
                s.error = None
            except (llm.LLMError, ValueError) as e:
                s.error = str(e)
    d = s.doc
    if not d:
        return
    alert_card("AI draft", [d["banner"]], "seal")
    st.markdown(f"**{d['title']}**")
    body = st.text_area(x["edit"], key="doc_body", height=420)
    c1, c2 = st.columns(2)
    c1.download_button(x["dl_txt"], d["banner"] + "\n\n" + body, file_name=f"{d['doc_type']}.txt", mime="text/plain")
    c2.download_button(x["dl_html"], doc_html(d, body), file_name=f"{d['doc_type']}.html", mime="text/html")
    if d["placeholders"]:
        alert_card(x["ph2"], d["placeholders"], "warn")
    if d["notes_for_user"]:
        st.markdown(f"**{x['notes']}**")
        bullets(d["notes_for_user"])
    for r in d["citations"]:
        cite_card(r, x)
    if d["removed_references"]:
        st.error(x["removed"] + " " + "; ".join(d["removed_references"]))


def main():
    st.set_page_config(page_title="Nyaya Sahayak", page_icon="⚖️", layout="centered", initial_sidebar_state="collapsed")
    st.markdown(CSS, unsafe_allow_html=True)
    _init()
    s = ss()
    case = db.get_case(s.case_id) if s.case_id else None
    x = T[ui_lang(s, case)]

    with st.sidebar:
        st.selectbox(x["lang"], ["auto", "en", "hi"], key="lang", format_func={"auto": "Auto / स्वतः", "en": "English", "hi": "हिन्दी"}.get)
        force = st.button(x["force"], key="force_btn", disabled=not s.case_id)
        if st.button(x["delete"], key="del_btn") and s.case_id:
            db.delete_case(s.case_id)
            s.case_id, s.chat, s.guidance, s.doc, s.extra, s.error, s.view = None, [], None, None, None, None, "chat"
            s.pop("doc_body", None)
            st.rerun()
        st.caption(texts.PRIVACY[ui_lang(s, case)])

    # chat_input is pinned to the bottom of the page; handle submissions before drawing the views
    prompt = st.chat_input(x["ph"]) or s.pending
    s.pending = None
    if force and s.case_id:
        process(s, "कृपया अभी तक की जानकारी के आधार पर मार्गदर्शन दें।" if ui_lang(s, case) == "hi"
                else "Please give guidance with what I have shared so far.", force=True)
    elif prompt:
        process(s, prompt)
        if s.view != "guid":
            s.view = "chat"
    case = db.get_case(s.case_id) if s.case_id else None
    x = T[ui_lang(s, case)]

    hero(x)
    stepper(s, x)
    st.radio("view", ["chat", "case", "guid", "docs"], key="view", horizontal=True,
             format_func=lambda k: x[k], label_visibility="collapsed")
    if s.error:
        st.error(x.get(s.error, s.error))
    cv = pipeline.view(case) if case else None
    if s.view == "chat":
        view_chat(s, x)
    elif s.view == "case":
        view_case(cv, x)
    elif s.view == "guid":
        view_guidance(s, x)
    else:
        view_docs(s, cv, x, ui_lang(s, case))
    st.markdown(f'<div class="disc">{esc(texts.DISCLAIMER[ui_lang(s, case)])}</div>', unsafe_allow_html=True)


main()
