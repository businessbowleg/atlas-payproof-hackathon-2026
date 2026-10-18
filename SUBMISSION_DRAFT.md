# PayPal AI Hackathon — Draft entry (NOT submitted)

Event: https://paypalaihackathon.devpost.com/
Official deadline: November 12, 2026, 12:00 PM Pacific Standard Time (3:00 PM Eastern).
Entry fee: $0.

## Project name
PayProof — AI-guided supplier integrity and sandbox purchase approval

## Elevator pitch
Small online sellers routinely receive supplier product feeds with duplicate SKUs,
invalid prices, and other import blockers. PayProof evaluates catalog readiness
locally, explains problems with an optionally enabled local AI model, and
demonstrates a human-approved PayPal sandbox payment for a detailed remediation
workflow. Deterministic checks—not AI guesses—decide which records are held.
It keeps customer data local and never mistakes sandbox currency for real revenue.

## Motivation
Merchant onboarding workflows are tedious, expensive, and easy to get wrong.
Unchecked supplier data can lead to broken listings, customer confusion,
and unnecessary manual cleanup.

## Demonstrated capabilities as of initial prototype
- Local browser-based CSV inspection of fictional data
- Duplicate and invalid price detection; row-specific exceptions
- Optional local-only Ollama explanation behind explicit enable flag
- PayPal Orders v2 create/capture *sandbox* code path, with mocked tests
- Fail-closed sandbox capture verification and demo-mode payment disclaimers
- Automated unit tests and local HTTP smoke test
- Source code independently licensed under MIT; no proprietary ATLAS files

## Not yet demonstrated — MUST finish before claiming a completed entry
- Actual PayPal developer sandbox order creation, buyer approval, capture
- Actual local-model inference test with appropriate spare compute
- Robust AI-guided actionable remediation beyond a basic explanation
- Video under three minutes, PUBLIC on YouTube, showing real app operation
- Working public repository and public submission with approved representative
- Any claim that a paid service, production checkout, public user accounts,
  automatic repair delivery, or actual payments exists

## Demo-video outline (target 2:15)
00:00–00:15 — The problem: an illustrative supplier CSV fails import
00:15–00:40 — Local CSV upload/inspection; duplicate and invalid price identified
00:40–01:00 — Optional local AI describes only verified exceptions
01:00–01:35 — PayPal SANDBOX order creation, explicit customer approval, capture
01:35–01:50 — Show sandbox result and that zero real money changed hands
01:50–02:05 — Independent tests and reproducible source instructions
02:05–02:15 — Clear limitations, target audience, future product

Only record the sandbox segment after it works end-to-end.
Do not fabricate footage, customer endorsements, prizes, or financial results.

## Prize relevance
Possible: Grand prizes, Best Use of PayPal + AI, Best Use of Agentic Commerce.
These are judged awards with uncertain probability. This project has no
special-sponsor integration currently; do not claim eligibility for sponsor prizes.

## Explicit owner-controlled actions remaining
1. Verify repository URL and app access (connected account currently lists no repos).
2. Join the hackathon under the owner's identity or authorized business representative.
3. Provision FREE PayPal developer sandbox credentials safely (never paste in chat).
4. Verify live sandbox order creation/approval/capture and optionally local AI.
5. Record and publish a real demo video, then submit on Devpost before deadline.

Official criteria: technology, design, impact, novelty, presentation
https://paypalaihackathon.devpost.com/rules

## Security and ownership
This prototype is not connected to ATLAS production, real Shopify orders,
live PayPal merchant accounts, or customer data. Never add any real credentials
or private business files to this public project.
