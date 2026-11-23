# E-commerce SKU Sentinel

Python automation that replaces a manual e-commerce SKU review with a scheduled inventory and margin-risk check.

It reads a Google Sheet, calculates stock coverage and unit net margin, writes only actionable SKUs to an exception queue, records each run, and sends an email alert with a direct link to the exception queue when action is needed.

> The repository uses generic sample data only. No client, product, credential, or private Google Sheet ID is included.

Inventory planning is often a manual review of a spreadsheet. This automation turns that review into a repeatable daily process: it applies defined business rules, records what happened, and alerts a reviewer only when a SKU needs attention.

**Status:** Live scheduled automation — verified via local execution and GitHub Actions (processes 10 SKUs and flags 5 exceptions in no more than 1 minute per run vs. a 15-minute manual review baseline).

## What it replaces

**Before:** An operator manually reviews a SKU spreadsheet, estimates days of stock remaining, checks unit margin after platform fees and ad spend, prepares an action list, and sends follow-up messages.

**After:** A scheduled Python run applies the same rules consistently, populates an `Action_Exceptions` queue, logs execution and time-savings metrics in `System_Run_Log`, and emails an actionable digest with a direct link to the review tab.

## How it works

```text
Raw_SKU_Data (Google Sheets via Apps Script Web App REST Bridge)
        -> Python validation and calculations
        -> Action_Exceptions + System_Run_Log
        -> Email alert with clickable Action_Exceptions link
```

### Rules

| Signal | Rule | Output |
| --- | --- | --- |
| Stockout risk | `days_of_supply <= lead_time_days + safety_stock_days` | `REORDER NOW` |
| Margin risk | `net_margin_pct < 15` | `LOW MARGIN AUDIT` |
| Both risks | Both rules match | `REORDER + LOW MARGIN` |
| Zero sales | `units_sold_30d = 0` | Uses `days_of_supply = 999` without division by zero |

## Tools used

- **Python:** data validation, inventory velocity & unit-economics calculations, orchestration, and alerts
- **pandas:** SKU data processing
- **Google Apps Script Web App + requests:** token-authenticated JSON REST bridge for serverless Google Sheets reads and writes
- **Gmail SMTP:** exception digest and failure notifications
- **GitHub Actions:** daily cron schedule (`07:00 UTC`) and manual workflow dispatch
- **Git + VS Code:** version control and development

## Time-savings measurement

Time savings are measured and logged on every successful run against an operator's baseline manual review time.

| Measure | Before automation | After automation |
| --- | ---: | ---: |
| Manual SKU-review minutes per run | `15.00` min (baseline) | `~0.05` min pipeline runtime (+ exception review) |
| Runs per month | `30` runs | `30` scheduled runs |
| Monthly hours | `(minutes x runs) / 60` | `(minutes x runs) / 60` |

`hours_saved_per_month = manual_monthly_hours - automated_monthly_hours`

Setting `BASELINE_MANUAL_REVIEW_MINUTES` in `.env` and GitHub Actions variables automatically writes the baseline, actual pipeline runtime, and estimated processing reduction into the `notes` column of `System_Run_Log`.

## Quick start

1. Create a Google Sheet with tabs named `Raw_SKU_Data`, `Action_Exceptions`, and `System_Run_Log`.
2. Copy `data/sample_raw_sku_data.csv` into `Raw_SKU_Data`.
3. Add these `System_Run_Log` headers: `timestamp_utc`, `status`, `rows_processed`, `exceptions_found`, `runtime_sec`, `notes`.
4. Open **Extensions -> Apps Script** in the Google Sheet, deploy the token-authenticated Web App (`doGet` / `doPost`) with access set to **Anyone**, and copy the `/exec` Web App URL.
5. Copy `.env.example` to `.env`, fill in your local values, then run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.main
```

6. Add the repository secrets listed below, trigger the GitHub Actions workflow manually, and confirm the Sheet updates.

## GitHub Actions secrets

Add these under **Settings -> Secrets and variables -> Actions -> Secrets**:

| Secret | Purpose |
| --- | --- |
| `SHEET_ID` | Google Sheet ID |
| `SHEET_URL` | Direct URL to the `Action_Exceptions` tab for email alerts |
| `APPS_SCRIPT_WEBHOOK_URL` | Deployed Google Apps Script Web App `/exec` URL |
| `APPS_SCRIPT_TOKEN` | Shared authentication token for the Apps Script endpoint |
| `GMAIL_USER` | Gmail sender address |
| `GMAIL_APP_PASSWORD` | Gmail App Password |
| `ALERT_RECIPIENT` | Alert recipient address |

Add `BASELINE_MANUAL_REVIEW_MINUTES` as an Actions **variable** (not a secret) under the **Variables** tab.

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
