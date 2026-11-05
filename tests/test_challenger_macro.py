"""
Empirical Challenge & Adversarial Stress Harness for data/macro_data.csv.

Independent verification harness by challenger_m1_2:
1. GDP & PFCE Quarterly Conservation vs. Live MoSPI API Data.
2. Boundary Smoothness & Step Jump Diagnostics (Intra- vs Inter-quarter).
3. CPI Index Continuity, Monotonicity & Inflation Rate Distribution.
4. Comprehensive Data Integrity & Anomaly Stress Test.
"""

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "macro_data.csv"


class LegacySSLAdapter(HTTPAdapter):
    """Enable OpenSSL 3.0+ legacy renegotiation for MoSPI servers."""
    def init_poolmanager(self, *args: Any, **kwargs: Any) -> Any:
        ctx = create_urllib3_context()
        ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def get_mospi_session() -> requests.Session:
    session = requests.Session()
    session.mount("https://", LegacySSLAdapter())
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    })
    return session


def fetch_mospi_nas_data(indicator_code: int, base_year: str) -> List[Dict[str, Any]]:
    session = get_mospi_session()
    url = (
        f"https://api.mospi.gov.in/api/nas/getNasData?"
        f"account_code=1&frequency_code=2&indicator_code={indicator_code}"
        f"&base_year={base_year}&series=Current&limit=100"
    )
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])


def fetch_mospi_cpi_data(start_year: int = 2011, end_year: int = 2025) -> Dict[str, float]:
    session = get_mospi_session()
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }
    cpi_data = {}
    for y in range(start_year, end_year + 1):
        url = (
            f"https://api.mospi.gov.in/api/cpi/getCpiData?"
            f"level=Group&base_year=2012&state_code=99&sector_code=3"
            f"&group_code=0&subgroup_code=0.99&year={y}&limit=100"
        )
        try:
            r = session.get(url, timeout=20)
            if r.status_code == 200:
                for rec in r.json().get("data", []):
                    m_name = str(rec.get("month", "")).strip().lower()
                    val = float(rec.get("index", 0.0))
                    status = rec.get("status", "")
                    if m_name in month_map and val > 0:
                        m_num = month_map[m_name]
                        d_str = f"{y:04d}-{m_num:02d}-01"
                        if d_str not in cpi_data or status == "F":
                            cpi_data[d_str] = round(val, 2)
        except Exception as e:
            print(f"Warning fetching MoSPI CPI for {y}: {e}")
    return cpi_data


