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


def build_success_notes(runtime_seconds: float) -> str:
    """Create an auditable runtime note without overstating human time savings."""
    notes = "Pipeline completed"
    baseline_minutes = os.getenv("BASELINE_MANUAL_REVIEW_MINUTES", "").strip()
    if not baseline_minutes:
        return notes

    try:
        baseline_value = float(baseline_minutes)
    except ValueError as error:
        raise ValueError("BASELINE_MANUAL_REVIEW_MINUTES must be a number of minutes") from error
    if baseline_value < 0:
        raise ValueError("BASELINE_MANUAL_REVIEW_MINUTES cannot be negative")

    runtime_minutes = runtime_seconds / 60
    estimated_processing_reduction = max(0, baseline_value - runtime_minutes)
    return (
        f"{notes}; baseline_manual_review_min={baseline_value:.2f}; "
        f"automation_runtime_min={runtime_minutes:.2f}; "
        f"estimated_processing_reduction_min={estimated_processing_reduction:.2f}"
    )


def main() -> None:
    load_dotenv()
    started_at = time.perf_counter()
    timestamp = datetime.now(timezone.utc).isoformat()
    client: SheetsClient | None = None
    rows_processed = 0
    try:
        client = SheetsClient(
            os.environ["SHEET_ID"],
            os.environ["APPS_SCRIPT_WEBHOOK_URL"],
            os.getenv("APPS_SCRIPT_TOKEN", "sentinel_secret_2026"),
        )
        raw_data = client.read_raw_data()
        rows_processed = len(raw_data)
        exceptions = analyze_skus(raw_data)
        client.replace_exceptions(exceptions)
        runtime_seconds = time.perf_counter() - started_at
        client.append_run_log(
            timestamp,
            "SUCCESS",
            rows_processed,
            len(exceptions),
            runtime_seconds,
            build_success_notes(runtime_seconds),
        )
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
