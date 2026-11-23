# E-commerce SKU Sentinel

Portfolio automation that monitors e-commerce inventory and unit economics in Google Sheets. It identifies stockout risk and low-margin SKUs, writes an operational exception queue, logs each run, and emails stakeholders when action is needed.

## Why this project

Inventory planning is often a manual review of a spreadsheet. This automation turns that review into a repeatable daily process: it applies defined business rules, records what happened, and alerts a reviewer only when a SKU needs attention.

**Status:** Portfolio demo. The repository contains generic sample data only. Mark it as a live automation only after completing the manual GitHub Actions run and confirming the Google Sheet updates.

## Workflow

```text
Google Sheet Raw_SKU_Data
        |
        v
Python validation and SKU analysis
        |
        +--> Action_Exceptions (action queue)
        +--> System_Run_Log (audit record)
        +--> Email digest or failure alert
```

## Business rules

| Signal | Rule | Result |
| --- | --- | --- |
| Stockout risk | `days_of_supply <= lead_time_days + safety_stock_days` | `REORDER NOW` |
| Margin risk | `net_margin_pct < 15` | `LOW MARGIN AUDIT` |
| Both risks | Both rules match | `REORDER + LOW MARGIN` |
| No sales | `units_sold_30d = 0` | `days_of_supply = 999` |

The pipeline rejects missing columns, invalid numeric values, negative stock or sales, and selling prices that are zero or below.

## Project structure

```text
src/analyzer.py        Validates data and calculates inventory and margin signals
src/sheets_client.py   Reads and writes the three Google Sheet tabs
src/notifier.py        Sends Gmail exception and failure alerts
src/main.py            Orchestrates the run, logging, and error handling
data/                  Generic sample data only
.github/workflows/     Scheduled GitHub Actions workflow
docs/                  Process discovery, runbook, and measurement templates
```

## Google Sheet schema

Create a spreadsheet with these tabs exactly:

### `Raw_SKU_Data`

Copy the ten generic rows from `data/sample_raw_sku_data.csv`. Required columns:

`sku_id`, `product_name`, `current_stock`, `units_sold_30d`, `lead_time_days`, `safety_stock_days`, `selling_price`, `unit_cogs`, `platform_fees`, `ad_spend_per_unit`

### `Action_Exceptions`

The pipeline replaces this tab on every successful run with:

`sku_id`, `product_name`, `flag_status`, `current_stock`, `daily_velocity`, `days_of_supply`, `reorder_threshold_days`, `suggested_reorder_qty`, `net_margin_pct`, `action_note`

### `System_Run_Log`

Add this header row before the first run:

`timestamp_utc`, `status`, `rows_processed`, `exceptions_found`, `runtime_sec`, `notes`

## Local setup

In the VS Code terminal:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.main
```

Add your real local settings only in `.env`. Put the downloaded Google service-account key in `credentials.json` at the repository root. Both files are ignored by Git.

## GitHub Actions setup

Add the following repository secrets under **Settings -> Secrets and variables -> Actions**:

| Secret | Value |
| --- | --- |
| `GOOGLE_CREDENTIALS_JSON` | Entire contents of local `credentials.json` |
| `SHEET_ID` | Google Sheet ID only |
| `GMAIL_USER` | Gmail address used to send alerts |
| `GMAIL_APP_PASSWORD` | 16-character Gmail App Password |
| `ALERT_RECIPIENT` | Address that receives alerts |

The workflow supports a daily scheduled run and a manual run from the GitHub Actions tab. See `docs/runbook.md` for verification and incident steps.

## Portfolio demonstration

After the live setup is verified, record a short screen demo:

1. Show the three Google Sheet tabs with only generic data.
2. Show the GitHub repository and `src/analyzer.py` business rules.
3. Trigger **Run workflow** in GitHub Actions.
4. Show the successful workflow run, the updated exception queue, and the new log row.
5. Show the safe failure behavior by describing the `FAILED` log and alert path; do not expose credentials.

Use the measurement template in `docs/measurement.md` to state the time saved truthfully. Do not publish client data, credentials, sheet IDs, or email addresses.

## Operating documentation

- `docs/process-discovery.md` — questions for the inventory or Amazon expert before automating.
- `docs/runbook.md` — setup checks, daily monitoring, and failure response.
- `docs/measurement.md` — baseline and post-automation time-savings calculation.

## Security

- This public repository contains generic sample data only.
- Never commit `.env`, `credentials.json`, Gmail app passwords, or Google Sheet IDs/URLs containing private client data.
- Check `git status --ignored` before every first push or credential change.
