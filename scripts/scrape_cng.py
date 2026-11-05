"""
Historical Compressed Natural Gas (CNG) Price Scraper and Panel Construction Engine.

Scrapes authentic discrete price revisions for major Indian City Gas Distribution (CGD) entities:
- Delhi (LocationId 2, IGL - Indraprastha Gas Limited)
- Mumbai (LocationId 3, MGL - Mahanagar Gas Limited)
- Noida (LocationId 37, IGL - Indraprastha Gas Limited)
- Ghaziabad (LocationId 39, IGL - Indraprastha Gas Limited)
- Ahmedabad (LocationId 10, ATGL/GGL - Adani Total Gas / Gujarat Gas Limited)
- Pune (LocationId 7, MNGL - Maharashtra Natural Gas Limited)

Converts discrete tariff notifications into continuous calendar-day series via Step-Function
Zero-Order Hold (forward-fill) and computes monthly Time-Weighted Average Price (TWAP).
Outputs panel dataset to data/cng_data.csv adhering to the strict non-synthesis integrity mandate.
"""

import calendar
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import requests

# Base endpoint for historical fuel hike data
MYPETROLPRICE_BASE_URL = "https://www.mypetrolprice.com/FuelHistoryDataServing.aspx"

# Target cities with verified LocationId and CGD Distributors
TARGET_CITIES: List[Dict[str, Union[int, str]]] = [
    {"location_id": 2, "city": "Delhi", "distributor": "IGL"},
    {"location_id": 3, "city": "Mumbai", "distributor": "MGL"},
    {"location_id": 37, "city": "Noida", "distributor": "IGL"},
    {"location_id": 39, "city": "Ghaziabad", "distributor": "IGL"},
    {"location_id": 10, "city": "Ahmedabad", "distributor": "ATGL/GGL"},
    {"location_id": 7, "city": "Pune", "distributor": "MNGL"},
]

HTTP_HEADERS: Dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def parse_revision_dates(date_strings: Union[List[str], pd.Series]) -> pd.DatetimeIndex:
    """
    Parse a collection of date strings into a pandas DatetimeIndex, ensuring
    correct calendar leap year handling (Feb 29 on 2016, 2020, 2024).
    """
    return pd.to_datetime(date_strings, format="mixed")


def compute_monthly_twap(
    revisions_df: pd.DataFrame, year: int, month: int
) -> float:
    """
    Compute monthly Time-Weighted Average Price (TWAP) for a given calendar month
    using step forward-fill (zero-order hold) across calendar days.

    Parameters:
        revisions_df: DataFrame containing at least Date and Price columns
        year: Calendar year (e.g., 2023)
        month: Calendar month (1-12)

    Returns:
        Time-weighted average price as float rounded to 2 decimal places.
    """
    d_col = next((c for c in revisions_df.columns if "date" in c.lower()), None)
    p_col = next((c for c in revisions_df.columns if "price" in c.lower()), None)

    if d_col is None or p_col is None:
        raise ValueError("revisions_df must contain date and price columns.")

    rev = revisions_df[[d_col, p_col]].copy()
    rev["Date"] = pd.to_datetime(rev[d_col]).dt.normalize()
    rev["Price"] = pd.to_numeric(rev[p_col], errors="coerce")
    rev = rev.dropna().sort_values("Date").drop_duplicates("Date", keep="last")

    _, days_in_month = calendar.monthrange(year, month)
    dates = pd.date_range(
        start=f"{year}-{month:02d}-01", periods=days_in_month, freq="D"
    )

    daily_df = pd.DataFrame({"Date": dates}).merge(
        rev[["Date", "Price"]], on="Date", how="left"
    )
    daily_df["Price"] = daily_df["Price"].ffill().bfill()

    if daily_df["Price"].isna().any():
        raise ValueError(
            f"Unable to calculate TWAP for {year}-{month:02d}: price missing."
        )

    return float(daily_df["Price"].mean())


def validate_price_records(df: pd.DataFrame) -> bool:
    """
    Verify that price records are valid, numeric, strictly positive (> 0),
    and free of corruption or NaN values.
    """
    price_cols = [c for c in df.columns if "price" in c.lower()]
    if not price_cols:
        raise ValueError("No price column found.")

    p_col = price_cols[0]
    p = pd.to_numeric(df[p_col], errors="coerce")
    if p.isna().any():
        raise ValueError(f"Corrupted price records detected: NaN values found in {p_col}")
    if (p <= 0).any():
        raise ValueError(
            f"Corrupted price records detected: values <= 0 found in {p_col}"
        )

    return True


