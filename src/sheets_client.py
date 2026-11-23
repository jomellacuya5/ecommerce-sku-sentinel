"""Google Sheets access helpers via Apps Script Web App bridge."""

from __future__ import annotations

import os
from urllib.parse import urljoin

import pandas as pd
import requests


class SheetsClient:
    """Thin client for the three-tab Sentinel workbook via Apps Script REST API."""

    def __init__(self, sheet_id: str, webhook_url: str | None = None, token: str | None = None) -> None:
        self._sheet_id = sheet_id
        self._webhook_url = webhook_url or os.environ["APPS_SCRIPT_WEBHOOK_URL"]
        self._token = token or os.getenv("APPS_SCRIPT_TOKEN", "sentinel_secret_2026")

    @property
    def url(self) -> str:
        return os.getenv("SHEET_URL", f"Sheet ID: {self._sheet_id}")

    def read_raw_data(self) -> pd.DataFrame:
        resp = requests.get(
            self._webhook_url,
            params={"token": self._token},
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            raise PermissionError(f"Apps Script error: {payload['error']}")
        return pd.DataFrame(payload["data"])

    def replace_exceptions(self, exceptions: pd.DataFrame) -> None:
        rows = [exceptions.columns.tolist()] + exceptions.fillna("").values.tolist()
        resp = requests.post(
            self._webhook_url,
            json={
                "token": self._token,
                "action": "replace_exceptions",
                "rows": rows,
            },
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") != "ok":
            raise RuntimeError(f"Failed to update Action_Exceptions: {payload}")

    def append_run_log(
        self,
        timestamp_utc: str,
        status: str,
        rows_processed: int,
        exceptions_found: int,
        runtime_sec: float,
        notes: str,
    ) -> None:
        resp = requests.post(
            self._webhook_url,
            json={
                "token": self._token,
                "action": "append_run_log",
                "row": [timestamp_utc, status, rows_processed, exceptions_found, round(runtime_sec, 2), notes],
            },
            timeout=20,
        )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") != "ok":
            raise RuntimeError(f"Failed to append System_Run_Log: {payload}")
