# Nyaya Sahayak: an AI legal assistant for everyday problems in India

Problem 2 of the Kuku AI Generalist assignment. A person describes a **rent deposit**, **consumer refund** or **unpaid salary**
problem (English or Hindi, text or voice) and gets: a structured case file, verified legal references, plain-language options,
an advocate-escalation warning when needed, and an editable draft letter (download as .txt or save as PDF).

It is general legal information, not a lawyer. It is designed to say "I could not verify that" instead of guessing.

## Run it (needs only Python 3.9+; no pip install, no npm)

```bash
git clone <this repo> && cd ai-lawyer
cp .env.example .env          # then edit .env: set LLM_PROVIDER and LLM_API_KEY
python3 server.py             # open http://localhost:8000
```

Free keys: Google AI Studio (Gemini free tier) works with `LLM_PROVIDER=gemini`. Any OpenAI-compatible host (Groq, OpenRouter, etc.)
works with `LLM_PROVIDER=openai_compat` plus `LLM_BASE_URL`. `LLM_PROVIDER=anthropic` is also supported. To swap the model, change
two lines in `.env`. To add a provider, add one function to `lawyer/llm.py`.

## If the AI step fails

- `python tools/test_llm.py` checks your key and model in one call. `python tools/list_models.py` lists the model names your key can use (model names get retired; set `LLM_MODEL` in `.env`).
- HTTP 404 = wrong or retired model name. 401/403 = bad key. 429 = free rate limit (the app retries with waits). 503 = provider busy (also retried). Timeout = slow or blocked network.

## Tests

```bash
python3 -m unittest tests.test_deterministic -v   # offline, no key: tests the code safeguards only (citation scrubber, safety rules, KB integrity)
python3 tests/run_scenarios.py                    # needs a key: runs the 6 required scenarios + a Hindi bonus; saves UNEDITED outputs to raw_outputs/
python3 tests/run_scenarios.py T4 T5              # run a subset
```

The scenario runner prints automated checks, but those are crude heuristics. Read `raw_outputs/*.md` and score them with
`docs/EVALUATION_TEMPLATE.md`. A professional-sounding answer is not a pass.

## How it works (per message)

1. **Redact** card/Aadhaar-like numbers and OTP/password text before anything is stored or sent to the model.
2. **Safety scan in code** (regex, English + Hindi): court notice/summons, criminal/police, ongoing case, family/property matters, emergencies. These fire regardless of what the model says.
3. **LLM step 1, extract**: classify the problem (tenant / consumer / employment / out_of_scope / unclear) and fill fact "slots" using only what the user said.
4. **Code: missing-information detection**: required slots per category live in `lawyer/prompts.py`. If any are empty, the next reply asks at most 3 questions and gives no legal conclusion (after 3 rounds, or on "Get guidance now", it proceeds and lists the gaps as uncertainties).
5. **Code: retrieval** from `kb/knowledge_base.json` by category (not model-driven).
6. **LLM step 2, guidance or document**: the model sees only KB entries and must reference them by id.
7. **Code: citation validation**: unknown ids dropped; citations shown to the user are rebuilt from the KB (act, section, official link, check date, verification level); any section number or case citation left in free text that is not backed by a verified entry is removed and reported. If the user cites "Section X of Y", code checks it against the KB and says so when it cannot be verified.
8. **Code: escalation**: advocate warning is added for court notices, criminal matters, ongoing cases, substantial amounts, unsupported categories, or no verified source.

Pages: landing, consultation (chat + language + voice), Case file tab (facts you stated vs missing vs AI readings, timeline, parties, evidence), Guidance tab, Documents tab.

## Hallucination prevention, honestly

- The model cannot introduce a citation: it can only name KB ids, and code renders them.
- Section numbers are shown only for entries marked with a checked `section`. Entries with unchecked sections (`pending_section`) have the number withheld from the model entirely.
- The KB is small on purpose (18 entries). Each carries a `verification` level, visible in the UI. **Only Consumer Protection Act s.69 was read as bare-act text, and that was on a third-party site, not India Code. Everything else rests on secondary sources (law-firm and legal-news pages) or on general principles. The official India Code pages still need to be opened and confirmed, and an advocate should review the KB before real-world use.**
- The system never cites court judgments. There are none in the KB.
- Important currency trap: the Payment of Wages Act, 1936 was repealed on 21 Nov 2025 and replaced by the Code on Wages, 2019. The KB reflects this; a model relying on older training data would not.

## Known limitations

- Covers only three problem types. Everything else gets a clear "outside scope, see an advocate" message.
- Tenant law is state-specific and the KB holds no state rent acts; guidance there is deliberately generic and tells the user to check their state.
- The validator catches fabricated section numbers and case citations by pattern. It cannot catch a wrong claim written in ordinary words, or a correct section number attached to the wrong act when both appear nearby. Human review is still required.
- Safety regexes can miss unusual phrasings and over-trigger on some words (e.g. "police"); they err toward escalation.
- Hindi quality depends on the chosen model and has not been reviewed by a native-speaking lawyer. KB text shown in citations is English.
- "Save as PDF" uses the browser's print dialog (works with Hindi); there is no server-side PDF engine.
- Voice input uses the browser's speech recognition (Chrome/Edge/Safari); the text path always works.
- No user accounts: a case is identified by a random id kept in the browser session. Not suitable for multi-user production as is. SQLite instead of Postgres; Python stdlib server instead of Next.js (chosen so it runs anywhere with zero installs; the master brief allowed this).
- Rate limiting is per-IP, in memory.
- Not deployed. Free hosts that run Python (Render, Railway, Hugging Face Spaces with a Docker/Python app) can run `python3 server.py` with env vars set.

## Scale and cost thinking

Two model calls per message (extract + reply/guidance); documents add one. Retrieval is free (in-process). Extraction and drafting can use a cheap fast model; a stronger model can be plugged in for guidance only. The larger risk at scale is KB maintenance: laws change (see the wage-law repeal), so each entry has a `checked_on` date and the next step is a scheduled re-verification job plus advocate sign-off per category/state.

## Layout

```
server.py            HTTP server + API         lawyer/pipeline.py   orchestration
lawyer/llm.py        swappable providers       lawyer/safety.py     escalation + redaction rules
lawyer/validate.py   citation validation       lawyer/kb.py         retrieval
lawyer/prompts.py    prompts + required slots  lawyer/texts.py      fixed EN/HI safety text
kb/knowledge_base.json                         static/index.html    UI
tests/               unit tests + scenario runner   docs/            disclosure, solution doc draft, eval template
```
