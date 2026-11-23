# Portfolio Evidence Plan

This project is designed to demonstrate the skills required for an e-commerce automation role. Use only evidence you can verify.

| Role requirement | Evidence in this project | What you must complete |
| --- | --- | --- |
| Python scripts and data processing | `src/analyzer.py`, `src/main.py` | Explain the stock and margin rules in your own words. |
| API connections | `src/sheets_client.py` | Complete the Google Sheets connection and successful local run. |
| Scheduled runs | `.github/workflows/daily_sentinel.yml` | Trigger one manual GitHub Actions run, then capture a successful scheduled run. |
| Failure awareness | `src/main.py`, `src/notifier.py`, `docs/runbook.md` | Verify a failure alert path without exposing secrets. |
| Clear documentation | `README.md`, `docs/` | Keep setup steps accurate as you test. |
| Time saved | `docs/measurement.md` | Measure baseline and post-automation time; do not estimate as a fact. |
| Expert interviews | `docs/process-discovery.md` | Use the questions with a real operator or explain how you would validate rules. |

## Before you share the project publicly

1. Confirm `git status --ignored` shows `.env` and `credentials.json` as ignored.
2. Confirm the repository contains only generic data and no private Sheet URL or ID.
3. Run the workflow manually and confirm the exception and log tabs update.
4. Capture a screenshot of the green Actions run and a redacted Sheet result.
5. Record a 60-120 second demo video using the README demo sequence.
6. Change the repository visibility to Public only after the security review.

## Truthful application wording

Use this only after the live test succeeds:

> I built a Python inventory-monitoring automation for a sample e-commerce SKU workflow. It reads a Google Sheet, calculates days of supply and net margin, writes an action queue for stockout and margin risks, records every run, and sends alerts. The project uses Python, the Google Sheets API, GitHub Actions scheduling, and documented recovery steps. I used generic data for the public demo and measured the time-saving baseline separately.

Replace any statement about run success rate or hours saved with your own measured result.
