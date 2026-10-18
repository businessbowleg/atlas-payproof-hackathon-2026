"""Read-only PayPal sandbox status must not capture an order."""
import json
import os
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app
from core import DataError
from paypal_sandbox import SandboxPayPal, PaymentError

class StatusTests(unittest.TestCase):
    def test_before_checkout_refused(self):
        ticket=app.begin_report("SKU,Price\nTEST,5.00\n")["ticket"]
        with self.assertRaises(DataError):
            app.get_checkout_status(ticket)

    def test_demo_status_is_not_paid(self):
        with patch.object(app, "SANDBOX", False):
            ticket=app.begin_report("SKU,Price\nTEST,5.00\n")["ticket"]
            app.create_checkout(ticket)
            v=app.get_checkout_status(ticket)
        self.assertEqual(v["status"], "SIMULATED")
        self.assertFalse(v["real_funds"])

    def test_paypal_status_read_only(self):
        with patch.object(app, "SANDBOX", True):
            with patch.object(app, "SandboxPayPal") as provider:
                provider.return_value.create_order.return_value={
                    "id":"SANDBOX123456","approve_url":"https://www.sandbox.paypal.com/foo",
                    "status":"CREATED"}
                provider.return_value.get_order.return_value={
                    "id":"SANDBOX123456","status":"CREATED",
                    "purchase_units":[{"amount":{"currency_code":"USD","value":"19.00"}}]}
                ticket=app.begin_report("SKU,Price\nTEST,5.00\n")["ticket"]
                app.create_checkout(ticket)
                v=app.get_checkout_status(ticket)
                self.assertEqual(v["status"],"CREATED")
                self.assertTrue(v["sandbox"])
                self.assertFalse(v["real_funds"])
                provider.return_value.get_order.assert_called_once_with("SANDBOX123456")
                provider.return_value.capture_order.assert_not_called()

    def test_bad_amount_rejected(self):
        with patch.object(app, "SANDBOX", True):
            with patch.object(app, "SandboxPayPal") as provider:
                provider.return_value.create_order.return_value={
                    "id":"SANDBOX123456","approve_url":"https://www.sandbox.paypal.com/foo",
                    "status":"CREATED"}
                provider.return_value.get_order.return_value={
                    "id":"SANDBOX123456","status":"CREATED",
                    "purchase_units":[{"amount":{"currency_code":"USD","value":"99.00"}}]}
                ticket=app.begin_report("SKU,Price\nTEST,5.00\n")["ticket"]
                app.create_checkout(ticket)
                with self.assertRaises(PaymentError):
                    app.get_checkout_status(ticket)
                provider.return_value.capture_order.assert_not_called()

    def test_paypal_get_never_post_or_capture(self):
        with patch.dict(os.environ,{"PAYPAL_SANDBOX_CLIENT_ID":"CLIENT_TEST",
                                    "PAYPAL_SANDBOX_SECRET":"SECRET_TEST"}):
            sdk=SandboxPayPal()
            sdk._token=lambda: "FAKE_ACCESS_TOKEN"
            class Response:
                def __enter__(self):return self
                def __exit__(self,*args):pass
                def read(self):return json.dumps({"id":"SANDBOX123456","status":"CREATED"}).encode()
            def mocked(req,timeout):
                self.assertEqual(req.get_method(),"GET")
                self.assertTrue(req.full_url.startswith("https://api-m.sandbox.paypal.com/"))
                self.assertNotIn("/capture",req.full_url)
                return Response()
            with patch("paypal_sandbox.urllib.request.urlopen",side_effect=mocked):
                self.assertEqual(sdk.get_order("SANDBOX123456")["status"],"CREATED")

    def test_invalid_order_id_rejected(self):
        with patch.dict(os.environ,{"PAYPAL_SANDBOX_CLIENT_ID":"CLIENT_TEST",
                                    "PAYPAL_SANDBOX_SECRET":"SECRET_TEST"}):
            with self.assertRaises(PaymentError):
                SandboxPayPal().get_order("../LIVE")
