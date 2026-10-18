# PayProof R3 — human-reviewed supplier corrections (candidate)

Branch: feature/reviewed-csv-remediation
Status: Candidate enhancement, NOT the hackathon R2 submission baseline.

This isolated revision adds a bounded, deterministic remediation workflow:

1. Inspect up to 1,500 CSV rows via the existing rule engine.
2. Generate an evidence-linked plan with exact row numbers and original SHA-256.
3. Let a human enter explicit replacement SKU and/or USD prices.
4. Require an affirmative approval checkbox before evaluating edits.
5. Verify the original source fingerprint, allowed row IDs, updated price formats,
   SKU uniqueness and absence of spreadsheet formula-like cells.
6. Withhold the corrected CSV until all basic integrity holds are resolved.
7. Permit a local download of the human-reviewed candidate CSV; never import it,
   publish it, contact a supplier, or take a payment.

No AI inference, payment request, account creation, outbound email, or production
deployment occurs in the remediation endpoints. The report does not establish
product legitimacy, compliance, supplier authorization or merchant readiness.

## Isolated validation

Run 39 unit tests with Python unittest discovery. Start the isolated local
preview with PAYPROOF_PORT=9091 and no sandbox credentials.

R3 must be separately reviewed and approved for merge only after the existing
PayProof R2 Devpost submission workflow is finished. Do not substitute R3 for
the already greenlit R2 recording and source while Work publishes them.

## Observed checks (2026-10-18)

* 39 standalone automated unit tests passing.
* Real Chrome end-to-end R3 remediation check passed.
* Real local HTTP preview endpoints passed.
* Small mobile viewport (375 px) had no horizontal overflow.
* No payment integrations invoked during remediation.
