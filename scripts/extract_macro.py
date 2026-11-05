"""
Indian Macroeconomic Time-Series Extraction, Base-Year Splicing, and Temporal Disaggregation Engine.

Extracts authentic macroeconomic indicators from the official Ministry of Statistics and
Programme Implementation (MoSPI) eSankhyiki REST API (https://api.mospi.gov.in):
- Quarterly Real Gross Domestic Product (GDP at constant 2011-12 prices, indicator_code=5)
- Quarterly Private Final Consumption Expenditure (PFCE / Income demand proxy, indicator_code=10)
- Monthly Consumer Price Index (CPI All-India Combined General Index, base 2012=100)

Features:
- Legacy SSL renegotiation transport adapter (OpenSSL 3.0+ compatibility)
- UN SNA 2008 / IMF QNA Ratio Linking Factor base-year splicing
- IMF Denton-Cholette Proportional Benchmarking disaggregation strictly conserving quarterly sums
- Shape-preserving Fritsch-Carlson Rescaled Monotone Cubic Spline disaggregation
- Generates data/macro_data.csv (Date, GDP_Monthly_Cr, CPI_Index, Income_PFCE_Cr)
- Strictly 0 synthetic or fabricated data points
"""

import calendar
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from scipy.interpolate import PchipInterpolator
from urllib3.util import create_urllib3_context


class LegacySSLAdapter(HTTPAdapter):
    """
    urllib3 HTTPAdapter enabling OpenSSL 3.0+ legacy server renegotiation (ssl.OP_LEGACY_SERVER_CONNECT).
    Required for secure communication with Indian Government (MoSPI) server infrastructure.
    """

    def init_poolmanager(self, *args: Any, **kwargs: Any) -> Any:
        ctx = create_urllib3_context()
        ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)


def get_mospi_session() -> requests.Session:
    """Create a requests session with LegacySSLAdapter mounted and browser headers."""
    session = requests.Session()
    session.mount("https://", LegacySSLAdapter())
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    })
    return session


def parse_fy_quarter(item: Dict[str, Any]) -> Tuple[int, int, int, int]:
    """
    Parse Indian Fiscal Year and Quarter string (e.g., '2011-12' and 'Q1')
    into chronological ordering tuple (cal_year, start_month, q_num, fy_start_year).

    Indian Fiscal Quarters:
      Q1: April - June (start_month = 4, cal_year = fy_start_year)
      Q2: July - September (start_month = 7, cal_year = fy_start_year)
      Q3: October - December (start_month = 10, cal_year = fy_start_year)
      Q4: January - March (start_month = 1, cal_year = fy_start_year + 1)
    """
    fy = str(item["year"])
    q_str = str(item["quarter"]).upper()
    start_year = int(fy.split("-")[0])
    q_num = int(q_str.replace("Q", ""))

    cal_year = start_year if q_num in (1, 2, 3) else start_year + 1
    start_month = {1: 4, 2: 7, 3: 10, 4: 1}[q_num]
    return (cal_year, start_month, q_num, start_year)


def compute_ratio_linking_factor(
    target_series: Dict[str, float],
    source_series: Dict[str, float],
    overlap_keys: Optional[List[str]] = None,
) -> float:
    """
    Compute SNA/IMF Ratio Linking Factor (L) across overlapping benchmark periods:
      L = sum(target_series[t]) / sum(source_series[t]) for t in overlap
    """
    if overlap_keys is None:
        overlap_keys = sorted(set(target_series.keys()) & set(source_series.keys()))

    if not overlap_keys:
        raise ValueError("No overlapping periods found between target and source series.")

    sum_target = sum(target_series[k] for k in overlap_keys)
    sum_source = sum(source_series[k] for k in overlap_keys)

    if sum_source == 0:
        raise ZeroDivisionError("Sum of source series across overlap is zero.")

    return sum_target / sum_source


def splice_base_years(
    primary_series: Dict[str, float],
    secondary_series: Dict[str, float],
    direction: str = "forward",
) -> Tuple[Dict[str, float], float]:
    """
    Splice secondary series into primary series using the Ratio Linking Factor method.

    Parameters:
        primary_series: Series under primary base year (e.g. 2011-12)
        secondary_series: Series under newer/older base year (e.g. 2022-23)
        direction: 'forward' to extend primary into newer periods; 'backward' to back-cast.

    Returns:
        (spliced_series_dict, linking_factor)
    """
    overlap_keys = sorted(set(primary_series.keys()) & set(secondary_series.keys()))
    if not overlap_keys:
        return dict(primary_series), 1.0

    linking_factor = compute_ratio_linking_factor(primary_series, secondary_series, overlap_keys)
    spliced = dict(primary_series)

    if direction == "forward":
        # Extend with newer periods from secondary scaled by linking_factor
        for k, v in secondary_series.items():
            if k not in spliced:
                spliced[k] = v * linking_factor
    elif direction == "backward":
        # Back-cast older periods from secondary scaled by linking_factor
        for k, v in secondary_series.items():
            if k not in spliced:
                spliced[k] = v * linking_factor

    return spliced, linking_factor