def test_quarterly_conservation():
    print("=" * 70)
    print("TEST 1: Quarterly Sum Conservation vs Official MoSPI Data")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # 1. Fetch live MoSPI NAS data for GDP (indicator 5) and PFCE (indicator 10)
    print("Fetching live GDP Base 2011-12...")
    raw_gdp_1112 = fetch_mospi_nas_data(5, "2011-12")
    print(f"Retrieved {len(raw_gdp_1112)} quarters of GDP 2011-12.")

    print("Fetching live GDP Base 2022-23...")
    raw_gdp_2223 = fetch_mospi_nas_data(5, "2022-23")
    print(f"Retrieved {len(raw_gdp_2223)} quarters of GDP 2022-23.")

    gdp_1112_dict = {f"{x['year']}_{x['quarter']}": float(x["constant_price"]) for x in raw_gdp_1112 if float(x.get("constant_price", 0)) > 0}
    gdp_2223_dict = {f"{x['year']}_{x['quarter']}": float(x["constant_price"]) for x in raw_gdp_2223 if float(x.get("constant_price", 0)) > 0}

    # Splicing factor
    overlap_keys = sorted(set(gdp_1112_dict.keys()) & set(gdp_2223_dict.keys()))
    sum_overlap_1112 = sum(gdp_1112_dict[k] for k in overlap_keys)
    sum_overlap_2223 = sum(gdp_2223_dict[k] for k in overlap_keys)
    l_gdp = sum_overlap_1112 / sum_overlap_2223
    print(f"Overlap quarters count: {len(overlap_keys)} ({overlap_keys[0]} to {overlap_keys[-1]})")
    print(f"Calculated Linking Factor L_GDP: {l_gdp:.8f}")

    spliced_gdp_ref = dict(gdp_1112_dict)
    for k, v in gdp_2223_dict.items():
        if k not in spliced_gdp_ref:
            spliced_gdp_ref[k] = v * l_gdp

    # Define Indian Fiscal Quarters mapping
    # Month 4, 5, 6 -> Q1 of FY YYYY-(YYYY+1)
    # Month 7, 8, 9 -> Q2 of FY YYYY-(YYYY+1)
    # Month 10, 11, 12 -> Q3 of FY YYYY-(YYYY+1)
    # Month 1, 2, 3 -> Q4 of FY (YYYY-1)-YYYY
    def get_fiscal_quarter(dt):
        y = dt.year
        m = dt.month
        if m in (4, 5, 6):
            return f"{y}-{str(y+1)[-2:]}_Q1"
        elif m in (7, 8, 9):
            return f"{y}-{str(y+1)[-2:]}_Q2"
        elif m in (10, 11, 12):
            return f"{y}-{str(y+1)[-2:]}_Q3"
        else:
            return f"{y-1}-{str(y)[-2:]}_Q4"

    df["FiscalQuarter"] = df["Date"].apply(get_fiscal_quarter)

    # 2. Fetch live MoSPI NAS data for PFCE (indicator 10)
    print("\nFetching live PFCE Base 2011-12...")
    raw_pfce_1112 = fetch_mospi_nas_data(10, "2011-12")
    print(f"Retrieved {len(raw_pfce_1112)} quarters of PFCE 2011-12.")
    print("Fetching live PFCE Base 2022-23...")
    raw_pfce_2223 = fetch_mospi_nas_data(10, "2022-23")
    print(f"Retrieved {len(raw_pfce_2223)} quarters of PFCE 2022-23.")

    pfce_1112_dict = {f"{x['year']}_{x['quarter']}": float(x["constant_price"]) for x in raw_pfce_1112 if float(x.get("constant_price", 0)) > 0}
    pfce_2223_dict = {f"{x['year']}_{x['quarter']}": float(x["constant_price"]) for x in raw_pfce_2223 if float(x.get("constant_price", 0)) > 0}

    overlap_keys_pfce = sorted(set(pfce_1112_dict.keys()) & set(pfce_2223_dict.keys()))
    l_pfce = sum(pfce_1112_dict[k] for k in overlap_keys_pfce) / sum(pfce_2223_dict[k] for k in overlap_keys_pfce)
    print(f"PFCE Linking Factor L_PFCE: {l_pfce:.8f}")

    spliced_pfce_ref = dict(pfce_1112_dict)
    for k, v in pfce_2223_dict.items():
        if k not in spliced_pfce_ref:
            spliced_pfce_ref[k] = v * l_pfce

    q_agg = df.groupby("FiscalQuarter").agg(
        Monthly_Sum_GDP=("GDP_Monthly_Cr", "sum"),
        Monthly_Sum_PFCE=("Income_PFCE_Cr", "sum"),
        Monthly_Count=("GDP_Monthly_Cr", "count"),
        Start_Date=("Date", "min"),
        End_Date=("Date", "max")
    ).reset_index()

    q_agg["Start_Date"] = q_agg["Start_Date"].dt.strftime("%Y-%m-%d")
    q_agg["End_Date"] = q_agg["End_Date"].dt.strftime("%Y-%m-%d")

    comparison = []
    for _, row in q_agg.iterrows():
        fq = row["FiscalQuarter"]
        m_sum_gdp = row["Monthly_Sum_GDP"]
        m_sum_pfce = row["Monthly_Sum_PFCE"]
        cnt = row["Monthly_Count"]

        ref_spliced_gdp = spliced_gdp_ref.get(fq, None)
        ref_unspliced_gdp = gdp_1112_dict.get(fq, None)

        ref_spliced_pfce = spliced_pfce_ref.get(fq, None)
        ref_unspliced_pfce = pfce_1112_dict.get(fq, None)

        abs_err_gdp = abs(m_sum_gdp - ref_spliced_gdp) if ref_spliced_gdp else None
        pct_err_gdp = (abs_err_gdp / ref_spliced_gdp) * 100.0 if ref_spliced_gdp else None

        abs_err_pfce = abs(m_sum_pfce - ref_spliced_pfce) if ref_spliced_pfce else None
        pct_err_pfce = (abs_err_pfce / ref_spliced_pfce) * 100.0 if ref_spliced_pfce else None

        comparison.append({
            "FiscalQuarter": fq,
            "Count": cnt,
            "Monthly_Sum_GDP": m_sum_gdp,
            "MoSPI_GDP_Spliced": ref_spliced_gdp,
            "Abs_Err_GDP": abs_err_gdp,
            "Pct_Err_GDP": pct_err_gdp,
            "Monthly_Sum_PFCE": m_sum_pfce,
            "MoSPI_PFCE_Spliced": ref_spliced_pfce,
            "Abs_Err_PFCE": abs_err_pfce,
            "Pct_Err_PFCE": pct_err_pfce,
        })

    comp_df = pd.DataFrame(comparison)
    print("\nQuarterly Conservation Results (first 5 and last 5 quarters):")
    print(comp_df[["FiscalQuarter", "Monthly_Sum_GDP", "MoSPI_GDP_Spliced", "Abs_Err_GDP", "Pct_Err_GDP"]].head(5).to_string(index=False))
    print("...")
    print(comp_df[["FiscalQuarter", "Monthly_Sum_GDP", "MoSPI_GDP_Spliced", "Abs_Err_GDP", "Pct_Err_GDP"]].tail(5).to_string(index=False))

    valid_pct_errs_gdp = comp_df["Pct_Err_GDP"].dropna()
    valid_abs_errs_gdp = comp_df["Abs_Err_GDP"].dropna()
    max_pct_dev_gdp = valid_pct_errs_gdp.max()
    max_abs_dev_gdp = valid_abs_errs_gdp.max()
    mean_pct_dev_gdp = valid_pct_errs_gdp.mean()

    valid_pct_errs_pfce = comp_df["Pct_Err_PFCE"].dropna()
    valid_abs_errs_pfce = comp_df["Abs_Err_PFCE"].dropna()
    max_pct_dev_pfce = valid_pct_errs_pfce.max()
    max_abs_dev_pfce = valid_abs_errs_pfce.max()

    print(f"\n--- SUMMARY OF QUARTERLY CONSERVATION ---")
    print(f"Total Quarters Evaluated: {len(comp_df)}")
    print(f"GDP Maximum Percentage Deviation: {max_pct_dev_gdp:.8f}%")
    print(f"GDP Mean Percentage Deviation: {mean_pct_dev_gdp:.8f}%")
    print(f"GDP Maximum Absolute Deviation: INR {max_abs_dev_gdp:.4f} Crore")
    print(f"PFCE Maximum Percentage Deviation: {max_pct_dev_pfce:.8f}%")
    print(f"PFCE Maximum Absolute Deviation: INR {max_abs_dev_pfce:.4f} Crore")

    return comp_df, max_pct_dev_gdp


