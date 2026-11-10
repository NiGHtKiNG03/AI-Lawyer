"""Lists model names your key can use.  Run from the project folder:  python tools/list_models.py"""
import json, urllib.request
from pathlib import Path
env = dict(l.strip().split("=", 1) for l in (Path(__file__).resolve().parent.parent / ".env").read_text().splitlines()
           if "=" in l and not l.startswith("#"))
key, provider = env.get("LLM_API_KEY", ""), env.get("LLM_PROVIDER", "gemini")
if provider == "gemini":
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=100", headers={"x-goog-api-key": key})
    for m in json.load(urllib.request.urlopen(req))["models"]:
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(m["name"].replace("models/", ""))
else:
    base = (env.get("LLM_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    req = urllib.request.Request(base + "/models", headers={"Authorization": "Bearer " + key})
    for m in json.load(urllib.request.urlopen(req))["data"]:
        print(m["id"])
