import requests, ssl, calendar
import numpy as np
import pandas as pd
from datetime import datetime, date
from scipy.interpolate import PchipInterpolator
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.options |= 0x4
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

def get_session():
    s = requests.Session()
    s.mount('https://', LegacySSLAdapter())
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return s

def denton_cholette(quarterly_values, indicator=None, epsilon=1e-8):
    """
    Denton-Cholette temporal disaggregation from quarterly to monthly.
    Strictly preserves quarterly totals: sum(m[3q : 3q+3]) == Q[q].
    """
    N = len(quarterly_values)
    M = 3 * N
    Q = np.asarray(quarterly_values, dtype=float)
    
    # Quarterly aggregation matrix C (N x 3N)
    C = np.zeros((N, M))
    for q in range(N):
        C[q, 3*q : 3*q + 3] = 1.0
        
    # First difference matrix D ((3N-1) x 3N)
    D = np.zeros((M - 1, M))
    for i in range(M - 1):
        D[i, i] = -1.0
        D[i, i + 1] = 1.0
        
    if indicator is None:
        # Standard Denton without indicator
        W = D.T @ D + epsilon * np.eye(M)
        W_inv = np.linalg.inv(W)
        CW_inv = C @ W_inv
        CW_inv_CT = CW_inv @ C.T
        CW_inv_CT_inv = np.linalg.inv(CW_inv_CT)
        m = W_inv @ C.T @ CW_inv_CT_inv @ Q
    else:
        # Proportional Denton with indicator
        I = np.asarray(indicator, dtype=float)
        P = np.diag(I)
        CP = C @ P
        W = D.T @ D + epsilon * np.eye(M)
        W_inv = np.linalg.inv(W)
        CPW_inv = CP @ W_inv
        denom = CPW_inv @ CP.T
        z = W_inv @ CP.T @ np.linalg.inv(denom) @ Q
        m = P @ z
        
    return m

def rescaled_monotone_spline(quarterly_values):
    """
    Fritsch-Carlson monotone cubic spline interpolation rescaled to preserve quarterly sums.
    """
    N = len(quarterly_values)
    Q = np.asarray(quarterly_values, dtype=float)
    
    # Place quarterly observations at quarter centroids: 1.5, 4.5, 7.5, ...
    t_q = np.arange(N) * 3.0 + 1.5
    y_q = Q / 3.0
    
    # Fit PCHIP (Piecewise Cubic Hermite Interpolating Polynomial)
    pchip = PchipInterpolator(t_q, y_q)
    
    # Evaluate at monthly grid: 0.5, 1.5, 2.5, ...
    t_m = np.arange(3 * N) + 0.5
    raw_m = pchip(t_m)
    
    # Rescale within each quarter to guarantee exact sum conservation
    m = np.zeros_like(raw_m)
    for q in range(N):
        idx = slice(3 * q, 3 * q + 3)
        q_sum = np.sum(raw_m[idx])
        if q_sum != 0:
            m[idx] = raw_m[idx] * (Q[q] / q_sum)
        else:
            m[idx] = Q[q] / 3.0
            
    return m

# Test algorithms
s = get_session()
print("Extracting GDP...")
r_gdp = s.get('https://api.mospi.gov.in/api/nas/getNasData?account_code=1&frequency_code=2&indicator_code=5&base_year=2011-12&series=Current&limit=100', timeout=20)
gdp_data = r_gdp.json().get('data', [])
print(f"Extracted {len(gdp_data)} GDP quarters.")

# Sort chronologically
# Quarters are named e.g. '2011-12' 'Q1'
def parse_fy_quarter(item):
    fy = item['year'] # '2011-12'
    q = item['quarter'] # 'Q1'
    start_year = int(fy.split('-')[0])
    q_num = int(q[1])
    # Q1: Apr-Jun (year = start_year)
    # Q2: Jul-Sep (year = start_year)
    # Q3: Oct-Dec (year = start_year)
    # Q4: Jan-Mar (year = start_year + 1)
    cal_year = start_year if q_num in (1, 2, 3) else start_year + 1
    start_month = {1: 4, 2: 7, 3: 10, 4: 1}[q_num]
    return (cal_year, start_month, q_num, start_year)

gdp_sorted = sorted(gdp_data, key=parse_fy_quarter)
print(f"Earliest GDP: {gdp_sorted[0]['year']} {gdp_sorted[0]['quarter']}, Latest: {gdp_sorted[-1]['year']} {gdp_sorted[-1]['quarter']}")

q_vals = [float(x['constant_price']) for x in gdp_sorted]
m_denton = denton_cholette(q_vals)
m_spline = rescaled_monotone_spline(q_vals)

# Check sum conservation
N = len(q_vals)
max_err_denton = max(abs(sum(m_denton[3*q : 3*q+3]) - q_vals[q]) for q in range(N))
max_err_spline = max(abs(sum(m_spline[3*q : 3*q+3]) - q_vals[q]) for q in range(N))
print(f"Max quarterly sum error (Denton): {max_err_denton:.8e}")
print(f"Max quarterly sum error (Spline): {max_err_spline:.8e}")
print(f"Denton min={m_denton.min():.2f}, max={m_denton.max():.2f}")
print(f"Spline min={m_spline.min():.2f}, max={m_spline.max():.2f}")
