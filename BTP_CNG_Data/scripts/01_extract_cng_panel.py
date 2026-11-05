#!/usr/bin/env python3
"""
01_extract_cng_panel.py (Stage 3 Data Recovery Version)
Extracts historical CNG price data across 10 major Indian cities:
1. Distinguishes raw observation records from true discrete price revisions (Delta P != 0).
2. Preserves observation_date, effective_date, and publication_release_date with verification flags.
3. Excludes incomplete current month (November 2026) from the finalized target panel;
   quarantines/isolates provisional month-to-date data.
4. Computes zero-order hold calendar daily forward-fill and aggregates monthly targets:
   - Month-End Price (cng_price_monthend)
   - Time-Weighted Average Price (cng_price_twap)
"""

import os
import sys
import json
import re
import logging
from datetime import datetime, timezone, date
import requests
import pandas as pd
import numpy as np

# Configure Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "01_extract_cng_panel.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("extract_cng_panel")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw", "cng_prices")
STRUCTURED_DIR = os.path.join(BASE_DIR, "structured", "price_revisions")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(STRUCTURED_DIR, exist_ok=True)

# Cutoff date: do not include incomplete months in finalized modeling panels
FINALIZED_MONTH_CUTOFF = "2026-10"

TARGET_CITIES = [
    {
        "city": "Delhi",
        "slug": "delhi",
        "location_id": 2,
        "operator": "Indraprastha Gas Limited (IGL)",
        "state": "Delhi NCR"
    },
    {
        "city": "Mumbai",
        "slug": "mumbai",
        "location_id": 3,
        "operator": "Mahanagar Gas Limited (MGL)",
        "state": "Maharashtra"
    },
    {
        "city": "Pune",
        "slug": "pune",
        "location_id": 7,
        "operator": "Maharashtra Natural Gas Limited (MNGL)",
        "state": "Maharashtra"
    },
    {
        "city": "Ahmedabad",
        "slug": "ahmedabad",
        "location_id": 10,
        "operator": "Adani Total Gas Limited (ATGL)",
        "state": "Gujarat"
    },
    {
        "city": "Lucknow",
        "slug": "lucknow",
        "location_id": 25,
        "operator": "Green Gas Limited (GGL)",
        "state": "Uttar Pradesh"
    },
    {
        "city": "Kanpur",
        "slug": "kanpur",
        "location_id": 292,
        "operator": "Central U.P. Gas Limited (CUGL)",
        "state": "Uttar Pradesh"
    },
    {
        "city": "Hyderabad",
        "slug": "hyderabad",
        "location_id": 8,
        "operator": "Bhagyanagar Gas Limited (BGL)",
        "state": "Telangana"
    },
    {
        "city": "Bengaluru",
        "slug": "bengaluru",
        "location_id": 6,
        "operator": "GAIL Gas Limited",
        "state": "Karnataka"
    },
    {
        "city": "Noida",
        "slug": "noida",
        "location_id": 38,
        "operator": "Indraprastha Gas Limited (IGL)",
        "state": "Uttar Pradesh"
    },
    {
        "city": "Gurgaon",
        "slug": "gurgaon",
        "location_id": 40,
        "operator": "Haryana City Gas / IGL",
        "state": "Haryana"
    }
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.mypetrolprice.com/"
}

