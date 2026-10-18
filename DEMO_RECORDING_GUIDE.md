# PayProof — Actual hackathon demonstration recording plan

A **real 79-second browser recording has now been produced**.
It can be downloaded from:
https://github.com/businessbowleg/atlas-payproof-hackathon-2026/releases/download/payproof-demo-v1/ATLAS_PayProof_Hackathon_Demo.mp4

This document remains the recording plan for reshoots, and the video still
must be uploaded to PUBLIC YouTube to satisfy the Devpost requirement.
The recorded footage comes from a real headless Chrome session on NODE001.
DO NOT simulate PayPal approval, AI model output, customer data, or prize status.

Official deadline: November 12, 2026, 12:00 p.m. Pacific / 3:00 p.m. Eastern.
The YouTube demonstration must be public and UNDER three minutes.
Under the rules, a runnable local app with complete instructions is sufficient;
hosted deployment is optional.

## Target 2:15 recording

00:00–00:15 — Show the actual PayProof landing page with its sample supplier CSV.
Narration: "A duplicate SKU or negative price can destroy an import. PayProof catches it first."

00:15–00:40 — Click Inspect; show the exact exception rows.
Narration: "These are deterministic checks, not AI guesses: one valid row, two held rows."

00:40–01:20 — Click Explain with local AI; wait for actual inference. The original live
CPU-only inference measured about 43 seconds. Editing may trim waiting time, but
must not claim instantaneous execution. 
Narration: "Our local model explains verified faults. Only aggregate findings,
not supplier source rows, go into the AI prompt."

01:20–01:48 — Click Create sandbox checkout; show the actual sandbox order.
Narration: "PayPal's sandbox creates a $19 demonstration order. No real funds move."

01:48–02:00 — Click Check sandbox order status (no purchase), show CREATED.
Narration: "This order has not been approved or paid. PayProof keeps that explicit."

02:00–02:15 — Show GitHub README and terminal with passing tests.
Narration: "The MIT-licensed source can run locally with Python and a free PayPal
developer sandbox. AI processing is optional and local."

## Owner recording steps

On NODE001, open the ATLAS PayProof Demo desktop shortcut, or navigate to
http://127.0.0.1:9087 in a browser if the local server is already running.
Use Windows Snipping Tool screen recording to capture the actual browser
actions. A single genuine recording is preferable to an artificial rendering.
Trim under three minutes, publish it publicly on YouTube, then submit its URL
on https://paypalaihackathon.devpost.com/ before the deadline.

Do not show any credentials, proprietary ATLAS screens, or personal documents.
Use only the fictional CSV in the app. No licensed music or third-party visuals.
The PayPal buyer approval and capture sequence has been SKIPPED at owner request.
That is not a failure of the read-only PayPal status demonstration.

Do not label this script or a textual preview as a real video.