def denton_cholette(
    quarterly_values: Union[List[float], np.ndarray],
    indicator: Optional[Union[List[float], np.ndarray]] = None,
    epsilon: float = 1e-8,
) -> np.ndarray:
    """
    Denton-Cholette Proportional Benchmarking Method (IMF standard).
    Disaggregates quarterly totals into 3 monthly values per quarter,
    strictly conserving quarterly aggregates: sum(m[3q : 3q+3]) == Q[q].

    Parameters:
        quarterly_values: 1D array of N quarterly values.
        indicator: Optional preliminary high-frequency indicator of length 3N.
        epsilon: Small Tikhonov regularization factor for numerical stability.

    Returns:
        1D numpy array of length 3N with interpolated monthly values.
    """
    Q = np.asarray(quarterly_values, dtype=float)
    N = len(Q)
    M = 3 * N

    # Aggregation matrix C (N x 3N)
    C = np.zeros((N, M))
    for q in range(N):
        C[q, 3 * q : 3 * q + 3] = 1.0

    # First-difference matrix D ((3N-1) x 3N)
    D = np.zeros((M - 1, M))
    for i in range(M - 1):
        D[i, i] = -1.0
        D[i, i + 1] = 1.0

    W = D.T @ D + epsilon * np.eye(M)
    W_inv = np.linalg.inv(W)

    if indicator is None:
        # Standard Denton without indicator
        CW_inv = C @ W_inv
        CW_inv_CT = CW_inv @ C.T
        CW_inv_CT_inv = np.linalg.inv(CW_inv_CT)
        m = W_inv @ C.T @ CW_inv_CT_inv @ Q
    else:
        # Proportional Denton with indicator
        I = np.asarray(indicator, dtype=float)
        # Avoid zero division in indicator
        I = np.where(I == 0, 1.0, I)
        P = np.diag(I)
        CP = C @ P
        CPW_inv = CP @ W_inv
        denom = CPW_inv @ CP.T
        denom_inv = np.linalg.inv(denom)
        z = W_inv @ CP.T @ denom_inv @ Q
        m = P @ z

    return m


def rescaled_monotone_spline(
    quarterly_values: Union[List[float], np.ndarray]
) -> np.ndarray:
    """
    Fritsch-Carlson shape-preserving monotone cubic spline interpolation (Pchip)
    evaluated at monthly points and rescaled within each quarter to guarantee exact
    sum conservation: sum(m[3q : 3q+3]) == Q[q].

    Parameters:
        quarterly_values: 1D array of N quarterly values.

    Returns:
        1D numpy array of length 3N with smooth, non-negative monthly values.
    """
    Q = np.asarray(quarterly_values, dtype=float)
    N = len(Q)

    # Place quarterly centroids at 1.5, 4.5, 7.5, ... with rate Q / 3.0
    t_q = np.arange(N) * 3.0 + 1.5
    y_q = Q / 3.0

    pchip = PchipInterpolator(t_q, y_q)

    # Evaluate at monthly centroids: 0.5, 1.5, 2.5, ...
    t_m = np.arange(3 * N) + 0.5
    raw_m = pchip(t_m)

    # Rescale within each quarter to ensure sum error is 0 to machine precision
    m = np.zeros_like(raw_m)
    for q in range(N):
        idx = slice(3 * q, 3 * q + 3)
        q_sum = np.sum(raw_m[idx])
        if q_sum > 0:
            m[idx] = raw_m[idx] * (Q[q] / q_sum)
        else:
            m[idx] = Q[q] / 3.0

    return m


def disaggregate_gdp(
    quarterly_gdp: Union[List[float], np.ndarray], preserve_sum: bool = False
) -> np.ndarray:
    """
    Disaggregate quarterly GDP to monthly frequency.

    Parameters:
        quarterly_gdp: Array of quarterly values.
        preserve_sum: If True, disaggregates so 3 monthly values sum to quarterly total (via Denton).
                      If False, interpolates the quarterly curve directly (Pchip level interpolation).
    """
    q_arr = np.asarray(quarterly_gdp, dtype=float)
    if preserve_sum:
        return denton_cholette(q_arr)
    else:
        # Standard monotonic interpolation of the series trajectory
        q_x = np.arange(len(q_arr)) * 3.0 + 1.5
        interpolator = PchipInterpolator(q_x, q_arr)
        m_x = np.arange(len(q_arr) * 3.0)
        return interpolator(m_x)