def fetch_city_observations(city_meta):
    """
    Extracts all discrete observation points for a target city.
    Distinguishes raw observation points from true price changes.
    """
    city_name = city_meta["city"]
    loc_id = city_meta["location_id"]
    raw_path = os.path.join(RAW_DIR, f"{city_meta['slug']}_raw_response.html")
    
    raw_text = None
    if os.path.exists(raw_path):
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
            
    if not raw_text or "new Date" not in raw_text:
        url = f"https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={loc_id}&Span=1000&selectedFuels=3H&HikeChartId=FuelHikeChartDetails"
        logger.info(f"Downloading raw data for {city_name} (LocationId {loc_id})...")
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            raw_text = r.text
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
        else:
            raise RuntimeError(f"HTTP {r.status_code} fetching data for {city_name}")
            
    matches = re.findall(r"new Date\('([^']+)'\)\s*,\s*y:([\d.]+)", raw_text)
    if not matches:
        raise ValueError(f"No date/price regex matches found for {city_name}")
        
    now_utc = datetime.now(timezone.utc).isoformat()
    obs_records = []
    
    for dt_str, price_str in matches:
        try:
            parsed_date = datetime.strptime(dt_str.strip(), "%b %d %Y").date()
            obs_records.append({
                "city": city_name,
                "state": city_meta["state"],
                "cgd_operator": city_meta["operator"],
                "observation_date": parsed_date.strftime("%Y-%m-%d"),
                "effective_date": parsed_date.strftime("%Y-%m-%d"),
                # Explicitly flag that publication date is an unverified proxy from distributor feed
                "publication_release_date": parsed_date.strftime("%Y-%m-%d"),
                "publication_verification_status": "unverified_distributor_feed_timestamp",
                "cng_price": float(price_str),
                "currency": "INR",
                "unit": "INR/kg",
                "source_id": "SRC-03",
                "source_name": "MyPetrolPrice / CGD Circulars",
                "extraction_timestamp": now_utc
            })
        except Exception as e:
            logger.error(f"Error parsing date {dt_str} for {city_name}: {e}")
            
    df_obs = pd.DataFrame(obs_records).drop_duplicates(subset=["observation_date"]).sort_values("observation_date").reset_index(drop=True)
    
    # Calculate price change and true revisions
    df_obs["prev_price"] = df_obs["cng_price"].shift(1)
    df_obs["price_change_inr"] = df_obs["cng_price"] - df_obs["prev_price"]
    
    # Flag true revisions: initial baseline or price difference != 0
    is_rev = []
    rev_type = []
    for idx, row in df_obs.iterrows():
        if pd.isna(row["prev_price"]):
            is_rev.append(True)
            rev_type.append("initial_baseline")
        elif abs(row["price_change_inr"]) > 0.001:
            is_rev.append(True)
            if row["price_change_inr"] > 0:
                rev_type.append("price_hike")
            else:
                rev_type.append("price_cut")
        else:
            is_rev.append(False)
            rev_type.append("observation_hold")
            
    df_obs["is_price_revision"] = is_rev
    df_obs["revision_type"] = rev_type
    
    # Days since last actual revision
    days_since = [np.nan]
    last_rev_dt = datetime.strptime(df_obs.iloc[0]["effective_date"], "%Y-%m-%d").date()
    for idx in range(1, len(df_obs)):
        curr_dt = datetime.strptime(df_obs.iloc[idx]["effective_date"], "%Y-%m-%d").date()
        days_since.append((curr_dt - last_rev_dt).days)
        if df_obs.iloc[idx]["is_price_revision"]:
            last_rev_dt = curr_dt
    df_obs["days_since_last_revision"] = days_since
    
    true_rev_count = df_obs["is_price_revision"].sum()
    logger.info(f"{city_name}: {len(df_obs)} observation records, {true_rev_count} true price revisions.")
    
    return df_obs


def compute_monthly_panel(city_meta, df_obs):
    """
    Computes zero-order hold daily forward fill and monthly aggregation.
    Separates finalized full months (up to 2026-10) from provisional partial months (2026-11).
    """
    city_name = city_meta["city"]
    df = df_obs.copy()
    df["dt"] = pd.to_datetime(df["observation_date"])
    df = df.sort_values("dt").reset_index(drop=True)
    
    start_date = df["dt"].min()
    end_date = df["dt"].max()
    
    full_calendar = pd.date_range(start=start_date, end=end_date, freq="D")
    daily_df = pd.DataFrame({"dt": full_calendar})
    daily_df = pd.merge(daily_df, df[["dt", "cng_price", "is_price_revision"]], on="dt", how="left")
    
    daily_df["cng_price_ffill"] = daily_df["cng_price"].ffill()
    daily_df["year_month"] = daily_df["dt"].dt.to_period("M")
    
    now_utc = datetime.now(timezone.utc).isoformat()
    monthly_finalized = []
    monthly_provisional = []
    
    for ym, group in daily_df.groupby("year_month"):
        ym_str = str(ym)
        last_day = group["dt"].max()
        days_in_sample = len(group)
        # Expected calendar days in this month
        days_in_month = (group["dt"].iloc[0] + pd.offsets.MonthEnd(1)).day
        is_complete = (days_in_sample == days_in_month) and (ym_str <= FINALIZED_MONTH_CUTOFF)
        
        month_end_price = group.loc[group["dt"] == last_day, "cng_price_ffill"].values[0]
        twap_price = group["cng_price_ffill"].mean()
        actual_revisions = group["is_price_revision"].sum()
        min_p = group["cng_price_ffill"].min()
        max_p = group["cng_price_ffill"].max()
        
        record = {
            "year_month": ym_str,
            "city": city_name,
            "state": city_meta["state"],
            "cgd_operator": city_meta["operator"],
            "cng_price_monthend": round(float(month_end_price), 2),
            "cng_price_twap": round(float(twap_price), 4),
            "revisions_in_month": int(actual_revisions),
            "min_price_month": round(float(min_p), 2),
            "max_price_month": round(float(max_p), 2),
            "days_in_month": int(days_in_month),
            "days_observed": int(days_in_sample),
            "is_complete_month": bool(is_complete),
            "target_status": "finalized_complete" if is_complete else "provisional_month_to_date",
            "observation_date": last_day.strftime("%Y-%m-%d"),
            "publication_release_date": last_day.strftime("%Y-%m-%d"),
            "publication_verification_status": "unverified_feed_proxy",
            "extraction_timestamp": now_utc
        }
        
        if is_complete:
            monthly_finalized.append(record)
        else:
            monthly_provisional.append(record)
            
    return pd.DataFrame(monthly_finalized), pd.DataFrame(monthly_provisional)


