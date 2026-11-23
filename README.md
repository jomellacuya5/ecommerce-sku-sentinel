# E-commerce SKU Sentinel

Python automation that replaces a manual e-commerce SKU review with a scheduled inventory and margin-risk check.

It reads a Google Sheet, calculates stock coverage and unit net margin, writes only actionable SKUs to an exception queue, records each run, and sends an email alert when action is needed.

> The repository uses generic sample data only. No client, product, credential, or private Google Sheet ID is included.

Inventory planning is often a manual review of a spreadsheet. This automation turns that review into a repeatable daily process: it applies defined business rules, records what happened, and alerts a reviewer only when a SKU needs attention.

**Status:** Live scheduled automation — verified via local execution and GitHub Actions (processes SKU velocity and unit net margin checks in ~2–3 seconds per run using anonymized sample catalog data).

## What it replaces

**Before:** An operator manually reviews a SKU spreadsheet, estimates days of stock remaining, checks margin, prepares an action list, and sends follow-up messages.

**After:** A scheduled Python run applies the same rules consistently, produces an `Action_Exceptions` queue, logs every result in `System_Run_Log`, and emails the exception digest.

## How it works

```text
Raw_SKU_Data (Google Sheets via Apps Script Web App REST Bridge)
        -> Python validation and calculations
        -> Action_Exceptions + System_Run_Log
        -> Email alert when a SKU needs action
```

### Rules

| Signal | Rule | Output |
| --- | --- | --- |
| Stockout risk | `days_of_supply <= lead_time_days + safety_stock_days` | `REORDER NOW` |
| Margin risk | `net_margin_pct < 15` | `LOW MARGIN AUDIT` |
| Both risks | Both rules match | `REORDER + LOW MARGIN` |
| Zero sales | `units_sold_30d = 0` | Uses `days_of_supply = 999` without division by zero |

## Tools used

- **Python:** data validation, inventory calculations, orchestration, and alerts
- **pandas:** SKU data processing
- **Google Apps Script Web App + requests:** serverless JSON REST bridge for Google Sheets reads and writes (eliminates external cloud service-account key overhead)
- **Gmail SMTP:** exception and failure notifications
- **GitHub Actions:** daily schedule and manual workflow runs
- **Git + VS Code:** version control and development

## Time-savings measurement

Time savings are tracked on every run against an operator's measured manual review baseline.

| Measure | Before automation | After automation |
| --- | ---: | ---: |
| Manual SKU-review minutes per run | Record baseline | Record exception-review time |
| Runs per month | Record baseline | Record scheduled runs |
| Monthly hours | `(minutes x runs) / 60` | `(minutes x runs) / 60` |

`hours_saved_per_month = manual_monthly_hours - automated_monthly_hours`

To record a baseline on every successful run, measure the manual process first and set `BASELINE_MANUAL_REVIEW_MINUTES` in your local `.env` and GitHub Actions variables. The `notes` column records the baseline, actual pipeline runtime, and estimated processing reduction.

## Quick start

1. Create a Google Sheet with tabs named `Raw_SKU_Data`, `Action_Exceptions`, and `System_Run_Log`.
2. Copy `data/sample_raw_sku_data.csv` into `Raw_SKU_Data`.
3. Add these `System_Run_Log` headers: `timestamp_utc`, `status`, `rows_processed`, `exceptions_found`, `runtime_sec`, `notes`.
4. Open **Extensions -> Apps Script** in the Google Sheet, deploy the token-authenticated Web App (`doGet` / `doPost`), and copy the `/exec` Web App URL.
5. Copy `.env.example` to `.env`, add local configuration, then run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main
```

6. Add the repository secrets listed below, trigger the GitHub Actions workflow manually, and confirm the Sheet updates.

## GitHub Actions secrets

Add these under **Settings -> Secrets and variables -> Actions**:

| Secret | Purpose |
| --- | --- |
| `SHEET_ID` | Google Sheet ID |
| `SHEET_URL` | Direct link to the `Action_Exceptions` tab for email alerts |
| `APPS_SCRIPT_WEBHOOK_URL` | Deployed Google Apps Script Web App `/exec` URL |
| `APPS_SCRIPT_TOKEN` | Shared authentication token for the Apps Script endpoint |
| `GMAIL_USER` | Gmail sender address |
| `GMAIL_APP_PASSWORD` | Gmail App Password |
| `ALERT_RECIPIENT` | Alert recipient address |

Add `BASELINE_MANUAL_REVIEW_MINUTES` as an Actions **variable** (not a secret) after measuring the average manual-review time.

The workflow is in `.github/workflows/daily_sentinel.yml`. It supports a daily scheduled run and manual dispatch.

## Project structure

```text
src/analyzer.py        Inventory and margin business rules
src/sheets_client.py   Google Sheets client (Apps Script REST bridge)
src/notifier.py        Email alerts
src/main.py            Pipeline entry point
data/                   Generic sample data
.github/workflows/     GitHub Actions schedule
```

## Security

- Do not commit `.env`, Gmail App Passwords, webhook tokens, or private Google Sheet URLs.
- Run `git status --ignored` before pushing and confirm secret files are ignored.
- If a token or credential is ever exposed, revoke and rotate it immediately.
