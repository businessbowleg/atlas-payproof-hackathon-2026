"""Deterministic supplier-data quality engine; no customer data leaves this process."""
import csv
import io
import re
from decimal import Decimal, InvalidOperation

MAX_BYTES = 1024 * 1024
MAX_ROWS = 1500
PRICE = "19.00"

class DataError(ValueError):
    pass

def inspect_csv(payload: str) -> dict:
    if not isinstance(payload, str) or not payload.strip():
        raise DataError("Provide CSV data.")
    if len(payload.encode("utf-8")) > MAX_BYTES:
        raise DataError("CSV exceeds 1 MiB limit.")
    try:
        rows = list(csv.DictReader(io.StringIO(payload, newline="")))
    except csv.Error as exc:
        raise DataError("Malformed CSV.") from exc
    if len(rows) > MAX_ROWS:
        raise DataError("CSV exceeds 1500 rows.")
    if not rows:
        raise DataError("CSV has no product rows.")
    headers = rows[0].keys()
    if None in headers or not {"sku", "price"}.issubset({str(x).lower().strip() for x in headers}):
        raise DataError("CSV must have SKU and Price columns.")
    header_map = {str(k).strip().lower(): k for k in headers}
    problems = []
    seen = set()
    safe_rows = 0
    for index, item in enumerate(rows, start=2):
        sku = str(item.get(header_map["sku"]) or "").strip()
        price = str(item.get(header_map["price"]) or "").strip()
        issues = []
        if not sku or not re.fullmatch(r"[A-Za-z0-9._-]{1,70}", sku):
            issues.append("SKU missing or invalid")
        if sku and sku.casefold() in seen:
            issues.append("Duplicate SKU")
        if sku:
            seen.add(sku.casefold())
        try:
            number = Decimal(price)
            if not number.is_finite() or number <= 0 or number.as_tuple().exponent < -2:
                issues.append("Invalid price")
        except InvalidOperation:
            issues.append("Invalid price")
        if issues:
            problems.append({"row": index, "sku": sku[:70], "issues": issues})
        else:
            safe_rows += 1
    return {
        "rows": len(rows),
        "accepted": safe_rows,
        "held": len(problems),
        "issues": problems[:100],
        "issues_truncated": len(problems) > 100,
        "quote_usd": PRICE,
        "rules": ["required SKU", "case-insensitive unique SKU", "finite positive USD price with at most two decimals"],
    }

def summary(result: dict) -> str:
    n = result["held"]
    if n == 0:
        return "All rows passed the deterministic checks. This does not verify supplier legitimacy or product compliance."
    return f"{n} of {result['rows']} rows were held. Review the row-level exceptions before importing the catalog."
