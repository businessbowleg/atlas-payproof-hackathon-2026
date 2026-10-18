# PayPal AI Hackathon — Submission Copy (NOT SUBMITTED)

Entry: PayProof — AI Supplier Integrity with PayPal Sandbox Checkout
Tagline: Catch broken supplier catalogs before they become broken customer orders.
Repository: https://github.com/businessbowleg/atlas-payproof-hackathon-2026
Hackathon: https://paypalaihackathon.devpost.com/
Deadline: November 12, 2026, 12:00 p.m. Pacific / 3:00 p.m. Eastern.

## Inspiration

Small sellers receive supplier CSV catalogs with duplicate SKUs, invalid pricing,
and inconsistent identifiers. These problems become broken listings and costly
manual corrections. PayProof offers local validation and AI explanations,
followed by a sandbox PayPal quote for a future remediation service.

## What it does

PayProof reads a supplier CSV and deterministically flags duplicate identifiers
and invalid prices, returning row-level findings and downloadable JSON evidence. It can ask a local CPU-only
Ollama model to explain the verified errors without supplying raw CSV rows
to the model. PayPal sandbox Orders v2 creates a $19 demonstration checkout,
and a separate read-only PayPal API call checks the sandbox order status.
Sandbox orders are never misrepresented as live payments.

## How we built it

Python standard-library browser server, CSV parser, Decimal validation,
local Ollama CPU-only model, PayPal sandbox OAuth and Orders v2 API,
responsive vanilla HTML/CSS/JS with a visual audit workbench, and unittest. Entire source is MIT-licensed
and separate from proprietary ATLAS production code.

## Key technical achievements

- Real PayPal sandbox OAuth verified on October 18, 2026.
- Real sandbox order creation verified with PayPal for 19.00 USD.
- Actual local CPU-only model inference verified (roughly 43 seconds).
- Deterministic CSV error detection with row-level problem reporting.
- Public GitHub repo containing runnable source, test suite and setup guide.
- No paid hosting, no production financial transactions, no real customer data.

## Challenges

Getting trustworthy data-integrity assessments matters more than plausible AI
text: rules determine whether rows pass, while local AI merely explains.
The payment workflow makes a strong distinction between a CREATED sandbox
order and a real paid transaction. All demo traffic is local/sandbox.

## What we learned

AI agents handling commerce need explicit evidence, provenance, and financial
truth. A generated checkout is not collected revenue. AI explanations need
deterministic grounding and limited data exposure.

## Next steps

Add human-approved CSV repair suggestions, signed payment webhooks,
merchant-facing authentication, and controlled catalog import pipelines.
These are proposed enhancements, not current capabilities.

## How judges can run it

Install Python 3.10 or newer.
Run: python3 -m unittest discover -s tests -v
Run: python3 app.py
Open: http://127.0.0.1:9087

For a genuine PayPal sandbox order, privately set PAYPAL_SANDBOX_CLIENT_ID and
PAYPAL_SANDBOX_SECRET from your own free sandbox developer app.
For local AI, install Ollama, pull an appropriate small model, and set
PAYPROOF_LOCAL_MODEL. The app also runs in explicitly labeled demo mode with
no credentials. Never publish sandbox secrets in GitHub.

## Submission state

GitHub source: PUBLISHED
Video captured (79 seconds) and published as GitHub release: VERIFIED
Public GitHub demo MP4: https://github.com/businessbowleg/atlas-payproof-hackathon-2026/releases/download/payproof-demo-v1/ATLAS_PayProof_Hackathon_Demo.mp4
Registered for hackathon: CONFIRMED BY OWNER
PayPal sandbox OAuth and order creation: VERIFIED
Buyer approval/capture: SKIPPED (do not claim completed)
Local model inference: VERIFIED
Public YouTube walkthrough URL: NOT YET AVAILABLE
Devpost final submission: NOT SUBMITTED
Prize money: NONE

Judging criteria: Technology, design, impact, innovation, presentation.
Official rules: https://paypalaihackathon.devpost.com/rules
