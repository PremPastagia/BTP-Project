"""
Process World Bank Commodity Pink Sheet and Caldara-Iacoviello GPR Index
into structured, monthly benchmark time-series tables in Parquet and CSV.
"""

import os
import pandas as pd
import numpy as np

RAW_WB = "BTP_CNG_Data/raw/energy_markets/WorldBank_CMO_Historical_Monthly.xlsx"
RAW_GPR = "BTP_CNG_Data/raw/macro_weather/gpr_monthly.xls"
OUT_DIR = "BTP_CNG_Data/structured/numerical_factors"

os.makedirs(OUT_DIR, exist_ok=True)

# 1. Process World Bank Commodities
print("Processing World Bank Commodity Pink Sheet...")
# Sheet 'Monthly Prices', skiprows=4
df_wb = pd.read_excel(RAW_WB, sheet_name="Monthly Prices", skiprows=4)

# First column is YYYYMYY (e.g., '1960M01')
df_wb = df_wb.rename(columns={df_wb.columns[0]: "Period"})
df_wb = df_wb[df_wb["Period"].astype(str).str.contains(r"^\d{4}M\d{2}$", na=False)].copy()

# Parse period to Year-Month Date (1st of month)
df_wb["Date"] = pd.to_datetime(df_wb["Period"].str.replace("M", "-") + "-01")

# Extract key energy benchmarks
target_cols = {
    "Crude oil, Brent": "Brent_Crude_USD_bbl",
    "Crude oil, Dubai": "Dubai_Crude_USD_bbl",
    "Crude oil, WTI": "WTI_Crude_USD_bbl",
    "Natural gas, US": "Henry_Hub_USD_mmbtu",
    "Natural gas, Europe": "TTF_NaturalGas_USD_mmbtu",
    "Liquefied natural gas, Japan": "LNG_Japan_USD_mmbtu",
    "Natural gas index": "World_Natural_Gas_Index"
}

wb_extracted = pd.DataFrame({"Date": df_wb["Date"]})
for raw_col, clean_col in target_cols.items():
    if raw_col in df_wb.columns:
        wb_extracted[clean_col] = pd.to_numeric(df_wb[raw_col], errors="coerce")

wb_extracted = wb_extracted[wb_extracted["Date"] >= "2010-01-01"].sort_values("Date").reset_index(drop=True)
print(f"World Bank series extracted: {len(wb_extracted)} months ({wb_extracted['Date'].min().strftime('%Y-%m')} to {wb_extracted['Date'].max().strftime('%Y-%m')})")

# 2. Process GPR Index
print("Processing Caldara-Iacoviello Geopolitical Risk Index...")
df_gpr = pd.read_excel(RAW_GPR)
# column 'month' is timestamp or numeric YYYYMM
df_gpr["Date"] = pd.to_datetime(df_gpr["month"])
gpr_extracted = df_gpr[["Date", "GPR", "GPRT", "GPRA"]].copy()
gpr_extracted.columns = ["Date", "GPR_Benchmark", "GPR_Threats", "GPR_Acts"]
for c in ["GPR_Benchmark", "GPR_Threats", "GPR_Acts"]:
    gpr_extracted[c] = pd.to_numeric(gpr_extracted[c], errors="coerce")

gpr_extracted = gpr_extracted[gpr_extracted["Date"] >= "2010-01-01"].sort_values("Date").reset_index(drop=True)
print(f"GPR series extracted: {len(gpr_extracted)} months ({gpr_extracted['Date'].min().strftime('%Y-%m')} to {gpr_extracted['Date'].max().strftime('%Y-%m')})")

# 3. Merge External Shocks
merged = pd.merge(wb_extracted, gpr_extracted, on="Date", how="outer").sort_values("Date").reset_index(drop=True)

out_parquet = os.path.join(OUT_DIR, "external_shocks_monthly.parquet")
out_csv = os.path.join(OUT_DIR, "external_shocks_monthly.csv")

merged.to_parquet(out_parquet, index=False)
merged.to_csv(out_csv, index=False)
print(f"Successfully saved {len(merged)} rows to {out_parquet} and {out_csv}")
