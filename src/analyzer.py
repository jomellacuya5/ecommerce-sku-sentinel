"""Inventory and margin analysis for the SKU Sentinel."""

from __future__ import annotations

import math

import pandas as pd

REQUIRED_COLUMNS = [
    "sku_id", "product_name", "current_stock", "units_sold_30d", "lead_time_days",
    "safety_stock_days", "selling_price", "unit_cogs", "platform_fees", "ad_spend_per_unit",
]
NUMERIC_COLUMNS = [column for column in REQUIRED_COLUMNS if column not in {"sku_id", "product_name"}]
EXCEPTION_COLUMNS = REQUIRED_COLUMNS + [
    "daily_velocity", "days_of_supply", "reorder_threshold_days", "suggested_reorder_qty",
    "net_margin_pct", "status",
]


def analyze_skus(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Validate and analyze SKU data, returning only non-healthy rows."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in raw_data.columns]
    if missing_columns:
        raise ValueError(f"Raw_SKU_Data is missing required columns: {', '.join(missing_columns)}")

    data = raw_data.loc[:, REQUIRED_COLUMNS].copy()
    data["sku_id"] = data["sku_id"].astype(str).str.strip()
    data["product_name"] = data["product_name"].astype(str).str.strip()
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    invalid_rows = data[NUMERIC_COLUMNS].isna().any(axis=1)
    if invalid_rows.any():
        invalid_skus = ", ".join(data.loc[invalid_rows, "sku_id"].tolist())
        raise ValueError(f"Invalid numeric values for SKU(s): {invalid_skus}")
    if (data["current_stock"] < 0).any() or (data["units_sold_30d"] < 0).any():
        raise ValueError("current_stock and units_sold_30d cannot be negative")
    if (data["selling_price"] <= 0).any():
        raise ValueError("selling_price must be greater than zero")

    data["daily_velocity"] = data["units_sold_30d"] / 30
    data["days_of_supply"] = data.apply(
        lambda row: 999.0 if row["units_sold_30d"] == 0 else row["current_stock"] / row["daily_velocity"], axis=1
    )
    data["reorder_threshold_days"] = data["lead_time_days"] + data["safety_stock_days"]
    required_stock = data["daily_velocity"] * data["reorder_threshold_days"]
    data["suggested_reorder_qty"] = (required_stock - data["current_stock"]).clip(lower=0).apply(math.ceil)
    data["net_margin_pct"] = (
        (data["selling_price"] - data["unit_cogs"] - data["platform_fees"] - data["ad_spend_per_unit"])
        / data["selling_price"] * 100
    )

    reorder_needed = data["days_of_supply"] <= data["reorder_threshold_days"]
    low_margin = data["net_margin_pct"] < 15
    data["status"] = "HEALTHY"
    data.loc[reorder_needed & ~low_margin, "status"] = "REORDER NOW"
    data.loc[~reorder_needed & low_margin, "status"] = "LOW MARGIN AUDIT"
    data.loc[reorder_needed & low_margin, "status"] = "REORDER + LOW MARGIN"
    return data.loc[data["status"] != "HEALTHY", EXCEPTION_COLUMNS].reset_index(drop=True)
