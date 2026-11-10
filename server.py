"""Zero-dependency web server (Python standard library only).  Run:  python3 server.py"""
import json
import mimetypes
import time
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from lawyer import config, db, llm, pipeline, prompts, texts

STATIC = Path(__file__).parent / "static"
MAX_BODY = 20_000
_hits = defaultdict(deque)


def rate_limited(ip):
    now, q = time.time(), _hits[ip]
    while q and now - q[0] > 300:
        q.popleft()
    if len(q) >= config.RATE_LIMIT_PER_5MIN:
        return True
    q.append(now)
    return False


class Handler(BaseHTTPRequestHandler):
    server_version = "AILawyer/1.0"

    def log_message(self, fmt, *args):  # never log request bodies or query strings (privacy)
        print(f"{self.command} {urlparse(self.path).path} -> {args[1] if len(args) > 1 else ''}")

    # -- helpers
    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > MAX_BODY:
            raise ValueError("Request too large")
        return json.loads(self.rfile.read(n) or b"{}")

    # -- routes
    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/config":
            return self._json(200, {"llm_configured": bool(config.LLM_API_KEY), "provider": config.LLM_PROVIDER,
                                    "disclaimer": texts.DISCLAIMER, "privacy": texts.PRIVACY,
                                    "doc_types": prompts.DOC_TYPES, "max_input_chars": config.MAX_INPUT_CHARS})
        if u.path == "/api/case":
            case = db.get_case(parse_qs(u.query).get("id", [""])[0])
            return self._json(200, pipeline.view(case)) if case else self._json(404, {"error": "Case not found"})
        rel = "index.html" if u.path in ("/", "") else u.path.lstrip("/").removeprefix("static/")
        f = (STATIC / rel).resolve()
        if STATIC.resolve() not in f.parents and f != STATIC.resolve() or not f.is_file():
            return self._json(404, {"error": "Not found"})
        data = f.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", (mimetypes.guess_type(f.name)[0] or "application/octet-stream") + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_DELETE(self):
        u = urlparse(self.path)
        if u.path == "/api/case":
            db.delete_case(parse_qs(u.query).get("id", [""])[0])
            return self._json(200, {"deleted": True})
        self._json(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path not in ("/api/chat", "/api/document"):
            return self._json(404, {"error": "Not found"})
        if rate_limited(self.client_address[0]):
            return self._json(429, {"error": "Too many requests. Please wait a few minutes and try again."})
        try:
            b = self._body()
            if path == "/api/chat":
                msg = str(b.get("message", "")).strip()
                if not msg:
                    return self._json(400, {"error": "Please type a message."})
                lang = b.get("language") if b.get("language") in ("auto", "en", "hi") else "auto"
                return self._json(200, pipeline.handle_message(b.get("case_id"), msg, lang, bool(b.get("force_guidance"))))
            return self._json(200, pipeline.generate_document(b.get("case_id"), b.get("doc_type"), b.get("language")))
        except ValueError as e:
            self._json(400, {"error": str(e)})
        except llm.LLMError as e:
            self._json(502, {"error": f"The AI service could not complete this step. {e}"})
        except Exception as e:  # noqa: BLE001  (message only; no user text)
            print("ERROR", type(e).__name__)
            self._json(500, {"error": "Something went wrong on the server. Please try again."})


if __name__ == "__main__":
    db.init()
    if not config.LLM_API_KEY:
        print("WARNING: LLM_API_KEY is not set. Copy .env.example to .env and add a key.")
    print(f"AI Lawyer running at http://localhost:{config.PORT}  (provider: {config.LLM_PROVIDER})")
    ThreadingHTTPServer(("0.0.0.0", config.PORT), Handler).serve_forever()
