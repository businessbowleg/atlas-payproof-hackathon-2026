# PayProof — Supplier Data Integrity + PayPal AI Commerce

**Status: isolated prototype, NOT a production payment or AI service.**

PayProof validates supplier CSV data and demonstrates a checkout workflow using the PayPal Orders v2 **sandbox only**. Created as a small, independently licensed hackathon candidate by Bowleg Systems. This repository is **not** ATLAS's proprietary internal code.

## Why it exists

Small merchants import faulty supplier catalogs. This app catches invalid prices, duplicate SKUs and invalid identifiers, then demonstrates paying for a more complete workflow. A local-LLM explanation is optional and disabled by default. Automatic corrected-file delivery is **not implemented** and must not be claimed as completed.

## Run locally (zero external packages)

Requires Python 3.10+.

    python3 -m unittest discover -s tests -v
    python3 app.py

Open http://127.0.0.1:9087 — prepopulated sample is fictional.

The app binds to loopback and stores session state in process memory only. The CSV is not written to disk. The test suite makes no network calls.

## Optional local AI (owner-controlled, off by default)

Set PAYPROOF_LOCAL_MODEL to an Ollama model already approved for use on your own machine. Then POST /insights with a ticket or use the button in the preview. The prompt receives only aggregate validation counts and issue categories, **not** uploaded CSV text. It calls loopback Ollama only. Verify the available model lane and resource budget before enabling; never preempt ATLAS production GPUs for a hackathon.

## Payment modes

* **DEMO_NO_PAYMENT** (default): Create order simulates a checkout. It cannot transfer money, and its response clearly says so.
* **PAYPAL_SANDBOX**: set PAYPAL_SANDBOX_CLIENT_ID and PAYPAL_SANDBOX_SECRET in process environment. This uses https://api-m.sandbox.paypal.com exclusively to create PayPal Orders v2 and returns an approval URL.

Example, with credentials loaded **privately** into the shell (never committed):

    PAYPAL_SANDBOX_CLIENT_ID="$ID" PAYPAL_SANDBOX_SECRET="$SECRET" python3 app.py

The sandbox approval is a test transaction. The capture endpoint verifies the order ID, amount, currency, and capture status on the server. Do not treat sandbox captures as revenue.

## API

* GET /health — preview status
* POST /inspect — JSON with csv text, returns ticket, diagnostics and quote
* POST /insights — optional local AI report explanation; 503 when disabled
* POST /checkout — JSON with ticket, returns demo or sandbox order
* POST /capture — JSON with ticket and order_id; verifies PayPal sandbox capture (API-only)

Do **not** deploy this preview on a public interface. Before production, add authentication, persistent idempotent payment records, strict server-side amounts, CSRF protection, rate limits, event/webhook verification, no sensitive-data logs, a real privacy policy, and independent security verification.

## Hackathon status

Candidate for the **PayPal AI Hackathon** (deadline Nov 12, 2026). This prototype is **not yet eligible as a completed entry** because live local-AI inference verification, payment approval end-to-end, a public repo, a presentation/demo, and Devpost entry remain outstanding.

Optional secondary candidate: GitLab Transcend, but real GitLab Duo Agent Platform workflows and public CI history are required. This project does not claim either currently.

## Intellectual property and safety

Only fictional examples. Do not add private ATLAS logic, employer documents, customer data, token files, merchant credentials or corporate secrets. MIT license applies only to this standalone project. Check competition terms before public release.

Sources: https://paypalaihackathon.devpost.com/rules ; https://developer.paypal.com/api/rest/authentication ; https://developer.paypal.com/api/orders-v2/ .


## Hackathon submission materials

See [SUBMISSION_DRAFT.md](SUBMISSION_DRAFT.md) for a fact-checked pitch,
demo-video outline, important limitations and checklist. A public YouTube
demo video and PayPal sandbox credentials are not included in source code.

This project can be published on GitHub. Its release does not confer any
permission to publish or modify proprietary ATLAS production source.
