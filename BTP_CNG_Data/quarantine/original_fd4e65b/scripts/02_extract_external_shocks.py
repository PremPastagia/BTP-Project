#!/usr/bin/env python3
"""
02_extract_external_shocks.py
Phase 3B: Extract World Bank Energy Commodity Benchmarks, Caldara-Iacoviello GPR,
USD/INR exchange rates, and Indian CPI & GDP series. Align monthly with anti-lookahead lags.
"""

import os
import sys
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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
            logger.info("World Bank Pink Sheet saved.")
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
    """Fetches front-month monthly closes for Brent and Henry Hub to extend series to current month."""
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
    gpr_url = "https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls"
    local_path = os.path.join(RAW_MACRO_DIR, "data_gpr_export.xls")
    
    if not os.path.exists(local_path):
        logger.info("Downloading Caldara & Iacoviello GPR Dataset...")
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
    """Pulls authentic monthly USD/INR exchange rate series from verified financial API."""
    url = "https://query1.finance.yahoo.com/v8/finance/chart/INR=X?range=15y&interval=1mo"
    local_path = os.path.join(RAW_MACRO_DIR, "usdinr_monthly_raw.json")
    
    logger.info("Fetching USD/INR monthly rates...")
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        data = r.json()["chart"]["result"][0]
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
    else:
        raise RuntimeError(f"Failed to fetch USD/INR: HTTP {r.status_code}")


def extract_cpi_imf():
    """Extracts official monthly CPI for India from IMF via DBnomics API."""
    url = "https://api.db.nomics.world/v22/series/IMF/CPI/M.IN.PCPI_IX?observations=1"
    local_path = os.path.join(RAW_MACRO_DIR, "cpi_imf_raw.json")
    
    logger.info("Fetching India Monthly CPI from IMF...")
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        data = r.json()
        series = data["series"]["docs"][0]
        periods = series["period"]
        values = series["value"]
        records = []
        for p, v in zip(periods, values):
            if v is not None and str(v).lower() != "na":
                records.append({
                    "year_month": p,
                    "cpi_index": float(v)
                })
        df = pd.DataFrame(records).drop_duplicates(subset=["year_month"]).sort_values("year_month").reset_index(drop=True)
        logger.info(f"Extracted {len(df)} monthly CPI observations from IMF.")
        return df
    else:
        raise RuntimeError(f"Failed to fetch CPI from IMF: HTTP {r.status_code}")


def extract_gdp_world_bank():
    """Extracts official Indian GDP from World Bank API and interpolates to monthly series."""
    url = "https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.KD?format=json&per_page=70"
    local_path = os.path.join(RAW_MACRO_DIR, "gdp_india_wb.json")
    
    logger.info("Fetching Indian GDP from World Bank...")
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(r.text)
        items = r.json()[1]
        records = []
        for item in items:
            yr = item["date"]
            val = item["value"]
            if val is not None:
                records.append({
                    "year": int(yr),
                    "gdp_real_usd": float(val)
                })
        df = pd.DataFrame(records).sort_values("year").reset_index(drop=True)
        logger.info(f"Extracted {len(df)} annual GDP observations from World Bank.")
        return df
    else:
        raise RuntimeError(f"Failed to fetch GDP from World Bank: HTTP {r.status_code}")


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
        
        # 4. CPI & GDP
        df_cpi = extract_cpi_imf()
        df_gdp = extract_gdp_world_bank()
        
        # Monthly date range from 2011-01 to 2026-11
        date_range = pd.date_range(start="2011-01-01", end="2026-11-01", freq="MS")
        panel = pd.DataFrame({"year_month": date_range.strftime("%Y-%m")})
        panel["year"] = pd.to_datetime(panel["year_month"] + "-01").dt.year
        
        # Merge all datasets
        panel = pd.merge(panel, df_energy, on="year_month", how="left")
        panel = pd.merge(panel, df_gpr, on="year_month", how="left")
        panel = pd.merge(panel, df_forex, on="year_month", how="left")
        panel = pd.merge(panel, df_cpi, on="year_month", how="left")
        panel = pd.merge(panel, df_gdp, on="year", how="left")
        
        # Clean interpolations and forward fills for latest months
        panel["gdp_real_usd"] = panel["gdp_real_usd"].interpolate(method="linear").bfill().ffill()
        panel["cpi_index"] = panel["cpi_index"].ffill()
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
        
        # Add Anti-Lookahead Lags (1-month publication lag for predictors)
        panel["brent_crude_usd_lag1"] = panel["brent_crude_usd"].shift(1)
        panel["henry_hub_usd_lag1"] = panel["henry_hub_usd"].shift(1)
        panel["ttf_gas_usd_lag1"] = panel["ttf_gas_usd"].shift(1)
        panel["lng_japan_usd_lag1"] = panel["lng_japan_usd"].shift(1)
        panel["gpr_index_lag1"] = panel["gpr_index"].shift(1)
        panel["cpi_index_lag1"] = panel["cpi_index"].shift(1)
        panel["usd_inr_mean_lag1"] = panel["usd_inr_mean"].shift(1)
        
        # Timestamps
        now_utc = datetime.now(timezone.utc).isoformat()
        panel["dt"] = pd.to_datetime(panel["year_month"] + "-01")
        panel["observation_date"] = (panel["dt"] + pd.offsets.MonthEnd(1)).dt.strftime("%Y-%m-%d")
        panel["publication_release_date"] = (panel["dt"] + pd.offsets.MonthEnd(1)).dt.strftime("%Y-%m-%d")
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
        
        # 4-line verification receipt
        print(f"Target File Path: {out_parquet}")
        print(f"Total Rows & Columns Extracted: {rows} rows, {cols} columns")
        print(f"Date Coverage: {min_date} to {max_date}")
        print("Status: SUCCESS")
        
    except Exception as exc:
        logger.exception("External shocks extraction failed.")
        print(f"Target File Path: {os.path.join(STRUCTURED_DIR, 'external_shocks_monthly.parquet')}")
        print("Total Rows & Columns Extracted: 0 rows, 0 columns")
        print("Date Coverage: None")
        print("Status: FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
