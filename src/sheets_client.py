"""Google Sheets access helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

RAW_TAB = "Raw_SKU_Data"
EXCEPTIONS_TAB = "Action_Exceptions"
RUN_LOG_TAB = "System_Run_Log"
SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class SheetsClient:
    """Thin client for the three-tab Sentinel workbook."""

    def __init__(self, sheet_id: str, credentials_json: str | None = None) -> None:
        self._spreadsheet = gspread.authorize(self._load_credentials(credentials_json)).open_by_key(sheet_id)

    @staticmethod
    def _load_credentials(credentials_json: str | None) -> Credentials:
        if credentials_json:
            return Credentials.from_service_account_info(json.loads(credentials_json), scopes=SHEETS_SCOPES)
        path = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
        if not path.is_file():
            raise FileNotFoundError(f"Google credentials file not found: {path}")
        return Credentials.from_service_account_file(path, scopes=SHEETS_SCOPES)

    @property
    def url(self) -> str:
        return self._spreadsheet.url

    def read_raw_data(self) -> pd.DataFrame:
        return pd.DataFrame(self._spreadsheet.worksheet(RAW_TAB).get_all_records())

    def replace_exceptions(self, exceptions: pd.DataFrame) -> None:
        worksheet = self._spreadsheet.worksheet(EXCEPTIONS_TAB)
        worksheet.clear()
        worksheet.update([exceptions.columns.tolist()] + exceptions.fillna("").values.tolist(), "A1")

    def append_run_log(
        self, timestamp_utc: str, status: str, rows_processed: int, exceptions_found: int,
        runtime_sec: float, notes: str,
    ) -> None:
        self._spreadsheet.worksheet(RUN_LOG_TAB).append_row(
            [timestamp_utc, status, rows_processed, exceptions_found, round(runtime_sec, 2), notes],
            value_input_option="USER_ENTERED",
        )
