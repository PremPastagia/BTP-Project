#!/usr/bin/env python3
"""
01_extract_cng_panel.py
Phase 3A: Scrape historical discrete CNG price revisions, apply zero-order hold
calendar forward-fill, compute month-end price and TWAP, and store structured panels.
"""

import os
import sys
import json
import re
import logging
from datetime import datetime, timezone
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

# Base Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw", "cng_prices")
STRUCTURED_DIR = os.path.join(BASE_DIR, "structured", "price_revisions")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(STRUCTURED_DIR, exist_ok=True)

# City Gas Distributor (CGD) metadata and target geography
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.mypetrolprice.com/"
}

def fetch_city_revisions(city_meta):
    """
    Scrapes discrete price revision points from MyPetrolPrice historical serving endpoint.
    Includes retry logic and timeout.
    """
    city_name = city_meta["city"]
    loc_id = city_meta["location_id"]
    url = f"https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={loc_id}&Span=1000&selectedFuels=3H&HikeChartId=FuelHikeChartDetails"
    
    logger.info(f"Fetching raw discrete revisions for {city_name} (LocationId: {loc_id})...")
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 200:
                raw_text = resp.text
                
                # Save raw response for audit provenance
                raw_path = os.path.join(RAW_DIR, f"{city_meta['slug']}_raw_response.html")
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(raw_text)
                
                matches = re.findall(r"new Date\('([^']+)'\)\s*,\s*y:([\d.]+)", raw_text)
                if not matches:
                    logger.warning(f"No regex matches found for {city_name} on attempt {attempt}")
                    continue
                
                records = []
                now_utc = datetime.now(timezone.utc).isoformat()
                for dt_str, price_str in matches:
                    try:
                        # Format is like 'Oct 01 2011'
                        parsed_date = datetime.strptime(dt_str.strip(), "%b %d %Y").date()
                        records.append({
                            "city": city_name,
                            "state": city_meta["state"],
                            "cgd_operator": city_meta["operator"],
                            "effective_date": parsed_date.strftime("%Y-%m-%d"),
                            "observation_date": parsed_date.strftime("%Y-%m-%d"),
                            "publication_release_date": parsed_date.strftime("%Y-%m-%d"),
                            "cng_price": float(price_str),
                            "currency": "INR",
                            "unit": "INR/kg",
                            "source": "MyPetrolPrice / CGD Circulars",
                            "extraction_timestamp": now_utc
                        })
                    except Exception as parse_err:
                        logger.error(f"Error parsing date {dt_str}: {parse_err}")
                
                # Deduplicate and sort chronologically
                df = pd.DataFrame(records)
                df = df.drop_duplicates(subset=["effective_date"]).sort_values("effective_date").reset_index(drop=True)
                logger.info(f"Successfully extracted {len(df)} discrete revisions for {city_name}")
                return df
            else:
                logger.warning(f"HTTP {resp.status_code} for {city_name} on attempt {attempt}")
        except Exception as e:
            logger.error(f"Request failed for {city_name} (attempt {attempt}): {e}")
            
    raise RuntimeError(f"Failed to fetch data for city: {city_name} after {max_retries} attempts")


def compute_monthly_panel(city_meta, df_discrete):
    """
    Computes zero-order hold daily forward fill and calculates:
    - Month-End Price (cng_price_monthend)
    - Time-Weighted Average Price (cng_price_twap)
    """
    city_name = city_meta["city"]
    
    # Ensure datetime format
    df = df_discrete.copy()
    df["dt"] = pd.to_datetime(df["effective_date"])
    df = df.sort_values("dt").reset_index(drop=True)
    
    start_date = df["dt"].min()
    end_date = df["dt"].max()
    
    # Generate complete daily calendar index
    full_date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    daily_df = pd.DataFrame({"dt": full_date_range})
    
    # Merge discrete revisions onto calendar
    daily_df = pd.merge(daily_df, df[["dt", "cng_price"]], on="dt", how="left")
    
    # Forward-fill zero order hold
    daily_df["cng_price_ffill"] = daily_df["cng_price"].ffill()
    
    # Monthly aggregation
    daily_df["year_month"] = daily_df["dt"].dt.to_period("M")
    
    monthly_records = []
    now_utc = datetime.now(timezone.utc).isoformat()
    
    for ym, group in daily_df.groupby("year_month"):
        last_day = group["dt"].max()
        month_end_price = group.loc[group["dt"] == last_day, "cng_price_ffill"].values[0]
        twap_price = group["cng_price_ffill"].mean()
        revisions_count = group["cng_price"].dropna().count()
        min_p = group["cng_price_ffill"].min()
        max_p = group["cng_price_ffill"].max()
        
        monthly_records.append({
            "year_month": str(ym),
            "city": city_name,
            "state": city_meta["state"],
            "cgd_operator": city_meta["operator"],
            "cng_price_monthend": round(float(month_end_price), 2),
            "cng_price_twap": round(float(twap_price), 4),
            "revisions_in_month": int(revisions_count),
            "min_price_month": round(float(min_p), 2),
            "max_price_month": round(float(max_p), 2),
            "observation_date": last_day.strftime("%Y-%m-%d"),
            "publication_release_date": last_day.strftime("%Y-%m-%d"),
            "extraction_timestamp": now_utc
        })
        
    return pd.DataFrame(monthly_records)


def main():
    try:
        all_discrete = []
        all_monthly = []
        
        for city_meta in TARGET_CITIES:
            df_city_discrete = fetch_city_revisions(city_meta)
            all_discrete.append(df_city_discrete)
            
            df_city_monthly = compute_monthly_panel(city_meta, df_city_discrete)
            all_monthly.append(df_city_monthly)
            
        combined_discrete = pd.concat(all_discrete, ignore_index=True)
        combined_monthly = pd.concat(all_monthly, ignore_index=True)
        
        # Save discrete revisions
        discrete_parquet = os.path.join(STRUCTURED_DIR, "discrete_revisions.parquet")
        discrete_csv = os.path.join(STRUCTURED_DIR, "discrete_revisions.csv")
        combined_discrete.to_parquet(discrete_parquet, index=False)
        combined_discrete.to_csv(discrete_csv, index=False)
        
        # Save monthly panels
        monthly_parquet = os.path.join(STRUCTURED_DIR, "cng_monthly_panel.parquet")
        monthly_csv = os.path.join(STRUCTURED_DIR, "cng_monthly_panel.csv")
        combined_monthly.to_parquet(monthly_parquet, index=False)
        combined_monthly.to_csv(monthly_csv, index=False)
        
        # Determine overall dates
        min_date = combined_monthly["observation_date"].min()
        max_date = combined_monthly["observation_date"].max()
        rows, cols = combined_monthly.shape
        
        # Print strictly the 4-line verification receipt to stdout
        print(f"Target File Path: {monthly_parquet}")
        print(f"Total Rows & Columns Extracted: {rows} rows, {cols} columns")
        print(f"Date Coverage: {min_date} to {max_date}")
        print("Status: SUCCESS")
        
    except Exception as exc:
        logger.exception("Extraction failed.")
        print(f"Target File Path: {os.path.join(STRUCTURED_DIR, 'cng_monthly_panel.parquet')}")
        print("Total Rows & Columns Extracted: 0 rows, 0 columns")
        print("Date Coverage: None")
        print("Status: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
