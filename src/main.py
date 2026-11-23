"""Run the daily SKU Sentinel pipeline."""

from __future__ import annotations

import os
import time
import traceback
from datetime import datetime, timezone

from dotenv import load_dotenv

from src.analyzer import analyze_skus
from src.notifier import send_exception_digest, send_failure_alert
from src.sheets_client import SheetsClient


def main() -> None:
    load_dotenv()
    started_at = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()
    client: SheetsClient | None = None
    rows_processed = 0
    try:
        client = SheetsClient(os.environ["SHEET_ID"], os.getenv("GOOGLE_CREDENTIALS_JSON"))
        raw_data = client.read_raw_data()
        rows_processed = len(raw_data)
        exceptions = analyze_skus(raw_data)
        client.replace_exceptions(exceptions)
        client.append_run_log(timestamp, "SUCCESS", rows_processed, len(exceptions), time.perf_counter() - started_at, "Pipeline completed")
        if not exceptions.empty:
            send_exception_digest(exceptions, client.url)
        print(f"SUCCESS: processed {rows_processed} rows; found {len(exceptions)} exceptions")
    except Exception:
        error_traceback = traceback.format_exc()
        print(error_traceback)
        if client is not None:
            try:
                client.append_run_log(timestamp, "FAILED", rows_processed, 0, time.perf_counter() - started_at, error_traceback[-4000:])
            except Exception:
                print("Could not write failure log to Google Sheets.")
        try:
            send_failure_alert(error_traceback)
        except Exception:
            print("Could not send failure email.")
        raise


if __name__ == "__main__":
    main()
