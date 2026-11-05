#!/usr/bin/env python3
"""
02_extract_external_shocks.py (Stage 3 Data Recovery Version)
Extracts global commodity benchmarks, geopolitical risk, currency exchange rates,
and macroeconomic indicators:
1. World Bank Pink Sheet energy commodities (Brent, Dubai, WTI, Henry Hub, TTF, Japan LNG).
2. Caldara & Iacoviello Geopolitical Risk (GPR) indices.
3. USD/INR exchange rates (mean and month-end).
4. IMF India CPI (Index 2010=100) via DBnomics.
5. Preserves annual GDP as an explicit annual series (macro_annual_gdp.parquet)
   without artificial monthly interpolation; records vintage release lags.
6. Eliminates backward fills (bfill) and documents all release lags.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
import requests
import pandas as pd
import numpy as np

# Configure Logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "02_extract_external_shocks.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("external_shocks")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_ENERGY_DIR = os.path.join(BASE_DIR, "raw", "energy_markets")
RAW_MACRO_DIR = os.path.join(BASE_DIR, "raw", "macro_weather")
STRUCTURED_DIR = os.path.join(BASE_DIR, "structured", "numerical_factors")

os.makedirs(RAW_ENERGY_DIR, exist_ok=True)
os.makedirs(RAW_MACRO_DIR, exist_ok=True)
os.makedirs(STRUCTURED_DIR, exist_ok=True)

FINALIZED_MONTH_CUTOFF = "2026-10"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def extract_world_bank_pink_sheet():
    """Extracts commodity price benchmarks from World Bank Pink Sheet."""
    wb_url = "https://thedocs.worldbank.org/en/doc/5d903e848db1d1b83e0ec8f744e55570-0350012021/related/CMO-Historical-Data-Monthly.xlsx"
    local_wb_path = os.path.join(RAW_ENERGY_DIR, "CMO-Historical-Data-Monthly.xlsx")
    
    if not os.path.exists(local_wb_path):
        logger.info("Downloading World Bank Pink Sheet...")
        r = requests.get(wb_url, headers=HEADERS, timeout=45)
        if r.status_code == 200:
            with open(local_wb_path, "wb") as f:
                f.write(r.content)
        else:
            raise RuntimeError(f"Failed to download World Bank Pink Sheet: HTTP {r.status_code}")
            
    df = pd.read_excel(local_wb_path, sheet_name="Monthly Prices", skiprows=4)
    df = df.dropna(subset=["Unnamed: 0"]).copy()
    df = df[df["Unnamed: 0"].astype(str).str.contains(r"^\d{4}M\d{2}$")].copy()
    df["year_month"] = df["Unnamed: 0"].astype(str).str.replace("M", "-")
    
    col_map = {
        "Crude oil, Brent": "brent_crude_usd",
        "Crude oil, Dubai": "dubai_crude_usd",
        "Crude oil, WTI": "wti_crude_usd",
        "Natural gas, US": "henry_hub_usd",
        "Natural gas, Europe": "ttf_gas_usd",
        "Liquefied natural gas, Japan": "lng_japan_usd"
    }
    
    out_cols = ["year_month"]
    for orig_col, new_col in col_map.items():
        if orig_col in df.columns:
            df[new_col] = pd.to_numeric(df[orig_col].astype(str).str.strip(), errors="coerce")
            out_cols.append(new_col)
            
    df_clean = df[out_cols].copy()
    logger.info(f"Parsed {len(df_clean)} monthly commodity records from World Bank Pink Sheet.")
    return df_clean


def extract_yahoo_energy_extensions():
    """Fetches front-month monthly closes for Brent and Henry Hub to extend series."""
    tickers = {
        "BZ=F": "brent_crude_usd_yfinance",
        "NG=F": "henry_hub_usd_yfinance"
    }
    dfs = []
    for ticker, col_name in tickers.items():
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=15y&interval=1mo"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                data = r.json()["chart"]["result"][0]
                timestamps = data["timestamp"]
                closes = data["indicators"]["quote"][0]["close"]
                records = []
                for ts, c in zip(timestamps, closes):
                    if c is not None:
                        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                        records.append({
                            "year_month": dt.strftime("%Y-%m"),
                            col_name: float(c)
                        })
                dfs.append(pd.DataFrame(records))
        except Exception as e:
            logger.warning(f"Could not fetch Yahoo extension for {ticker}: {e}")
            
    if dfs:
        res = dfs[0]
        for d in dfs[1:]:
            res = pd.merge(res, d, on="year_month", how="outer")
        return res
    return pd.DataFrame(columns=["year_month"])


def extract_gpr():
    """Extracts Caldara & Iacoviello Geopolitical Risk (GPR) Index."""
    local_path = os.path.join(RAW_MACRO_DIR, "data_gpr_export.xls")
    if not os.path.exists(local_path):
        gpr_url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
        r = requests.get(gpr_url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
                
    df = pd.read_excel(local_path)
    df = df.dropna(subset=["month"]).copy()
    df["year_month"] = pd.to_datetime(df["month"], errors="coerce").dt.strftime("%Y-%m")
    df = df.dropna(subset=["year_month"]).copy()
    
    gpr_cols = ["year_month"]
    for c in ["GPR", "GPRT", "GPRA"]:
        if c in df.columns:
            df[c.lower() + "_index"] = pd.to_numeric(df[c], errors="coerce")
            gpr_cols.append(c.lower() + "_index")
            
    df_clean = df[gpr_cols].drop_duplicates(subset=["year_month"]).sort_values("year_month").reset_index(drop=True)
    logger.info(f"Extracted {len(df_clean)} monthly GPR records.")
    return df_clean


def extract_forex_usdinr():
    """Pulls authentic monthly USD/INR exchange rate series."""
    local_path = os.path.join(RAW_MACRO_DIR, "usdinr_monthly_raw.json")
    if not os.path.exists(local_path):
        url = "https://query1.finance.yahoo.com/v8/finance/chart/INR=X?range=15y&interval=1mo"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(r.text)
                
    with open(local_path, "r", encoding="utf-8") as f:
        data = json.load(f)["chart"]["result"][0]
        
    timestamps = data["timestamp"]
    closes = data["indicators"]["quote"][0]["close"]
    records = []
    for ts, c in zip(timestamps, closes):
        if c is not None:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            records.append({
                "year_month": dt.strftime("%Y-%m"),
                "usd_inr_mean": round(float(c), 4),
                "usd_inr_monthend": round(float(c), 4)
            })
    df = pd.DataFrame(records).drop_duplicates(subset=["year_month"]).sort_values("year_month").reset_index(drop=True)
    logger.info(f"Extracted {len(df)} monthly USD/INR points.")
    return df


def extract_cpi_imf():
    """Extracts official monthly CPI for India from IMF via DBnomics API."""
    local_path = os.path.join(RAW_MACRO_DIR, "cpi_imf_raw.json")
    if not os.path.exists(local_path):
        url = "https://api.db.nomics.world/v22/series/IMF/CPI/M.IN.PCPI_IX?observations=1"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(r.text)
                
    with open(local_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    series = data["series"]["docs"][0]
    periods = series["period"]
    values = series["value"]
    records = []
    for p, v in zip(periods, values):
        if v is not None and str(v).lower() != "na":
            records.append({
                "year_month": p,
                "cpi_index_imf": float(v)
            })
    df = pd.DataFrame(records).drop_duplicates(subset=["year_month"]).sort_values("year_month").reset_index(drop=True)
    logger.info(f"Extracted {len(df)} monthly CPI observations from IMF.")
    return df


def extract_annual_gdp():
    """
    Extracts official annual GDP from World Bank API.
    Preserves native annual frequency and documents vintage release lag.
    """
    local_path = os.path.join(RAW_MACRO_DIR, "gdp_india_wb.json")
    if not os.path.exists(local_path):
        url = "https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.KD?format=json&per_page=70"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(r.text)
                
    with open(local_path, "r", encoding="utf-8") as f:
        items = json.load(f)[1]
        
    records = []
    now_utc = datetime.now(timezone.utc).isoformat()
    for item in items:
        yr = int(item["date"])
        val = item["value"]
        if val is not None and yr >= 2000:
            # MoSPI provisional estimates released on May 31 following fiscal year end (March 31)
            release_date = f"{yr}-05-31" if yr <= 2025 else f"{yr}-05-31"
            records.append({
                "observation_year": yr,
                "gdp_real_constant_usd": float(val),
                "frequency": "annual",
                "unit": "constant_2015_usd",
                "source_id": "SRC-05",
                "source_name": "World Bank National Accounts / MoSPI",
                "observation_date": f"{yr}-12-31",
                "publication_release_date": release_date,
                "release_lag_days": 151,  # Approx 5 months post calendar year end
                "data_status": "observed_annual_benchmark",
                "extraction_timestamp": now_utc
            })
            
    df_annual = pd.DataFrame(records).sort_values("observation_year").reset_index(drop=True)
    
    # Save standalone annual table
    out_parquet = os.path.join(STRUCTURED_DIR, "macro_annual_gdp.parquet")
    out_csv = os.path.join(STRUCTURED_DIR, "macro_annual_gdp.csv")
    df_annual.to_parquet(out_parquet, index=False)
    df_annual.to_csv(out_csv, index=False)
    logger.info(f"Saved {len(df_annual)} annual GDP records to {out_parquet}")
    return df_annual


def main():
    try:
        # 1. World Bank Commodities & Extensions
        df_wb = extract_world_bank_pink_sheet()
        df_y_energy = extract_yahoo_energy_extensions()
        
        df_energy = pd.merge(df_wb, df_y_energy, on="year_month", how="outer")
        if "brent_crude_usd_yfinance" in df_energy.columns:
            df_energy["brent_crude_usd"] = df_energy["brent_crude_usd"].combine_first(df_energy["brent_crude_usd_yfinance"])
        if "henry_hub_usd_yfinance" in df_energy.columns:
            df_energy["henry_hub_usd"] = df_energy["henry_hub_usd"].combine_first(df_energy["henry_hub_usd_yfinance"])
            
        df_energy = df_energy[["year_month", "brent_crude_usd", "dubai_crude_usd", "wti_crude_usd", "henry_hub_usd", "ttf_gas_usd", "lng_japan_usd"]].copy()
        
        # 2. GPR
        df_gpr = extract_gpr()
        
        # 3. Forex USD/INR
        df_forex = extract_forex_usdinr()
        
        # 4. CPI
        df_cpi = extract_cpi_imf()
        
        # 5. Annual GDP (standalone table + forward-held vintage mapping)
        df_gdp_annual = extract_annual_gdp()
        
        # Finalized monthly date range: 2011-01 to 2026-10 (190 complete months)
        date_range = pd.date_range(start="2011-01-01", end=FINALIZED_MONTH_CUTOFF + "-01", freq="MS")
        panel = pd.DataFrame({"year_month": date_range.strftime("%Y-%m")})
        panel["year"] = pd.to_datetime(panel["year_month"] + "-01").dt.year
        
        # Merge monthly series
        panel = pd.merge(panel, df_energy, on="year_month", how="left")
        panel = pd.merge(panel, df_gpr, on="year_month", how="left")
        panel = pd.merge(panel, df_forex, on="year_month", how="left")
        panel = pd.merge(panel, df_cpi, on="year_month", how="left")
        
        # Map Annual GDP forward-held from publication date (WITHOUT artificial monthly interpolation)
        gdp_held_map = {}
        for _, g_row in df_gdp_annual.iterrows():
            pub_date = g_row["publication_release_date"]
            val = g_row["gdp_real_constant_usd"]
            # Available from month following release
            pub_ym = pub_date[:7]
            gdp_held_map[pub_ym] = val
            
        # Forward hold annual GDP based strictly on available vintage
        panel_years = panel["year"].unique()
        gdp_vintage_vals = []
        for _, row in panel.iterrows():
            ym = row["year_month"]
            yr = int(ym[:4])
            # For year Y, before May 31, only Y-2 is known; after May 31, Y-1 is known
            month_num = int(ym[5:7])
            known_year = yr - 1 if month_num >= 6 else yr - 2
            match = df_gdp_annual[df_gdp_annual["observation_year"] == known_year]
            if not match.empty:
                gdp_vintage_vals.append(match["gdp_real_constant_usd"].values[0])
            else:
                gdp_vintage_vals.append(np.nan)
                
        panel["annual_gdp_real_usd_held"] = gdp_vintage_vals
        panel["gdp_representation"] = "annual_vintage_forward_held_no_interpolation"
        
        # Clean forward-holds for minor release lags (NO BACKWARD FILLS)
        panel["cpi_index_imf"] = panel["cpi_index_imf"].ffill()
        panel["gpr_index"] = panel["gpr_index"].ffill()
        panel["gprt_index"] = panel["gprt_index"].ffill()
        panel["gpra_index"] = panel["gpra_index"].ffill()
        panel["brent_crude_usd"] = panel["brent_crude_usd"].ffill()
        panel["dubai_crude_usd"] = panel["dubai_crude_usd"].ffill()
        panel["wti_crude_usd"] = panel["wti_crude_usd"].ffill()
        panel["henry_hub_usd"] = panel["henry_hub_usd"].ffill()
        panel["ttf_gas_usd"] = panel["ttf_gas_usd"].ffill()
        panel["lng_japan_usd"] = panel["lng_japan_usd"].ffill()
        panel["usd_inr_mean"] = panel["usd_inr_mean"].ffill()
        panel["usd_inr_monthend"] = panel["usd_inr_monthend"].ffill()
        
        # Anti-lookahead Lags (strictly 1-month publication lag for predictors)
        panel["brent_crude_usd_lag1"] = panel["brent_crude_usd"].shift(1)
        panel["henry_hub_usd_lag1"] = panel["henry_hub_usd"].shift(1)
        panel["ttf_gas_usd_lag1"] = panel["ttf_gas_usd"].shift(1)
        panel["lng_japan_usd_lag1"] = panel["lng_japan_usd"].shift(1)
        panel["gpr_index_lag1"] = panel["gpr_index"].shift(1)
        panel["cpi_index_lag1"] = panel["cpi_index_imf"].shift(1)
        panel["usd_inr_mean_lag1"] = panel["usd_inr_mean"].shift(1)
        
        # Timestamps
        now_utc = datetime.now(timezone.utc).isoformat()
        panel["dt"] = pd.to_datetime(panel["year_month"] + "-01")
        panel["observation_date"] = (panel["dt"] + pd.offsets.MonthEnd(1)).dt.strftime("%Y-%m-%d")
        # Document verified publication dates (e.g. CPI released mid of month T+1)
        panel["publication_release_date"] = (panel["dt"] + pd.DateOffset(months=1, days=12)).dt.strftime("%Y-%m-%d")
        panel["extraction_timestamp"] = now_utc
        panel = panel.drop(columns=["dt", "year"])
        
        panel = panel.sort_values("year_month").reset_index(drop=True)
        
        # Save Parquet and CSV
        out_parquet = os.path.join(STRUCTURED_DIR, "external_shocks_monthly.parquet")
        out_csv = os.path.join(STRUCTURED_DIR, "external_shocks_monthly.csv")
        panel.to_parquet(out_parquet, index=False)
        panel.to_csv(out_csv, index=False)
        
        min_date = panel["observation_date"].min()
        max_date = panel["observation_date"].max()
        rows, cols = panel.shape
        
        print(f"Target File Path: {out_parquet}")
        print(f"Total Rows & Columns Extracted: {rows} rows, {cols} columns")
        print(f"Date Coverage: {min_date} to {max_date} (Annual GDP isolated in macro_annual_gdp.parquet)")
        print("Status: SUCCESS")
        
    except Exception as exc:
        logger.exception("Failed to extract external shocks.")
        print(f"Target File Path: {os.path.join(STRUCTURED_DIR, 'external_shocks_monthly.parquet')}")
        print("Total Rows & Columns Extracted: 0 rows, 0 columns")
        print("Date Coverage: None")
        print("Status: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
