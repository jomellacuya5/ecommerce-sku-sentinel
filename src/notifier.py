"""Email alerts for successful exception runs and failures."""

from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

import pandas as pd


def _send_email(subject: str, body: str) -> None:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = os.environ["GMAIL_USER"]
    message["To"] = os.environ["ALERT_RECIPIENT"]
    message.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(os.environ["GMAIL_USER"], os.environ["GMAIL_APP_PASSWORD"])
        server.send_message(message)


def send_exception_digest(exceptions: pd.DataFrame, sheet_url: str) -> None:
    lines = [f"{len(exceptions)} SKU exception(s) found.", ""]
    for _, row in exceptions.iterrows():
        lines.append(
            f"- {row['sku_id']} | {row['product_name']} | {row['status']} | "
            f"days supply: {row['days_of_supply']:.1f} | margin: {row['net_margin_pct']:.1f}%"
        )
    lines.extend(["", f"Review the Action_Exceptions tab: {sheet_url}"])
    _send_email("SKU Sentinel: action required", "\n".join(lines))


def send_failure_alert(error_traceback: str) -> None:
    _send_email("SKU Sentinel: pipeline failed", f"The SKU Sentinel failed.\n\n{error_traceback}")