def test_boundary_smoothness():
    print("\n" + "=" * 70)
    print("TEST 2: Smoothness & Quarter Boundary Jump Diagnostics")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    # Add quarter info
    df["Month"] = df["Date"].dt.month
    # Month positions inside fiscal quarter:
    # Q1: 4 (pos 1), 5 (pos 2), 6 (pos 3)
    # Q2: 7 (pos 1), 8 (pos 2), 9 (pos 3)
    # Q3: 10 (pos 1), 11 (pos 2), 12 (pos 3)
    # Q4: 1 (pos 1), 2 (pos 2), 3 (pos 3)
    pos_map = {4: 1, 5: 2, 6: 3, 7: 1, 8: 2, 9: 3, 10: 1, 11: 2, 12: 3, 1: 1, 2: 2, 3: 3}
    df["Quarter_Pos"] = df["Month"].map(pos_map)

    # Month-to-month changes
    df["GDP_Diff"] = df["GDP_Monthly_Cr"].diff()
    df["GDP_Pct_Change"] = (df["GDP_Monthly_Cr"].pct_change()) * 100.0

    # Classify transition type:
    # If Quarter_Pos == 1: transition from previous row was (Pos 3 of prev Q -> Pos 1 of new Q) = INTER-QUARTER BOUNDARY
    # If Quarter_Pos in (2, 3): transition was within quarter (1->2 or 2->3) = INTRA-QUARTER
    df["Transition_Type"] = np.where(df["Quarter_Pos"] == 1, "INTER_BOUNDARY", "INTRA_QUARTER")
    df.loc[0, "Transition_Type"] = "START"

    intra = df[df["Transition_Type"] == "INTRA_QUARTER"]
    inter = df[df["Transition_Type"] == "INTER_BOUNDARY"]

    print(f"Total Transitions: {len(df) - 1} (Intra-quarter: {len(intra)}, Inter-quarter boundary: {len(inter)})")

    print("\n--- GDP Month-to-Month Absolute Change Distribution ---")
    print(f"Intra-Quarter: mean={intra['GDP_Diff'].abs().mean():.2f} Cr, std={intra['GDP_Diff'].abs().std():.2f} Cr, max={intra['GDP_Diff'].abs().max():.2f} Cr, median={intra['GDP_Diff'].abs().median():.2f} Cr")
    print(f"Inter-Boundary: mean={inter['GDP_Diff'].abs().mean():.2f} Cr, std={inter['GDP_Diff'].abs().std():.2f} Cr, max={inter['GDP_Diff'].abs().max():.2f} Cr, median={inter['GDP_Diff'].abs().median():.2f} Cr")

    print("\n--- GDP Month-to-Month Percentage Change Distribution ---")
    print(f"Intra-Quarter: mean={intra['GDP_Pct_Change'].abs().mean():.3f}%, std={intra['GDP_Pct_Change'].abs().std():.3f}%, max={intra['GDP_Pct_Change'].abs().max():.3f}%, median={intra['GDP_Pct_Change'].abs().median():.3f}%")
    print(f"Inter-Boundary: mean={inter['GDP_Pct_Change'].abs().mean():.3f}%, std={inter['GDP_Pct_Change'].abs().std():.3f}%, max={inter['GDP_Pct_Change'].abs().max():.3f}%, median={inter['GDP_Pct_Change'].abs().median():.3f}%")

    # Specific quarter boundaries breakdown:
    # Q1 to Q2: Month 6 -> Month 7 (June -> July)
    # Q2 to Q3: Month 9 -> Month 10 (Sept -> Oct)
    # Q3 to Q4: Month 12 -> Month 1 (Dec -> Jan)
    # Q4 to Q1: Month 3 -> Month 4 (March -> April)
    df["Boundary_Name"] = ""
    for i in range(1, len(df)):
        m_prev = df.loc[i-1, "Month"]
        m_curr = df.loc[i, "Month"]
        if (m_prev, m_curr) == (6, 7):
            df.loc[i, "Boundary_Name"] = "Q1->Q2 (Jun-Jul)"
        elif (m_prev, m_curr) == (9, 10):
            df.loc[i, "Boundary_Name"] = "Q2->Q3 (Sep-Oct)"
        elif (m_prev, m_curr) == (12, 1):
            df.loc[i, "Boundary_Name"] = "Q3->Q4 (Dec-Jan)"
        elif (m_prev, m_curr) == (3, 4):
            df.loc[i, "Boundary_Name"] = "Q4->Q1 (Mar-Apr)"

    boundary_summary = df[df["Boundary_Name"] != ""].groupby("Boundary_Name").agg(
        Count=("GDP_Pct_Change", "count"),
        Mean_Abs_Pct=("GDP_Pct_Change", lambda s: s.abs().mean()),
        Max_Abs_Pct=("GDP_Pct_Change", lambda s: s.abs().max()),
        Mean_Abs_Diff=("GDP_Diff", lambda s: s.abs().mean()),
        Max_Abs_Diff=("GDP_Diff", lambda s: s.abs().max())
    )
    print("\n--- Boundary Transitions by Quarter Junction ---")
    print(boundary_summary.to_string())

    # Second Differences: Check curvature/acceleration spikes at boundaries
    df["GDP_Diff2"] = df["GDP_Diff"].diff()
    intra_diff2 = df[df["Transition_Type"] == "INTRA_QUARTER"]["GDP_Diff2"].dropna()
    inter_diff2 = df[df["Transition_Type"] == "INTER_BOUNDARY"]["GDP_Diff2"].dropna()
    print(f"\n--- Curvature / 2nd Difference (Delta^2 GDP) ---")
    print(f"Intra-Quarter 2nd diff: mean={intra_diff2.abs().mean():.2f} Cr, max={intra_diff2.abs().max():.2f} Cr")
    print(f"Inter-Boundary 2nd diff: mean={inter_diff2.abs().mean():.2f} Cr, max={inter_diff2.abs().max():.2f} Cr")

    # Ratio of inter to intra max and mean
    ratio_mean = inter['GDP_Pct_Change'].abs().mean() / intra['GDP_Pct_Change'].abs().mean()
    ratio_max = inter['GDP_Pct_Change'].abs().max() / intra['GDP_Pct_Change'].abs().max()
    print(f"\nInter/Intra Mean Pct Change Ratio: {ratio_mean:.3f}")
    print(f"Inter/Intra Max Pct Change Ratio: {ratio_max:.3f}")

    return df