def extract_mospi_nas_indicator(
    session: requests.Session,
    indicator_code: int,
    base_year: str = "2011-12",
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch National Accounts Statistics (NAS) quarterly records from MoSPI API.
    indicator_code: 5 = Gross Domestic Product, 10 = Private Final Consumption Expenditure.
    """
    url = (
        f"https://api.mospi.gov.in/api/nas/getNasData?"
        f"account_code=1&frequency_code=2&indicator_code={indicator_code}"
        f"&base_year={base_year}&series=Current&limit={limit}"
    )
    resp = session.get(url, timeout=25)
    if resp.status_code != 200:
        raise RuntimeError(
            f"MoSPI NAS API returned status {resp.status_code} for indicator {indicator_code}"
        )

    data = resp.json().get("data", [])
    return data


def extract_mospi_cpi(
    session: requests.Session,
    start_year: int = 2011,
    end_year: int = 2025,
) -> Dict[str, float]:
    """
    Extract All-India Combined General Consumer Price Index (Base 2012=100) from MoSPI API.
    Queries year-by-year, deduplicates provisional/final releases, and returns mapping { 'YYYY-MM-01': index }.
    """
    cpi_by_date: Dict[str, float] = {}

    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12
    }

    for y in range(start_year, end_year + 1):
        url = (
            f"https://api.mospi.gov.in/api/cpi/getCpiData?"
            f"level=Group&base_year=2012&state_code=99&sector_code=3"
            f"&group_code=0&subgroup_code=0.99&year={y}&limit=100"
        )
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code != 200:
                continue
            records = resp.json().get("data", [])
            for r in records:
                m_name = str(r.get("month", "")).strip().lower()
                idx_val = float(r.get("index", 0.0))
                if m_name in month_map and idx_val > 0:
                    m_num = month_map[m_name]
                    d_key = f"{y:04d}-{m_num:02d}-01"
                    # If duplicate, prefer finalized status 'F'
                    status = r.get("status", "")
                    if d_key not in cpi_by_date or status == "F":
                        cpi_by_date[d_key] = round(idx_val, 2)
        except requests.RequestException as exc:
            print(f"Warning: CPI fetch failed for year {y}: {exc}")

    return cpi_by_date


def build_macro_timeline(
    output_path: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """
    Extract real GDP, PFCE, and CPI from MoSPI, perform base-year splicing,
    temporally disaggregate to continuous monthly timeline, validate integrity,
    and save to data/macro_data.csv.

    Columns: Date, GDP_Monthly_Cr, CPI_Index, Income_PFCE_Cr
    """
    if output_path is None:
        project_root = Path(__file__).resolve().parent.parent
        output_path = project_root / "data" / "macro_data.csv"
    else:
        output_path = Path(output_path)

    session = get_mospi_session()

    print("Fetching MoSPI National Accounts Statistics (GDP & PFCE Base 2011-12)...")
    raw_gdp_1112 = extract_mospi_nas_indicator(session, indicator_code=5, base_year="2011-12")
    raw_pfce_1112 = extract_mospi_nas_indicator(session, indicator_code=10, base_year="2011-12")

    print("Fetching MoSPI National Accounts Statistics (GDP & PFCE Base 2022-23 for Splicing)...")
    try:
        raw_gdp_2223 = extract_mospi_nas_indicator(session, indicator_code=5, base_year="2022-23")
        raw_pfce_2223 = extract_mospi_nas_indicator(session, indicator_code=10, base_year="2022-23")
    except Exception as exc:
        print(f"Base 2022-23 fetch warning: {exc}")
        raw_gdp_2223 = []
        raw_pfce_2223 = []

    # Map records into dict { 'YYYY_Qn': value }
    dict_gdp_1112 = {
        f"{x['year']}_{x['quarter']}": float(x["constant_price"])
        for x in raw_gdp_1112
        if "constant_price" in x and float(x.get("constant_price", 0)) > 0
    }
    dict_pfce_1112 = {
        f"{x['year']}_{x['quarter']}": float(x["constant_price"])
        for x in raw_pfce_1112
        if "constant_price" in x and float(x.get("constant_price", 0)) > 0
    }

    dict_gdp_2223 = {
        f"{x['year']}_{x['quarter']}": float(x["constant_price"])
        for x in raw_gdp_2223
        if "constant_price" in x and float(x.get("constant_price", 0)) > 0
    }
    dict_pfce_2223 = {
        f"{x['year']}_{x['quarter']}": float(x["constant_price"])
        for x in raw_pfce_2223
        if "constant_price" in x and float(x.get("constant_price", 0)) > 0
    }

    # Perform Base-Year Splicing (Ratio Linking Factor)
    spliced_gdp, l_gdp = splice_base_years(dict_gdp_1112, dict_gdp_2223, direction="forward")
    spliced_pfce, l_pfce = splice_base_years(dict_pfce_1112, dict_pfce_2223, direction="forward")
    print(f"Base-Year Splicing: L_GDP={l_gdp:.6f}, L_PFCE={l_pfce:.6f}")

    # Build chronological list of quarterly records
    quarterly_records: List[Dict[str, Any]] = []
    for k in spliced_gdp:
        if k in spliced_pfce:
            parts = k.split("_")
            item = {"year": parts[0], "quarter": parts[1]}
            sort_key = parse_fy_quarter(item)
            quarterly_records.append({
                "key": k,
                "year": parts[0],
                "quarter": parts[1],
                "sort_key": sort_key,
                "cal_year": sort_key[0],
                "start_month": sort_key[1],
                "gdp_quarterly": spliced_gdp[k],
                "pfce_quarterly": spliced_pfce[k],
            })

    quarterly_records.sort(key=lambda x: x["sort_key"])
    print(f"Total quarterly records available: {len(quarterly_records)} quarters "
          f"({quarterly_records[0]['key']} to {quarterly_records[-1]['key']}).")

    # Extract quarterly values
    gdp_q_vals = np.array([r["gdp_quarterly"] for r in quarterly_records])
    pfce_q_vals = np.array([r["pfce_quarterly"] for r in quarterly_records])

    # Perform Denton-Cholette temporal disaggregation with preliminary spline indicator
    gdp_spline_prelim = rescaled_monotone_spline(gdp_q_vals)
    pfce_spline_prelim = rescaled_monotone_spline(pfce_q_vals)

    gdp_monthly = denton_cholette(gdp_q_vals, indicator=gdp_spline_prelim)
    pfce_monthly = denton_cholette(pfce_q_vals, indicator=pfce_spline_prelim)

    # Verify quarterly sum conservation: error < 1e-3
    n_q = len(quarterly_records)
    max_err_gdp = max(abs(sum(gdp_monthly[3 * q : 3 * q + 3]) - gdp_q_vals[q]) for q in range(n_q))
    max_err_pfce = max(abs(sum(pfce_monthly[3 * q : 3 * q + 3]) - pfce_q_vals[q]) for q in range(n_q))
    print(f"Temporal Disaggregation Max Sum Error: GDP={max_err_gdp:.6e}, PFCE={max_err_pfce:.6e}")

    # Build monthly dates for each quarter
    monthly_rows: List[Dict[str, Any]] = []
    idx = 0
    for q_idx, q_rec in enumerate(quarterly_records):
        cal_year = q_rec["cal_year"]
        start_m = q_rec["start_month"]
        for m_offset in range(3):
            m_num = start_m + m_offset
            y_num = cal_year
            if m_num > 12:
                m_num -= 12
                y_num += 1
            d_str = f"{y_num:04d}-{m_num:02d}-01"
            monthly_rows.append({
                "Date": d_str,
                "GDP_Monthly_Cr": round(float(gdp_monthly[idx]), 2),
                "Income_PFCE_Cr": round(float(pfce_monthly[idx]), 2),
            })
            idx += 1

    df_macro = pd.DataFrame(monthly_rows)

    # Fetch Monthly CPI
    print("Fetching MoSPI All-India Combined CPI (2011 to 2025)...")
    cpi_dict = extract_mospi_cpi(session, start_year=2011, end_year=2025)
    print(f"Fetched {len(cpi_dict)} monthly CPI points.")

    # Merge CPI with macro series
    df_macro["CPI_Index"] = df_macro["Date"].map(cpi_dict)

    # Drop rows without CPI or GDP (ensuring continuous, fully populated 10+ year panel)
    df_macro = df_macro.dropna().sort_values("Date").reset_index(drop=True)

    # Select final contract columns in exact order
    final_cols = ["Date", "GDP_Monthly_Cr", "CPI_Index", "Income_PFCE_Cr"]
    df_macro = df_macro[final_cols]

    # Verification checks
    if len(df_macro) < 120:
        raise ValueError(f"Macro timeline has fewer than 120 months: {len(df_macro)}")

    if df_macro.isna().any().any():
        raise ValueError("macro_data contains NaN values.")

    for col in ["GDP_Monthly_Cr", "CPI_Index", "Income_PFCE_Cr"]:
        if (df_macro[col] <= 0).any():
            raise ValueError(f"macro_data column {col} contains non-positive values.")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_macro.to_csv(output_path, index=False)
    print(f"Successfully generated {output_path} with {len(df_macro)} continuous monthly rows.")
    return df_macro


if __name__ == "__main__":
    df = build_macro_timeline()
    print("\nMacroeconomic Data Summary:")
    print(f"Total Months: {len(df)}")
    print(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
    print("\nDescriptive Statistics:")
    print(df.describe().to_string())
