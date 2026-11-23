# E-commerce SKU Sentinel

Automated Python pipeline that reads SKU data from Google Sheets, flags stockout risks and net-margin erosion, updates an action tab, logs every run, and emails alerts.

## Safety first

- This repository includes **generic sample data only**.
- Do not commit `credentials.json`, `.env`, Gmail app passwords, or copied Google Sheet URLs containing sensitive data. The included `.gitignore` excludes local credential files.
- Keep the repository public only while its contents are safe for public viewing.

## Create the Google Sheet

1. Create `Ecommerce_SKU_Sentinel_Demo` with tabs named exactly `Raw_SKU_Data`, `Action_Exceptions`, and `System_Run_Log`.
2. Copy the header and ten rows from `data/sample_raw_sku_data.csv` into `Raw_SKU_Data` at A1.
3. Add this header row to `System_Run_Log`: `timestamp_utc, status, rows_processed, exceptions_found, runtime_sec, notes`.
4. Leave `Action_Exceptions` empty. The first run supplies its headers.

## Google Cloud setup

1. Create a Google Cloud project and enable **Google Sheets API** and **Google Drive API**.
2. Create a service account and download its JSON key as `credentials.json` in the repository root.
3. Copy the `client_email` from that file and share the spreadsheet with it as **Editor**.
4. Copy `.env.example` to `.env`, set `SHEET_ID` from the spreadsheet URL, and fill the email settings.

## Local setup in VS Code

Open this folder in VS Code, then use its integrated terminal:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.main
```

On Windows PowerShell, activate with `venv\Scripts\Activate.ps1` and copy with `Copy-Item .env.example .env`.

## Rules implemented

- Missing required columns or invalid numeric values stop the run.
- A SKU with zero sales receives `days_of_supply = 999`; no division by zero occurs.
- `days_of_supply <= lead_time_days + safety_stock_days` triggers reorder risk.
- Net margin below 15% triggers a margin audit.
- Every non-healthy SKU is written to `Action_Exceptions`.

## GitHub Actions secrets

Under **Settings → Secrets and variables → Actions**, add:

| Secret | Value |
| --- | --- |
| `GOOGLE_CREDENTIALS_JSON` | Entire contents of local `credentials.json` |
| `SHEET_ID` | Google Sheet ID only |
| `GMAIL_USER` | Gmail address used to send alerts |
| `GMAIL_APP_PASSWORD` | 16-character Gmail App Password |
| `ALERT_RECIPIENT` | Email address that receives alerts |

The workflow runs at 07:00 UTC daily and can be started manually from the Actions tab.

## Safe first push

Before pushing, run `git status --ignored` and confirm `.env` and `credentials.json` are ignored. Then run:

```bash
git init
git add README.md .gitignore .env.example requirements.txt src data .github
git commit -m "Add SKU Sentinel pipeline"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ecommerce-sku-sentinel.git
git push -u origin main
```

Never use `git add .` until you inspect `git status`. Explicitly staging only public files is safer.
