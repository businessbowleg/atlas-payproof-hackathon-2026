"""PayPal Orders v2 SANDBOX adapter. No live API host exists in this module."""
import base64
import json
import os
import re
import urllib.error
import urllib.request
import uuid
from decimal import Decimal

BASE = "https://api-m.sandbox.paypal.com"

class PaymentError(RuntimeError):
    pass

class SandboxPayPal:
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_SANDBOX_CLIENT_ID", "")
        self.secret = os.getenv("PAYPAL_SANDBOX_SECRET", "")
        if not self.client_id or not self.secret:
            raise PaymentError("Sandbox credentials are not configured.")

    def _request(self, path, body, token=None, request_id=None):
        if not path.startswith("/") or not isinstance(body, (dict, str)):
            raise PaymentError("Invalid sandbox request.")
        if token is None:
            raw = (self.client_id + ":" + self.secret).encode()
            auth = "Basic " + base64.b64encode(raw).decode()
        else:
            auth = "Bearer " + token
        payload = body.encode() if isinstance(body, str) else json.dumps(body).encode()
        headers = {"Authorization": auth, "Accept": "application/json",
                   "Content-Type": "application/x-www-form-urlencoded" if isinstance(body, str) else "application/json"}
        if request_id:
            headers["PayPal-Request-Id"] = request_id
        req = urllib.request.Request(BASE + path, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=12) as res:
                return json.loads(res.read())
        except urllib.error.HTTPError as exc:
            raise PaymentError("PayPal sandbox returned HTTP " + str(exc.code)) from exc
        except (OSError, ValueError) as exc:
            raise PaymentError("PayPal sandbox unavailable.") from exc

    def _token(self):
        body = self._request("/v1/oauth2/token", "grant_type=client_credentials")
        token = body.get("access_token")
        if not token:
            raise PaymentError("Sandbox OAuth did not return a token.")
        return token

    def create_order(self, amount, reference):
        if Decimal(amount) <= 0 or not re.fullmatch(r"[A-Za-z0-9_-]{8,80}", reference):
            raise PaymentError("Invalid checkout request.")
        payload = {"intent": "CAPTURE", "purchase_units": [
            {"reference_id": reference, "amount": {"currency_code": "USD", "value": str(amount)}}]}
        data = self._request("/v2/checkout/orders", payload, self._token(), str(uuid.uuid4()))
        url = next((link["href"] for link in data.get("links", [])
                    if link.get("rel") in ("approve", "payer-action")), None)
        if not data.get("id") or not url:
            raise PaymentError("Sandbox order missing approval information.")
        if not url.startswith("https://www.sandbox.paypal.com/"):
            raise PaymentError("Sandbox approval URL verification failed.")
        return {"id": data["id"], "approve_url": url, "status": data.get("status")}

    def capture_order(self, order_id, request_id):
        if not re.fullmatch(r"[A-Za-z0-9]{8,40}", order_id):
            raise PaymentError("Invalid order ID.")
        return self._request("/v2/checkout/orders/" + order_id + "/capture",
                             {}, self._token(), request_id)

def valid_capture(data, expected_amount):
    if data.get("status") != "COMPLETED":
        return False
    for unit in data.get("purchase_units", []):
        for entry in unit.get("payments", {}).get("captures", []):
            amount = entry.get("amount") or {}
            if (entry.get("status") == "COMPLETED" and amount.get("currency_code") == "USD"
                and Decimal(amount.get("value", "0")) == Decimal(expected_amount)):
                return True
    return False
