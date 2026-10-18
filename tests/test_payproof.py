"""Independent stdlib tests, no PayPal credentials or network needed."""
import os
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import app
from core import DataError, inspect_csv
from paypal_sandbox import PaymentError, SandboxPayPal, valid_capture

class QualityTests(unittest.TestCase):
    def test_good(self):
        r = inspect_csv("SKU,Price\nA,1.25\nB,20\n")
        self.assertEqual((r["accepted"], r["held"]), (2, 0))
    def test_case_insensitive_duplicate(self):
        r = inspect_csv("SKU,Price\nA,1\n a ,1\n")
        self.assertEqual(r["held"], 1)
    def test_bad_values(self):
        r = inspect_csv("SKU,Price\nB,-1\nC,NaN\nD,1.333\nE,0\n")
        self.assertEqual(r["held"], 4)
    def test_formula_in_sku_rejected(self):
        self.assertEqual(inspect_csv("SKU,Price\n=cmd,10\n")["held"], 1)
    def test_missing_columns(self):
        with self.assertRaises(DataError):
            inspect_csv("sku,amount\nx,2")
    def test_no_rows(self):
        with self.assertRaises(DataError):
            inspect_csv("SKU,Price\n")
    def test_size_limit(self):
        with self.assertRaises(DataError):
            inspect_csv("SKU,Price\n" + "A" * 1200000 + ",5")
    def test_quote_is_fixed_server_side(self):
        self.assertEqual(inspect_csv("SKU,Price\nX,1")["quote_usd"], "19.00")

class PaymentTests(unittest.TestCase):
    def test_missing_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(PaymentError):
                SandboxPayPal()
    def test_real_paypal_host_not_used(self):
        from paypal_sandbox import BASE
        self.assertEqual(BASE, "https://api-m.sandbox.paypal.com")
    def test_capture_verification(self):
        expected={"status":"COMPLETED","purchase_units":[{"payments":{"captures":[
            {"status":"COMPLETED","amount":{"currency_code":"USD","value":"19.00"}}]}}]}
        self.assertTrue(valid_capture(expected, "19.00"))
        self.assertFalse(valid_capture(expected, "20.00"))
        self.assertFalse(valid_capture({"status":"COMPLETED"}, "19.00"))
    def test_demo_never_means_paid(self):
        with patch.object(app, "SANDBOX", False):
            ticket=app.begin_report("SKU,Price\nX,1")["ticket"]
            order=app.create_checkout(ticket)
            result=app.capture_checkout(ticket, order["id"])
            self.assertFalse(result["paid"])
            self.assertEqual(result["status"], "DEMO_ONLY")
    def test_cannot_capture_other_order(self):
        with patch.object(app, "SANDBOX", False):
            ticket=app.begin_report("SKU,Price\nX,1")["ticket"]
            app.create_checkout(ticket)
            with self.assertRaises(DataError):
                app.capture_checkout(ticket, "DEMO-UNKNOWN")

if __name__ == "__main__":
    unittest.main()