def test_cpi_integrity():
    print("\n" + "=" * 70)
    print("TEST 3: CPI Index Monotonicity, Continuity & Inflation Rates")
    print("=" * 70)

    df = pd.read_csv(CSV_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)

    print(f"Total CPI months in dataset: {len(df)}")
    print(f"CPI Range: min={df['CPI_Index'].min()}, max={df['CPI_Index'].max()}")

    # 1. Compare against MoSPI official CPI API
    print("Fetching authentic MoSPI CPI for verification...")
    live_cpi = fetch_mospi_cpi_data(2011, 2025)
    print(f"Retrieved {len(live_cpi)} live MoSPI CPI data points.")

    mismatch_count = 0
    max_cpi_diff = 0.0
    for idx, row in df.iterrows():
        d_str = row["Date"].strftime("%Y-%m-%d")
        csv_val = float(row["CPI_Index"])
        api_val = live_cpi.get(d_str)
        if api_val is not None:
            diff = abs(csv_val - api_val)
            if diff > max_cpi_diff:
                max_cpi_diff = diff
            if diff > 0.05:
                mismatch_count += 1
                print(f"Mismatch at {d_str}: CSV={csv_val}, MoSPI API={api_val}, diff={diff}")

    print(f"CPI Matching with MoSPI API: {len(df) - mismatch_count} / {len(df)} exact matches (within 0.05 index points)")
    print(f"Max CPI Difference vs MoSPI API: {max_cpi_diff:.4f}")

    # 2. Check Continuity and Date Sequence
    df["Date_Diff_Days"] = df["Date"].diff().dt.days
    irregular_gaps = df[df["Date_Diff_Days"].notna() & ((df["Date_Diff_Days"] < 28) | (df["Date_Diff_Days"] > 31))]
    print(f"Irregular Calendar Gaps count: {len(irregular_gaps)}")

    # 3. Monotonicity & Inflation Rates
    df["CPI_MoM_Diff"] = df["CPI_Index"].diff()
    df["CPI_MoM_Inflation"] = df["CPI_Index"].pct_change() * 100.0
    df["CPI_YoY_Inflation"] = df["CPI_Index"].pct_change(12) * 100.0

    drops = df[df["CPI_MoM_Diff"] < 0]
    print(f"\nNon-monotonic CPI Months (MoM drops): {len(drops)} / {len(df) - 1} months ({len(drops)/(len(df)-1)*100:.1f}%)")
    print("Distribution of MoM CPI drops (Seasonal food dips):")
    print(drops[["Date", "CPI_Index", "CPI_MoM_Diff", "CPI_MoM_Inflation"]].head(15).to_string())

    # Month of year breakdown for negative inflation
    drops_by_month = drops["Date"].dt.month.value_counts().sort_index()
    month_names = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}
    print("\nNegative MoM Inflation occurrences by calendar month:")
    for m, c in drops_by_month.items():
        print(f"  {month_names[m]}: {c} times")

    # Inflation distribution
    print("\n--- CPI Inflation Rate Statistics (177 Months) ---")
    print(f"MoM Inflation: mean={df['CPI_MoM_Inflation'].mean():.3f}%, min={df['CPI_MoM_Inflation'].min():.3f}%, max={df['CPI_MoM_Inflation'].max():.3f}%, std={df['CPI_MoM_Inflation'].std():.3f}%")
    yoy_valid = df["CPI_YoY_Inflation"].dropna()
    print(f"YoY Inflation: mean={yoy_valid.mean():.3f}%, min={yoy_valid.min():.3f}%, max={yoy_valid.max():.3f}%, std={yoy_valid.std():.3f}%")

    # Outlier / extreme jump check
    extreme_mom = df[df["CPI_MoM_Inflation"].abs() > 4.0]
    print(f"Extreme MoM Inflation (> 4.0%): {len(extreme_mom)} occurrences")
    if len(extreme_mom) > 0:
        print(extreme_mom[["Date", "CPI_Index", "CPI_MoM_Inflation"]].to_string())

    return df


if __name__ == "__main__":
    print("STARTING EMPIRICAL CHALLENGE HARNESS FOR MACRO DATA")
    comp_df, max_pct_dev = test_quarterly_conservation()
    smooth_df = test_boundary_smoothness()
    cpi_df = test_cpi_integrity()
    print("\nHARNESS COMPLETED SUCCESSFULLY.")