def main():
    try:
        all_obs = []
        all_final_monthly = []
        all_prov_monthly = []
        
        for city_meta in TARGET_CITIES:
            df_city_obs = fetch_city_observations(city_meta)
            all_obs.append(df_city_obs)
            
            df_city_final, df_city_prov = compute_monthly_panel(city_meta, df_city_obs)
            all_final_monthly.append(df_city_final)
            all_prov_monthly.append(df_city_prov)
            
        combined_obs = pd.concat(all_obs, ignore_index=True)
        combined_revs = combined_obs[combined_obs["is_price_revision"] == True].reset_index(drop=True)
        combined_monthly = pd.concat(all_final_monthly, ignore_index=True)
        combined_provisional = pd.concat(all_prov_monthly, ignore_index=True)
        
        # 1. Save all discrete observations
        obs_parquet = os.path.join(STRUCTURED_DIR, "discrete_observations.parquet")
        obs_csv = os.path.join(STRUCTURED_DIR, "discrete_observations.csv")
        combined_obs.to_parquet(obs_parquet, index=False)
        combined_obs.to_csv(obs_csv, index=False)
        
        # 2. Save strictly true discrete revisions
        rev_parquet = os.path.join(STRUCTURED_DIR, "discrete_revisions.parquet")
        rev_csv = os.path.join(STRUCTURED_DIR, "discrete_revisions.csv")
        combined_revs.to_parquet(rev_parquet, index=False)
        combined_revs.to_csv(rev_csv, index=False)
        
        # 3. Save finalized monthly panel (up to 2026-10)
        monthly_parquet = os.path.join(STRUCTURED_DIR, "cng_monthly_panel.parquet")
        monthly_csv = os.path.join(STRUCTURED_DIR, "cng_monthly_panel.csv")
        combined_monthly.to_parquet(monthly_parquet, index=False)
        combined_monthly.to_csv(monthly_csv, index=False)
        
        # 4. Save provisional partial month
        prov_parquet = os.path.join(STRUCTURED_DIR, "cng_monthly_provisional.parquet")
        prov_csv = os.path.join(STRUCTURED_DIR, "cng_monthly_provisional.csv")
        combined_provisional.to_parquet(prov_parquet, index=False)
        combined_provisional.to_csv(prov_csv, index=False)
        
        min_date = combined_monthly["observation_date"].min()
        max_date = combined_monthly["observation_date"].max()
        rows, cols = combined_monthly.shape
        
        print(f"Target File Path: {monthly_parquet}")
        print(f"Total Rows & Columns Extracted: {rows} rows, {cols} columns (10 cities)")
        print(f"Date Coverage: {min_date} to {max_date} (True revisions: {len(combined_revs)}, Observations: {len(combined_obs)})")
        print("Status: SUCCESS")
        
    except Exception as exc:
        logger.exception("Failed to extract CNG panel.")
        print(f"Target File Path: {os.path.join(STRUCTURED_DIR, 'cng_monthly_panel.parquet')}")
        print("Total Rows & Columns Extracted: 0 rows, 0 columns")
        print("Date Coverage: None")
        print("Status: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
