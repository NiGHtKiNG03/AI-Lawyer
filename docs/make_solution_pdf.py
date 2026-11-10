"""Builds the 2-page solution PDF. Fill docs/results.json first, then:  pip install reportlab  &&  python docs/make_solution_pdf.py
Anything not filled in is printed as PENDING in red, so an unfinished PDF cannot be mistaken for a finished one."""
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = Path(__file__).resolve().parent
R = json.loads((HERE / "results.json").read_text(encoding="utf-8"))
INK, ACC, RED = colors.HexColor("#12231f"), colors.HexColor("#0e6b5c"), colors.HexColor("#a32a2a")

body = ParagraphStyle("b", fontName="Helvetica", fontSize=8.7, leading=11.2, textColor=INK, spaceAfter=3)
h = ParagraphStyle("h", parent=body, fontName="Helvetica-Bold", fontSize=10.2, leading=12.5, textColor=ACC, spaceBefore=6, spaceAfter=2)
title = ParagraphStyle("t", parent=body, fontName="Helvetica-Bold", fontSize=15, leading=18, spaceAfter=1)
small = ParagraphStyle("s", parent=body, fontSize=7.8, leading=9.6, textColor=colors.HexColor("#4a5c56"))
cell = ParagraphStyle("c", parent=body, fontSize=8, leading=9.8, spaceAfter=0)
bul = ParagraphStyle("bul", parent=body, leftIndent=9, bulletIndent=0, spaceAfter=1.5)


def pend(v):
    if v in (None, "") or str(v).startswith("["):
        return f'<font color="#a32a2a"><b>PENDING</b> {"" if v in (None, "") else v}</font>'
    return v


def P(t, st=body):
    return Paragraph(t, st)


def B(t):
    return Paragraph(t, bul, bulletText="\u2022")


s = []
s += [P("Nyaya Sahayak: an AI legal helper for everyday problems in India", title),
      P(f"Kuku AI Generalist Assignment, Problem 2 &nbsp;|&nbsp; {pend(R['name'])}, {pend(R['roll_no'])}, {pend(R['branch'])} &nbsp;|&nbsp; Prototype: {pend(R['repo_link'])}", small)]

s += [P("1. Why I picked this problem", h),
      P("People rarely get legal help for small disputes: a deposit the landlord keeps, a refund that never arrives, salary that stops. "
        "A lawyer feels too costly for a Rs 5,000 problem, and the paperwork is scary, so people give up. I also picked it because it tests "
        "honesty under pressure: language models confidently invent laws, and a legal tool that does that is worse than no tool. "
        "My users are ordinary people in India on a phone or laptop, comfortable in English or Hindi, with a dispute of roughly Rs 5,000 to a few lakh and no lawyer.")]

s += [P("2. Scope and assumptions", h),
      B("<b>Three problem types only:</b> rent deposits, consumer refunds/complaints, unpaid or delayed salary. Anything else (criminal, family, property title) gets a plain \"outside scope, see an advocate\" message."),
      B("<b>Tenant law is state-specific</b> and I did not load any state rent acts, so deposit guidance is deliberately general and tells the user to check their state."),
      B("<b>Law as of November 2026.</b> For example the Payment of Wages Act, 1936 was repealed on 21 Nov 2025 and replaced by the Code on Wages, 2019; the knowledge base reflects that."),
      B("<b>\"Substantial amount\" = Rs 2 lakh</b> (a setting) triggers an advocate warning. No user accounts; a case lives in a random id, kept 30 days and deletable. PDF export uses the browser's print dialog.")]

s += [P("3. How it works", h),
      P("Each message goes through these steps. The model does language work; ordinary code makes the decisions that must be reliable. "
        "<b>(1)</b> Redact card/Aadhaar-like numbers and OTPs. <b>(2)</b> Code scans for danger signs in English and Hindi: court notice or summons, police/criminal, "
        "ongoing case, family/property, safety emergencies. <b>(3)</b> The model extracts facts into fixed slots (location, dates, amount, proof) using only what the user said. "
        "<b>(4)</b> Code finds missing slots and asks at most three questions, with no legal conclusion yet (it moves on after three rounds or when the user taps \"Get guidance now\"). "
        "<b>(5)</b> Code retrieves matching entries from a small curated knowledge base. <b>(6)</b> The model writes guidance or a draft letter, allowed to cite knowledge-base ids only. "
        "<b>(7)</b> Code validates citations and adds the advocate warning. Output is a case file (facts told vs missing vs AI's readings), guidance with sources, and an editable letter (.txt or PDF), "
        "in English or Hindi, with voice input where the browser supports it.")]

s += [P("4. Technology and what AI vs code vs a human does", h),
      P("Python standard library server, SQLite, plain HTML/JS: zero installs, easy for anyone to run. The model sits behind a three-provider adapter (Gemini, any OpenAI-compatible API, Anthropic), "
        "so swapping models is two lines in <font face='Courier'>.env</font>. <b>AI:</b> understanding messy stories, plain-language explanation, drafting, Hindi. "
        "<b>Code:</b> slot logic, retrieval, citation checks, safety rules, escalation, redaction. <b>Human:</b> an advocate must review the knowledge base and every draft before it is sent or filed; the app says so on every draft.")]