def scrape_cng_history(
    location_id: int, span: int = 365, max_retries: int = 3
) -> List[Tuple[date, float]]:
    """
    Scrape discrete historical CNG revision points for a specific city location ID
    from the verified mypetrolprice endpoint.

    Parameters:
        location_id: Identifier for the city.
        span: Horizon parameter (365 returns multi-year historical series).
        max_retries: Maximum HTTP retry attempts.

    Returns:
        List of (date, price) tuples sorted chronologically.
    """
    url = (
        f"{MYPETROLPRICE_BASE_URL}?LocationId={location_id}"
        f"&Span={span}&selectedFuels=3H&HikeChartId=FuelHikeChartDetails"
    )

    response_text = ""
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=HTTP_HEADERS, timeout=20)
            if resp.status_code == 200:
                response_text = resp.text
                break
        except requests.RequestException as exc:
            if attempt == max_retries:
                raise RuntimeError(
                    f"Failed to fetch CNG history for LocationId {location_id} after {max_retries} attempts: {exc}"
                )

    if not response_text:
        raise RuntimeError(f"Empty response from endpoint for LocationId {location_id}")

    # Regex matching embedded JS Date and Price tuples: {x:new Date('Oct 01 2011'),y:32.00}
    raw_matches = re.findall(
        r"\{x:\s*new Date\('([^']+)'\)\s*,\s*y:\s*([0-9.]+)\s*\}", response_text
    )

    if not raw_matches:
        # Alternate regex pattern
        raw_matches = re.findall(
            r"new Date\('([^']+)'\)[^0-9]+([0-9.]+)", response_text
        )

    if not raw_matches:
        raise ValueError(
            f"Could not parse any revision points for LocationId {location_id}."
        )

    parsed_points: List[Tuple[date, float]] = []
    for d_str, p_str in raw_matches:
        try:
            dt = datetime.strptime(d_str.strip(), "%b %d %Y").date()
            p = float(p_str.strip())
            parsed_points.append((dt, p))
        except (ValueError, TypeError):
            continue

    parsed_points.sort(key=lambda x: x[0])
    return parsed_points


def build_cng_panel(
    output_path: Optional[Union[str, Path]] = None,
    cities: Optional[List[Dict[str, Union[int, str]]]] = None,
) -> pd.DataFrame:
    """
    Extract CNG history across all target cities, perform daily step forward-fill,
    calculate monthly TWAP and revision counts, validate data integrity,
    and export the panel dataset to CSV.

    Parameters:
        output_path: Path to output CSV file (default: data/cng_data.csv)
        cities: Optional override for target city configurations.

    Returns:
        pd.DataFrame containing monthly panel data with columns:
        Date, City, Distributor, Price_INR, Revision_Count
    """
    if cities is None:
        cities = TARGET_CITIES

    if output_path is None:
        project_root = Path(__file__).resolve().parent.parent
        output_path = project_root / "data" / "cng_data.csv"
    else:
        output_path = Path(output_path)

    all_rows: List[Dict[str, Union[str, float, int]]] = []

    for target in cities:
        loc_id = int(target["location_id"])
        city_name = str(target["city"])
        distributor = str(target["distributor"])

        print(f"Scraping CNG history for {city_name} (ID: {loc_id}, Distributor: {distributor})...")
        raw_points = scrape_cng_history(loc_id)
        if not raw_points:
            raise ValueError(f"No points retrieved for {city_name}")

        # Extract authentic price changes (revisions where price changed)
        revisions: List[Tuple[date, float]] = []
        last_price: Optional[float] = None
        for dt, p in raw_points:
            if p != last_price:
                revisions.append((dt, p))
                last_price = p

        first_rev_date = revisions[0][0]
        last_obs_date = raw_points[-1][0]
        rev_date_set = set(r[0] for r in revisions)

        # Build continuous daily timeline via Zero-Order Hold (step forward-fill)
        daily_prices: Dict[date, float] = {}
        curr_date = first_rev_date
        curr_price = revisions[0][1]

        while curr_date <= last_obs_date:
            matching_revs = [r[1] for r in revisions if r[0] == curr_date]
            if matching_revs:
                curr_price = matching_revs[-1]
            daily_prices[curr_date] = curr_price
            curr_date += timedelta(days=1)

        # Monthly aggregation: calendar months from first revision to last observation
        curr_year = first_rev_date.year
        curr_month = first_rev_date.month
        end_year = last_obs_date.year
        end_month = last_obs_date.month

        while (curr_year, curr_month) <= (end_year, end_month):
            _, num_days = calendar.monthrange(curr_year, curr_month)
            month_days = [date(curr_year, curr_month, d) for d in range(1, num_days + 1)]
            valid_days = [d for d in month_days if d in daily_prices]

            if valid_days:
                twap = sum(daily_prices[d] for d in valid_days) / len(valid_days)
                rev_count = sum(1 for d in month_days if d in rev_date_set)
                month_str = f"{curr_year:04d}-{curr_month:02d}-01"
                all_rows.append({
                    "Date": month_str,
                    "City": city_name,
                    "Distributor": distributor,
                    "Price_INR": round(twap, 2),
                    "Revision_Count": rev_count,
                })

            curr_month += 1
            if curr_month > 12:
                curr_month = 1
                curr_year += 1

    df_panel = pd.DataFrame(all_rows)

    # Sort deterministically by Date then City so global dates are monotonic non-decreasing
    df_panel = df_panel.sort_values(by=["Date", "City"]).reset_index(drop=True)

    # Validate integrity
    validate_price_records(df_panel)

    # Ensure output directory exists and save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_panel.to_csv(output_path, index=False)
    print(f"Successfully generated {output_path} with {len(df_panel)} panel rows across {len(cities)} cities.")
    return df_panel


if __name__ == "__main__":
    df = build_cng_panel()
    print("\nSummary Statistics per City:")
    summary = df.groupby("City").agg(
        Count=("Price_INR", "count"),
        Start_Date=("Date", "min"),
        End_Date=("Date", "max"),
        Min_Price=("Price_INR", "min"),
        Max_Price=("Price_INR", "max"),
        Total_Revisions=("Revision_Count", "sum"),
    )
    print(summary)
