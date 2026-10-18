import json
import os
import unittest
from unittest.mock import patch, MagicMock
import assistant
import app
from core import inspect_csv, DataError

class LocalAI(unittest.TestCase):
    def test_disabled_no_inference(self):
        with patch.dict(os.environ, {"PAYPROOF_LOCAL_MODEL": ""}):
            with self.assertRaises(assistant.AIUnavailable):
                assistant.explain(inspect_csv("SKU,Price\nX,5"))
    def test_local_only_and_aggregates(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, *args): return b'{"response":"Check held rows first."}'
        def fake(req, timeout):
            self.assertEqual(req.full_url, "http://127.0.0.1:11434/api/generate")
            data = json.loads(req.data)
            self.assertNotIn("HIDDEN-PRIVATE-DATA", data["prompt"])
            self.assertEqual(data["options"]["temperature"], 0)
            return Response()
        report = inspect_csv("SKU,Price\nHIDDEN-PRIVATE-DATA,1")
        with patch.dict(os.environ, {"PAYPROOF_LOCAL_MODEL": "test-small-model"}):
            with patch.object(assistant.urllib.request, "urlopen", side_effect=fake):
                self.assertIn("Check held", assistant.explain(report)["guidance"])

class PaymentState(unittest.TestCase):
    def test_sandbox_checks_amount_before_marking_captured(self):
        with patch.object(app, "SANDBOX", True):
            with patch.object(app, "SandboxPayPal") as provider:
                provider.return_value.create_order.return_value = {
                    "id":"SANDBOX123456", "approve_url":"https://www.sandbox.paypal.com/foo", "status":"CREATED"}
                provider.return_value.capture_order.return_value = {
                    "id":"SANDBOX123456", "status":"COMPLETED", "purchase_units":[{"payments":{"captures":[{
                        "status":"COMPLETED","amount":{"currency_code":"USD","value":"1.00"}}]}}]}
                ticket=app.begin_report("SKU,Price\nX,5")["ticket"]
                app.create_checkout(ticket)
                with self.assertRaises(app.PaymentError):
                    app.capture_checkout(ticket, "SANDBOX123456")
                self.assertNotEqual(app.sessions[ticket]["state"], "SANDBOX_CAPTURED")
    def test_deduplicated_sandbox_order(self):
        with patch.object(app, "SANDBOX", True):
            with patch.object(app, "SandboxPayPal") as provider:
                provider.return_value.create_order.return_value = {
                    "id":"SANDBOX123456", "approve_url":"https://www.sandbox.paypal.com/foo", "status":"CREATED"}
                ticket=app.begin_report("SKU,Price\nX,5")["ticket"]
                first=app.create_checkout(ticket)
                second=app.create_checkout(ticket)
                self.assertEqual(first, second)
                provider.return_value.create_order.assert_called_once()
