"""Human-reviewed supplier CSV remediation.

Rules:
* Never silently change an SKU or price.
* Validate data and CSV provenance before accepting explicit operator edits.
* Block formula-bearing cells from exported CSV.
* Never call payments or remote models.
* Do not persist the supplier catalog.
"""
import csv
import hashlib
import hmac
import io
import re
from decimal import Decimal, InvalidOperation

from core import DataError, MAX_BYTES, MAX_ROWS, inspect_csv


def _digest(text):
    if not isinstance(text, str):
        raise DataError("CSV must be text.")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _table(text):
    if not isinstance(text, str) or len(text.encode("utf-8")) > MAX_BYTES:
        raise DataError("Missing or oversized CSV.")
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        headers = reader.fieldnames
        if not headers or any(h is None or not str(h).strip() for h in headers):
            raise DataError("Malformed header.")
        lower = [x.strip().lower() for x in headers]
        if len(set(lower)) != len(lower):
            raise DataError("Duplicate or ambiguous CSV headers.")
        if not {"sku", "price"} <= set(lower):
            raise DataError("CSV must have SKU and Price columns.")
        rows = list(reader)
    except csv.Error as exc:
        raise DataError("Malformed CSV.") from exc
    if not rows or len(rows) > MAX_ROWS:
        raise DataError("CSV has no rows or exceeds 1500 rows.")
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise DataError("Every CSV row must match the header length.")
    return headers, rows, headers[lower.index("sku")], headers[lower.index("price")]


def plan_repairs(text):
    baseline = inspect_csv(text)
    _table(text)
    return {
        "source_sha256": _digest(text),
        "rows": baseline["rows"],
        "held": baseline["held"],
        "issues": [
            {"row": entry["row"], "sku": entry["sku"], "reasons": entry["issues"],
             "required_action": "Operator must provide an explicit corrected SKU and/or price."}
            for entry in baseline["issues"]
        ],
        "issues_truncated": baseline["issues_truncated"],
        "notice": "No corrections have been applied. A person must approve every edit.",
    }


def apply_reviewed_repairs(text, source_sha256, edits, approved=False):
    if approved is not True:
        raise DataError("Explicit operator approval required.")
    current_digest = _digest(text)
    if not isinstance(source_sha256, str) or not hmac.compare_digest(source_sha256, current_digest):
        raise DataError("Source CSV fingerprint mismatch; inspect the current catalog again.")
    baseline = inspect_csv(text)
    headers, rows, sku_col, price_col = _table(text)
    if not isinstance(edits, list) or len(edits) > MAX_ROWS:
        raise DataError("Edits must be a bounded list.")
    editable = {entry["row"] for entry in baseline["issues"]}
    if baseline["issues_truncated"]:
        raise DataError("Too many held rows for reviewed remediation; process in smaller batches.")
    seen = set()
    applied = []
    for patch in edits:
        if not isinstance(patch, dict) or set(patch) - {"row", "sku", "price"}:
            raise DataError("Each correction needs a row and permitted SKU/price fields only.")
        row = patch.get("row")
        if type(row) is not int or row not in editable or row in seen:
            raise DataError("Edit refers to a non-held, duplicate, or out-of-range row.")
        if not set(patch).intersection({"sku", "price"}):
            raise DataError("Edit contains no correction.")
        seen.add(row)
        product = rows[row - 2]
        changes = []
        for key, col in (("sku", sku_col), ("price", price_col)):
            if key in patch:
                value = patch[key]
                if not isinstance(value, str):
                    raise DataError("Correction values must be strings.")
                value = value.strip()
                if key == "sku" and not re.fullmatch(r"[A-Za-z0-9._-]{1,70}", value):
                    raise DataError("Corrected SKU is invalid.")
                if key == "price":
                    try:
                        number = Decimal(value)
                    except InvalidOperation as exc:
                        raise DataError("Corrected price is invalid.") from exc
                    if (not number.is_finite() or number <= 0 or
                            number.as_tuple().exponent < -2 or number >= Decimal("1000000000000")):
                        raise DataError("Corrected price must be positive USD with at most two decimals.")
                    value = f"{number:.2f}"
                if value != product[col]:
                    product[col] = value
                    changes.append(key)
        if changes:
            applied.append({"row": row, "changed_fields": changes})
    # If deterministic failures remain, do not export *any* CSV. An incomplete
    # plan may still contain invalid negative prices, so formula checks apply
    # only when an export is otherwise eligible.
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=headers, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows(rows)
    result = out.getvalue()
    report = inspect_csv(result)
    ready = report["held"] == 0 and bool(applied) and baseline["held"] > 0
    if not ready:
        return {
            "source_sha256": current_digest, "candidate_sha256": None,
            "applied": applied, "ready": False,
            "remaining": report["issues"], "remaining_count": report["held"],
            "candidate_csv": None,
            "notice": "Remaining validation failures: no corrected file will be exported."
        }
    # CSV spreadsheet formula injection can affect ANY column, not just SKU/Price.
    formula_risks = []
    for i, product in enumerate(rows, start=2):
        for header in headers:
            cell = product[header].lstrip()
            if cell and cell[0] in ("=", "+", "-", "@", "\t", "\r"):
                formula_risks.append({"row": i, "field": header})
    if formula_risks:
        raise DataError("Export blocked: spreadsheet formula-like cells present; review original CSV data.")
    if len(result.encode("utf-8")) > MAX_BYTES:
        raise DataError("Remediated CSV exceeds 1 MiB limit.")
    return {
        "source_sha256": current_digest,
        "candidate_sha256": _digest(result),
        "applied": applied,
        "ready": ready,
        "remaining": report["issues"],
        "remaining_count": report["held"],
        # No downloadable CSV until every deterministic hold is resolved.
        "candidate_csv": result if ready else None,
        "notice": "READY FOR HUMAN REVIEW, NOT FOR AUTOMATIC SUPPLIER IMPORT." if ready
                  else "Remaining validation failures: no corrected file will be exported.",
    }
