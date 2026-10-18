"""Loopback-only preview server; no live payments, no persistent customer data."""
import json
import os
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from core import DataError, PRICE, inspect_csv, summary
from assistant import AIUnavailable, enabled as ai_enabled, explain as ai_explain
from paypal_sandbox import PaymentError, SandboxPayPal, valid_capture

ROOT = Path(__file__).resolve().parent
SANDBOX = os.getenv("PAYPAL_SANDBOX_CLIENT_ID") and os.getenv("PAYPAL_SANDBOX_SECRET")
# Intentionally process-local state. Restart drops sessions and orders.
sessions = {}
lock = threading.Lock()

def mode():
    return "PAYPAL_SANDBOX" if SANDBOX else "DEMO_NO_PAYMENT"

def explain_ticket(ticket):
    with lock:
        item = sessions.get(ticket)
        if not item:
            raise DataError("Unknown ticket.")
        report = item["report"]
    return ai_explain(report)

def begin_report(text):
    result = inspect_csv(text)
    ticket = secrets.token_urlsafe(18)
    with lock:
        sessions[ticket] = {"report": result, "state": "INSPECTED", "order_id": None}
    return {"ticket": ticket, "summary": summary(result), "report": result, "mode": mode()}

def create_checkout(ticket):
    with lock:
        item = sessions.get(ticket)
        if not item or item["state"] not in ("INSPECTED", "ORDER_CREATED"):
            raise DataError("Unknown or ineligible ticket.")
        if item["state"] == "ORDER_CREATED":
            return item["checkout"]
    if not SANDBOX:
        # This is explicitly NOT a financial transaction.
        order = {"id": "DEMO-" + secrets.token_hex(6), "approve_url": None,
                 "status": "SIMULATED", "notice": "NO PAYMENT WAS MADE"}
    else:
        order = SandboxPayPal().create_order(PRICE, ticket.replace("-", "_"))
    with lock:
        item = sessions.get(ticket)
        if not item or item["state"] != "INSPECTED":
            raise DataError("Ticket state changed; retry.")
        item["checkout"] = order
        item["order_id"] = order["id"]
        item["state"] = "ORDER_CREATED"
    return order

def capture_checkout(ticket, order_id):
    with lock:
        item = sessions.get(ticket)
        if not item or item["state"] != "ORDER_CREATED" or item["order_id"] != order_id:
            raise DataError("Order is not linked to ticket.")
        if not SANDBOX:
            return {"status": "DEMO_ONLY", "paid": False, "notice": "No funds transferred."}
        # Never call a live payment endpoint, even if environment variables change.
        data = SandboxPayPal().capture_order(order_id, ticket[:36])
        if data.get("id") != order_id or not valid_capture(data, PRICE):
            raise PaymentError("Sandbox capture not confirmed at quoted amount.")
        item["state"] = "SANDBOX_CAPTURED"
    return {"status": "SANDBOX_CAPTURED", "paid": False,
            "notice": "Sandbox test credits only; no real funds."}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Avoid logging raw CSV, session tokens, or private uploads.
        return

    def respond(self, data, status=200):
        raw = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline' 'self'")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if urlsplit(self.path).path == "/":
            raw = (ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
        elif urlsplit(self.path).path == "/health":
            self.respond({"healthy": True, "mode": mode(), "live_payments": False, "local_ai_enabled": ai_enabled()})
        else:
            self.respond({"error": "Not found"}, 404)

    def do_POST(self):
        try:
            if self.headers.get("Origin") not in (None, "http://127.0.0.1:9087", "http://localhost:9087"):
                raise DataError("Cross-site requests are not allowed.")
            if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
                raise DataError("Expected application/json.")
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 1200000:
                raise DataError("Request too large or empty.")
            body = json.loads(self.rfile.read(size))
            path = urlsplit(self.path).path
            if path == "/inspect":
                result = begin_report(body["csv"])
            elif path == "/insights":
                result = explain_ticket(body["ticket"])
            elif path == "/checkout":
                result = create_checkout(body["ticket"])
            elif path == "/capture":
                result = capture_checkout(body["ticket"], body["order_id"])
            else:
                return self.respond({"error": "Not found"}, 404)
            self.respond(result)
        except (DataError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self.respond({"error": str(exc)[:160]}, 400)
        except AIUnavailable as exc:
            self.respond({"error": str(exc)[:160]}, 503)
        except PaymentError as exc:
            self.respond({"error": str(exc)[:160]}, 502)

if __name__ == "__main__":
    print("ATLAS PayProof isolated preview on http://127.0.0.1:9087 — " + mode(), flush=True)
    ThreadingHTTPServer(("127.0.0.1", 9087), Handler).serve_forever()
