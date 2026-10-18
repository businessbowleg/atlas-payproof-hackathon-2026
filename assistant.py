"""Optional local AI interpretation. Off unless PAYPROOF_LOCAL_MODEL is set."""
import json
import os
import urllib.error
import urllib.request

class AIUnavailable(RuntimeError):
    pass

def enabled():
    return bool(os.getenv("PAYPROOF_LOCAL_MODEL", "").strip())

def explain(report):
    model = os.getenv("PAYPROOF_LOCAL_MODEL", "").strip()
    if not model:
        raise AIUnavailable("Local AI is not enabled; deterministic validation remains available.")
    # Only aggregate facts, never full CSV content, enter the prompt.
    fact = {
        "rows": report["rows"], "held": report["held"], "accepted": report["accepted"],
        "reasons": sorted({reason for row in report["issues"] for reason in row["issues"]}),
    }
    prompt = ("You are a supplier data QA assistant. In 90 words or fewer, explain these "
              "verified counts, what the operator should fix, and what remains unverified. "
              "Do not imply payment or full catalog compliance. No invented findings. "
              + json.dumps(fact, sort_keys=True))
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps({"model": model, "prompt": prompt, "stream": False,
                         "keep_alive": "0s",
                         "options": {"temperature": 0, "num_predict": 170,
                                     "num_gpu": 0, "num_thread": 2}}).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as result:
            body = json.loads(result.read(65536))
    except (OSError, ValueError) as exc:
        raise AIUnavailable("Local model did not produce a response.") from exc
    value = str(body.get("response") or "").strip()
    if not value:
        raise AIUnavailable("Local model returned an empty response.")
    return {"guidance": value[:1800], "source": "LOCAL_OLLAMA",
            "disclaimer": "Model commentary; verify against the deterministic row report."}
