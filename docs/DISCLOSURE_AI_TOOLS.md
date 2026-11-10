# AI Tool Disclosure

## Tools I used
- **Claude** (chat, with web search and a code sandbox). It designed the architecture, wrote the code, the first draft of the knowledge base, the prompts, the UI, the unit tests and the document drafts, and searched the web to check which laws are currently in force.
- **A free LLM API** (set through `LLM_PROVIDER` / `LLM_MODEL` in `.env`) powers the running app. For the test outputs I used: **[provider and exact model name]**.
- **VS Code** for editing and running everything locally.

## How AI contributed, and what I did myself
Claude did most of the typing: the Python backend, the safety and citation-checking code, the English/Hindi interface text, and the test runner. My part was choosing Problem 2 and its scope, setting the app up on my machine, debugging the connection to the model provider, running the scenarios, **[reading and scoring the raw outputs, and checking the knowledge-base links against the official sites: keep these only if you really did them]**, and writing up the results.

## Where the AI tools got it wrong (all of these actually happened)

**1. A hard-coded model name that no longer worked (the one I'd highlight).**
The code defaulted to a Gemini model name (`gemini-2.5-flash`) that Claude picked from memory. When I ran the app, every message failed with "HTTP 404". The first version of the error handler also hid the provider's explanation, so the failure was a mystery. After the handler was changed to show Google's own message, it said the model was "no longer available to new users" and named a newer one. I set `LLM_MODEL` in `.env` and the default was updated. The fix I'd make permanent: never trust a remembered model name, make it a setting, and include helper scripts (`tools/test_llm.py`, `tools/list_models.py`) so anyone can check their own key and model in one command.

**2. Missing-information logic treated a real answer as "missing".**
Claude's list of "empty" values included the string "none". A tenant who says the landlord gave no explanation produces exactly that value, so the app would keep asking questions forever. A plumbing check with a stand-in model got stuck asking instead of giving guidance; removing "none" from the list fixed it.

**3. The citation scrubber left broken sentences.**
The first version of the case-law patterns matched pieces of a citation like "(2015) 4 SCC 123" separately, leaving "[removed] (2015) 4 [removed]". I only noticed by reading the output, not just checking the fake citation was gone. Fixed by ordering the patterns most-specific first.

**4. A small environment slip.**
Claude used a shell shortcut that this sandbox's shell does not support, creating a folder literally named `{lawyer,kb,static,...}`. It surfaced when the next file writes failed, and was fixed.

## What I did not let the AI decide
Whether the app may give an answer or must send the person to an advocate (that is plain code, not the model), what counts as a verified legal source, and the claims I make in the solution document.

*(Add any error you see from the LLM itself while reading raw_outputs/, quoted exactly as it appeared, e.g. a wrong section or an outdated Act. That is the most valuable item here.)*
