"""Replaceable LLM layer. Add a provider by adding one function and one entry in PROVIDERS.
Errors never include request/response bodies, so user text does not leak into logs."""
import json
import re
import time
import urllib.error
import urllib.request

from . import config


class LLMError(Exception):
    pass


DEFAULT_MODELS = {
    "gemini": "gemini-3.8-flash",
    "openai_compat": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-5",
}


def _post(url, headers, payload):
    """POST with patient retries: free tiers often answer 429 (rate limit) or 503 (busy)."""
    data = json.dumps(payload).encode("utf-8")
    last = None
    for attempt in range(5):
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json", **headers}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = ""
            if e.code in (400, 401, 403, 404):  # provider's own explanation (never includes our request)
                detail = " - " + e.read().decode("utf-8", "ignore")[:300]
            last = LLMError(f"LLM provider returned HTTP {e.code}{detail}")
            if e.code not in (429, 500, 502, 503, 504):
                raise last from None
        except Exception as e:  # noqa: BLE001
            last = LLMError(f"LLM request failed ({type(e).__name__})")
        time.sleep(min(60, 5 * 2 ** attempt))
    raise last from None


def _gemini(system, messages, json_mode, model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    contents = [{"role": "user" if m["role"] == "user" else "model",
                 "parts": [{"text": m["content"]}]} for m in messages]
    gen = {"temperature": 0.2}
    if json_mode:
        gen["responseMimeType"] = "application/json"
    out = _post(url, {"x-goog-api-key": config.LLM_API_KEY},
                {"systemInstruction": {"parts": [{"text": system}]}, "contents": contents, "generationConfig": gen})
    try:
        return "".join(p.get("text", "") for p in out["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        raise LLMError("Gemini returned no text (possibly blocked or empty)") from None


def _openai_compat(system, messages, json_mode, model):
    base = (config.LLM_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    payload = {"model": model, "temperature": 0.2,
               "messages": [{"role": "system", "content": system}] + messages}
    if json_mode and config.LLM_JSON_MODE:
        payload["response_format"] = {"type": "json_object"}
    out = _post(f"{base}/chat/completions", {"Authorization": f"Bearer {config.LLM_API_KEY}"}, payload)
    try:
        return out["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise LLMError("Provider returned no text") from None


def _anthropic(system, messages, json_mode, model):
    out = _post("https://api.anthropic.com/v1/messages",
                {"x-api-key": config.LLM_API_KEY, "anthropic-version": "2023-06-01"},
                {"model": model, "max_tokens": 4000, "temperature": 0.2, "system": system, "messages": messages})
    try:
        return "".join(b.get("text", "") for b in out["content"])
    except (KeyError, TypeError):
        raise LLMError("Anthropic returned no text") from None


PROVIDERS = {"gemini": _gemini, "openai_compat": _openai_compat, "anthropic": _anthropic}


def complete(system, messages, json_mode=False):
    if not config.LLM_API_KEY:
        raise LLMError("LLM_API_KEY is not set. Copy .env.example to .env and add a key.")
    fn = PROVIDERS.get(config.LLM_PROVIDER)
    if not fn:
        raise LLMError(f"Unknown LLM_PROVIDER '{config.LLM_PROVIDER}'")
    model = config.LLM_MODEL or DEFAULT_MODELS[config.LLM_PROVIDER]
    return fn(system, messages, json_mode, model)


def parse_json(text):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.I)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", t, re.S)
        if m:
            return json.loads(m.group(0))
        raise


def complete_json(system, messages):
    """Returns (parsed_dict, raw_text). Retries once on invalid JSON."""
    raw = complete(system, messages, json_mode=True)
    try:
        return parse_json(raw), raw
    except json.JSONDecodeError:
        retry = messages + [{"role": "assistant", "content": raw},
                            {"role": "user", "content": "That was not valid JSON. Return ONLY the JSON object."}]
        raw2 = complete(system, retry, json_mode=True)
        try:
            return parse_json(raw2), raw2
        except json.JSONDecodeError:
            raise LLMError("Model did not return valid JSON twice") from None