s += [P("5. Legal accuracy and hallucination prevention", h),
      B("The model cannot introduce a citation. It may only name knowledge-base ids; the act, section, official link and check date shown to the user are built by code from the knowledge base."),
      B("A section number is shown only when that entry's section was actually checked. Unchecked ones are withheld from the model entirely. The system never cites court judgments."),
      B("Any leftover section number or case citation in the model's text that no verified entry backs is stripped and reported to the user. If the user quotes a section, code checks it and says \"I could not verify that\" instead of describing it."),
      B("<b>Honest status:</b> the knowledge base has 18 entries, each labelled verified / secondary-verified / provisional / general principle. Only Consumer Protection Act s.69 was read as bare-act text, and on a third-party site, not India Code. "
        "The rest rest on law-firm and legal-news sources or general principles. The official links must still be opened and an advocate must review the entries before real use.")]

s += [P("6. Testing and results", h),
      P(f"<b>Method.</b> Seven realistic scenarios run through the real pipeline and a real model (<b>{pend(R['model_used'])}</b>, run {pend(R['run_date'])}): the six required cases plus a Hindi one. "
        "Raw outputs are saved unedited in <font face='Courier'>raw_outputs/</font>. Automated checks are only a first filter; I read each output and scored it on eight points (legal accuracy, citation reliability, "
        "follow-up questions, document quality, language, hallucination prevention, user experience, correct escalation), checking each cited provision against its official link."),
      ]
rows = [[P("<b>Scenario</b>", cell), P("<b>What I checked</b>", cell), P("<b>What actually happened</b>", cell)]]
expect = {
    "T1 Rental deposit": "Asks city/state, agreement, dates; guidance; demand notice with placeholders",
    "T2 Online refund": "Asks purchase date, seller, proof; consumer forums; refund request draft",
    "T3 Unpaid salary": "Asks employment type, dates, salary terms; cites Code on Wages, not repealed Act; demand letter",
    "T4 Vague complaint": "Only questions, no legal conclusion",
    "T5 Invented section": "Says it cannot verify; does not invent what the section says",
    "T6 Court notice": "Flags urgency, advises advocate, invents no deadline",
    "T7 Hindi deposit (bonus)": "Hindi replies and letter keep dates, amounts and names exact",
}
for k, v in R["scenarios"].items():
    rows.append([P(k, cell), P(expect.get(k, ""), cell), P(pend(v), cell)])
tb = Table(rows, colWidths=[3.1 * cm, 6.3 * cm, 8.4 * cm], repeatRows=1)
tb.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd6d1")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4f2ee")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
s += [tb, Spacer(1, 3),
      P("<b>Checks already done on the code itself:</b> 16 offline unit tests of the safeguards (citation scrubber, safety rules, redaction, knowledge-base integrity) pass. "
        "A plumbing run with a stand-in model caught two of my own bugs before any real run: a real answer of \"none\" was treated as missing information, and the scrubber left sentence fragments around removed citations. "
        "Both are fixed. These tests show the code works; they say nothing about the model's answer quality, which is what the table above is for."),
      P(f"<b>Biggest failure I saw:</b> {pend(R['biggest_failure_seen'])}")]

s += [P("7. Limitations and failure cases", h),
      B("The validator catches invented section numbers and case citations by pattern. It cannot catch a wrong claim written in ordinary words, or a right number attached to the wrong act when both appear close together."),
      B("Safety rules are keyword-based and can miss unusual wording or over-trigger (they lean towards sending people to an advocate). The model can still misclassify a case."),
      B("Hindi quality depends on the model and has not been checked by a Hindi-speaking lawyer; citation text is English. No state rent law, so tenant advice stays general."),
      B("It relies on free model tiers. During setup I hit a retired default model name (HTTP 404), busy servers (503) and rate limits (429); the app now retries with waits, and the model is set in <font face='Courier'>.env</font>. Not deployed yet; single-browser sessions only.")]

s += [P("8. Scaling", h),
      P("A case costs about two model calls per message plus one per drafted document, and retrieval is free, so a cheaper fast model can do extraction while a stronger one writes guidance. "
        "The real cost of scale is keeping the law correct: laws change (the wage-law repeal is an example), so each entry has a check date and the next step is a scheduled re-verification plus advocate sign-off. "
        "Adding a category is a new slot list, a few knowledge-base entries and test cases; adding a state means advocate-reviewed state rent-law entries. Next steps: retrieval over official PDFs with passage-level citations, "
        "an evaluation set of 100+ real cases, proper accounts and encrypted storage.")]


def foot(c, d):
    c.saveState(); c.setFont("Helvetica", 7); c.setFillColor(colors.HexColor("#4a5c56"))
    c.drawString(1.5 * cm, 0.8 * cm, "General legal information, not a substitute for a qualified advocate in India."); c.drawRightString(A4[0] - 1.5 * cm, 0.8 * cm, f"Page {d.page}"); c.restoreState()


out = HERE / "Solution_Document.pdf"
doc = SimpleDocTemplate(str(out), pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm, topMargin=1.3 * cm, bottomMargin=1.4 * cm, title="Solution Document: Nyaya Sahayak")
doc.build(s, onFirstPage=foot, onLaterPages=foot)
from pypdf import PdfReader  # noqa: E402
n = len(PdfReader(str(out)).pages)
print(f"Wrote {out} ({n} pages)" + ("" if n <= 2 else "  <-- TOO LONG: shorten your results sentences"))
sys.exit(0 if n <= 2 else 1)
