"""Financially isolated reviewed CSV correction tests."""
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core import DataError
from remediation import plan_repairs, apply_reviewed_repairs

SAMPLE = "SKU,Price,Name\nDEMO-101,12.50,Gasket\nDEMO-101,12.50,Duplicate\nDEMO-103,-4.00,Invalid\n"

def revise(csv=SAMPLE, changes=None, approved=True, hash_override=None):
    token=plan_repairs(csv)["source_sha256"]
    return apply_reviewed_repairs(csv, hash_override if hash_override is not None else token,
                                  changes or [], approved=approved)

class RemediationTests(unittest.TestCase):
    def test_no_automatic_edits(self):
        plan=plan_repairs(SAMPLE)
        self.assertEqual(plan["held"], 2)
        self.assertEqual([x["row"] for x in plan["issues"]], [3,4])
        self.assertNotIn("candidate_csv", plan)

    def test_explicit_two_corrections_export(self):
        outcome=revise(changes=[{"row":3,"sku":"DEMO-102"},{"row":4,"price":"5"}])
        self.assertTrue(outcome["ready"])
        self.assertEqual(outcome["remaining_count"], 0)
        self.assertIn("DEMO-102,12.50,Duplicate", outcome["candidate_csv"])
        self.assertIn("DEMO-103,5.00,Invalid", outcome["candidate_csv"])
        self.assertEqual(len(outcome["applied"]), 2)

    def test_requires_operator_consent(self):
        with self.assertRaisesRegex(DataError, "approval"):
            revise(changes=[{"row":3,"sku":"DEMO-102"}],approved=False)

    def test_source_provenance(self):
        with self.assertRaisesRegex(DataError, "fingerprint"):
            revise(changes=[{"row":3,"sku":"DEMO-102"}],hash_override="9"*64)

    def test_cannot_change_passing_row(self):
        with self.assertRaisesRegex(DataError,"non-held"):
            revise(changes=[{"row":2,"sku":"DEMO-999"}])

    def test_reject_duplicate_row_edits(self):
        with self.assertRaises(DataError):
            revise(changes=[{"row":3,"sku":"NEW-A"},{"row":3,"sku":"NEW-B"}])

    def test_no_file_when_incomplete(self):
        r=revise(changes=[{"row":3,"sku":"DEMO-102"}])
        self.assertFalse(r["ready"])
        self.assertIsNone(r["candidate_csv"])
        self.assertEqual(r["remaining_count"], 1)

    def test_no_file_when_duplicate_remains(self):
        r=revise(changes=[{"row":3,"sku":"DEMO-101"},{"row":4,"price":"5"}])
        self.assertFalse(r["ready"])
        self.assertIsNone(r["candidate_csv"])

    def test_invalid_prices_rejected(self):
        for price in ("-5","0","NaN","Infinity","1.234","garbage","+1e99"):
            with self.subTest(price=price):
                with self.assertRaises(DataError):
                    revise(changes=[{"row":4,"price":price}])

    def test_csv_formula_other_column_fails_closed(self):
        doc="SKU,Price,Name\nGOOD,10,Safe\nGOOD,10,=HYPERLINK(\"\"url\"\")\n"
        with self.assertRaisesRegex(DataError,"formula"):
            revise(doc,changes=[{"row":3,"sku":"SAFE-2"}])

    def test_price_formula_requires_operator_fix(self):
        doc="SKU,Price,Name\nA,2.00,Safe\nB,=2+2,Example\n"
        incomplete=revise(doc,changes=[])
        self.assertFalse(incomplete["ready"])
        self.assertIsNone(incomplete["candidate_csv"])
        with self.assertRaises(DataError):
            revise(doc,changes=[{"row":3,"price":"=2+2"}])

    def test_case_insensitive_duplicate_recheck(self):
        r=revise(changes=[{"row":3,"sku":"demo-101"},{"row":4,"price":"2.00"}])
        self.assertFalse(r["ready"])

    def test_disallow_unrecognized_keys(self):
        with self.assertRaisesRegex(DataError,"permitted"):
            revise(changes=[{"row":3,"sku":"B","force":True}])

    def test_disallow_malformed_header(self):
        with self.assertRaises(DataError):
            plan_repairs("SKU,sku,Price\nX,Y,1\n")

    def test_original_remains_unchanged(self):
        _=revise(changes=[{"row":3,"sku":"DEMO-102"},{"row":4,"price":"5"}])
        self.assertEqual(SAMPLE.splitlines()[2],"DEMO-101,12.50,Duplicate")

    def test_no_remote_integrations(self):
        import remediation
        from pathlib import Path
        data=Path(remediation.__file__).read_text(encoding="utf-8")
        self.assertNotIn("urllib",data)
        self.assertNotIn("SandboxPayPal",data)

if __name__ == "__main__":
    unittest.main()
