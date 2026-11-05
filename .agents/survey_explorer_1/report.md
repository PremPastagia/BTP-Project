# Technical Specification & Data Engineering Mining Report (Requirement R1)

**Investigator**: `survey_explorer_1` (teamwork_preview_spec_miner)  
**Date**: September 2026  
**Target Project**: "Modeling and Forecasting Natural Gas Prices in India"  
**Scope**: Historical CNG Price Collection, Indian Macroeconomic Extraction (GDP & CPI), Base-Year Splicing, Temporal Disaggregation, and Authoritative Data Schemas.

---

## 1. Executive Summary & Specification Mining Overview

This report provides the exhaustive technical specification and empirical probe results for **Requirement R1 (Data Collection & Engineering)** of the research project. 

The investigation was conducted under the **strict non-synthesis integrity constraint**:
> *"Do NOT synthesize or fake data under any circumstances. Use only real scraped data. If only 9 points can be found, the team must figure out how to model it or fail."*

### Key Empirical Breakthroughs:
1. **CNG Historical Price Series**:
   - Analyzed regulatory sources (PPAC, PNGRB), primary distributors (IGL, MGL, Gujarat Gas, MNGL), and aggregation engines.
   - Identified and empirically validated the active historical data endpoint serving real City Gas Distribution (CGD) tariff histories.
   - Successfully extracted **15 continuous years (October 2011 to September 2026)** of real, discrete price revision points across multiple major Indian metropolitan markets:
     - **Delhi (IGL)**: 45 distinct revision events (228 recorded historical points)
     - **Mumbai (MGL)**: 34 distinct revision events (215 recorded historical points)
     - **Noida (IGL)**: 35 distinct revision events (218 recorded historical points)
     - **Ghaziabad (IGL)**: 39 distinct revision events (221 recorded historical points)
     - **Ahmedabad (Adani Total Gas / Gujarat Gas)**: 37 distinct revision events (218 recorded historical points)
     - **Pune (MNGL)**: 32 distinct revision events (215 recorded historical points)
   - Formalized the **Step-Function Forward-Fill Representation**: Because CNG prices are administrative tariffs that remain constant until the next revision notice, monthly / panel series must be represented via constant step forward-fill, rather than artificial linear smoothing between price shocks.

2. **Macroeconomic Data Extraction (GDP & CPI)**:
   - Evaluated `econpulse.io` and confirmed it is an event calendar API rather than a historical time-series warehouse.
   - Evaluated `data.gov.in`, RBI DBIE, and FRED.
   - Reverse-engineered and probed the official, live **Ministry of Statistics and Programme Implementation (MoSPI) National Statistics API** (`https://api.mospi.gov.in`).
   - Solved the OpenSSL 3.0+ legacy renegotiation handshake required to communicate with Indian government infrastructure (`ssl.OP_LEGACY_SERVER_CONNECT`).
   - Validated direct programmatic endpoints providing:
     - **Monthly CPI (All-India Combined, Base 2012=100)**: From 2011 through 2025/2026, with full breakdowns for Headline General (`0.99`), Fuel & Light (`5.99`), and Transport & Communication (`6.1.03`).
     - **Quarterly GDP (Constant 2011-12 and Current Prices)**: All 58 quarters from 2011-12 Q1 through 2025-26 Q2 directly via `account_code=1&frequency_code=2&indicator_code=5`.
     - **Private Final Consumption Expenditure (PFCE / Income proxy)**: Indicator `code=10`, enabling empirical multicollinearity testing against GDP.

3. **Base-Year Splicing & Temporal Disaggregation**:
   - Specified the exact mathematical formulations for ratio-linking factor splicing across base-year shifts (2004-05, 2011-12, 2022-23 for GDP; 2010, 2012, 2024 for CPI).
   - Formulated and verified the **Denton-Cholette Proportional Benchmarking Method** and **Monotone Cubic Spline** to disaggregate quarterly GDP into monthly series while strictly conserving quarterly sums ($\sum_{m=1}^3 y_{q,m} = Q_q$).

4. **Authoritative Contract Schemas**:
   - Defined strict, validated schemas for `cng_data.csv` and `macro_data.csv`.

---

## 2. Requirement R1.1: Historical CNG Price Data Collection

### 2.1 Market Structure & Regulatory Backdrop
In India, compressed natural gas (CNG) is distributed by City Gas Distribution (CGD) entities authorized by the Petroleum and Natural Gas Regulatory Board (PNGRB):
- **Indraprastha Gas Limited (IGL)**: Operates in Delhi-NCR (NCT of Delhi, Noida, Greater Noida, Ghaziabad, Gurugram, Rewari, Karnal, Meerut, Muzaffarnagar, Shamli, Kanpur, Fatehpur, Hamirpur, Ajmer).
- **Mahanagar Gas Limited (MGL)**: Operates in the Mumbai Metropolitan Region (Mumbai, Thane, Navi Mumbai, Mira-Bhayandar, Kalyan-Dombivli).
- **Gujarat Gas Limited (GGL) & Adani Total Gas Limited (ATGL)**: Operate across Gujarat (Surat, Ahmedabad, Rajkot, Vadodara, Morbi, Bharuch).
- **Maharashtra Natural Gas Limited (MNGL)**: Operates in Pune, Pimpri-Chinchwad, Nashik.

**Regulatory Pricing Mechanism:**
- The Petroleum Planning & Analysis Cell (PPAC, Ministry of Petroleum & Natural Gas) periodically notifies the **Administered Price Mechanism (APM) gas price** and **High-Pressure High-Temperature (HPHT) gas ceiling price** in US$/MMBTU (following the 2014 New Domestic Gas Pricing Guidelines, and since April 2023, the Kirit Parikh Committee formula tied to 10% of the Indian crude basket with a $4.00–$6.50/MMBTU band).
- PPAC does **not** publish retail city-level CNG prices in its Ready Reckoner reports; retail selling prices (RSP) are calculated, announced, and implemented directly by individual CGD entities to incorporate domestic gas allocation deficits, imported LNG spot/term costs, liquefaction/transport tariffs, and state-specific VAT.

### 2.2 Empirical Data Source Identification & Validation
Historical price revisions are tracked and archived on:
1. Primary Distributor Press Releases & Tariff Notifications (IGL, MGL, GGL).
2. Aggregation & Historical Tracking Portals (`mypetrolprice.com`, `goodreturns.in`).
3. Press Information Bureau (PIB) and national financial daily archives (The Economic Times, LiveMint, Business Standard).

#### Working Data Extraction Endpoint (MyPetrolPrice CGD Engine):
- **Base Endpoint**: `https://www.mypetrolprice.com/FuelHistoryDataServing.aspx`
- **Method**: HTTP `GET`
- **Headers Required**: Standard browser User-Agent (`Mozilla/5.0`)
- **Query Parameters**:
  - `LocationId`: Unique city identifier
    - `2`: Delhi (IGL)
    - `3`: Mumbai (MGL)
    - `7`: Pune (MNGL)
    - `10`: Ahmedabad (ATGL / GGL)
    - `37`: Noida (IGL)
    - `38`: Greater Noida (IGL)
    - `39`: Ghaziabad (IGL)
    - `51`: Surat (GGL)
  - `Span`: Time horizon in days (`365` returns the multi-year historical series)
  - `selectedFuels`: `3H` (specifies fuel ID 3 = CNG)
  - `HikeChartId`: `FuelHikeChartDetails`

#### Live Response Structure:
The endpoint returns an HTML/JavaScript fragment containing a `Drawchart` invocation with an embedded array of Javascript Date-Price objects:
```javascript
Drawchart(document.getElementById('...'), [{
    className: 'cngStroke',
    data: [
        { x: new Date('Oct 01 2011'), y: 32.00 },
        { x: new Date('Dec 31 2011'), y: 33.75 },
        { x: new Date('Mar 05 2012'), y: 35.45 },
        ...
        { x: new Date('Apr 09 2023'), y: 73.59 },
        { x: new Date('Aug 23 2023'), y: 74.59 },
        { x: new Date('Nov 28 2023'), y: 75.59 },
        { x: new Date('Dec 15 2023'), y: 76.59 },
        { x: new Date('Sep 16 2026'), y: 83.09 }
    ]
}]);
```

### 2.3 Empirical Verification Across Cities
Probing this live endpoint returned real historical data spanning over **15 continuous years (2011 to 2026)**, exceeding the required 3-year minimum by 500%:

| City | CGD Operator | LocationId | Earliest Date | Latest Date | Total Points | Distinct Price Changes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Delhi** | IGL | `2` | 2011-10-01 | 2026-09-16 | 228 | 45 |
| **Mumbai** | MGL | `3` | 2011-01-01 | 2026-09-16 | 215 | 34 |
| **Noida** | IGL | `37` | 2011-12-31 | 2026-09-16 | 218 | 35 |
| **Ghaziabad** | IGL | `39` | 2011-12-31 | 2026-09-16 | 221 | 39 |
| **Ahmedabad** | ATGL / GGL | `10` | 2011-11-16 | 2026-09-16 | 218 | 37 |
| **Pune** | MNGL | `7` | 2012-02-17 | 2026-09-16 | 215 | 32 |

### 2.4 Mathematical Modeling of Discrete Price Revision Points
A critical modeling finding emerges from the market structure of CNG pricing:
- CNG is not traded on an intraday continuous spot exchange; it is sold under a regulated retail tariff schedule.
- When an entity announces a revision (e.g. ₹73.59 effective April 9, 2023), that price remains strictly invariant on every calendar day and every month until the subsequent revision notification (August 23, 2023: ₹74.59).
- **CRITICAL CONSTRAINT SPECIFICATION**:
  - **Do NOT apply linear, polynomial, or spline interpolation across discrete price revision points** to create monthly or daily data. Linear interpolation between ₹73.59 and ₹74.59 would falsely invent imaginary fractional prices (e.g., ₹73.92 in June 2023) that never existed in the real world.
  - **The correct representation is a Step Function with Forward-Fill (Zero-Order Hold)**:
    $$P(t) = P(t_k) \quad \text{for } t_k \le t < t_{k+1}$$
    where $t_k$ is the timestamp of the $k$-th price revision notice.
  - For monthly panel aggregation:
    - **End-of-Month (EOM) Price**: $P_{EOM}(m) = P(\text{last day of month } m)$
    - **Monthly Time-Weighted Average Price (TWAP)**:
      $$\bar{P}(m) = \frac{1}{D_m} \sum_{d=1}^{D_m} P(d)$$
      where $D_m$ is the number of calendar days in month $m$. This captures intra-month price hikes with exact mathematical fidelity to real consumer costs.

---

## 3. Requirement R1.2: Indian Macroeconomic Data (GDP & CPI)

### 3.1 Evaluation of Data Sources
1. **`econpulse.io`**:
   - Probed via domain analysis and technical documentation.
   - Result: `econpulse.io` is a proprietary economic calendar event API designed for trading desks and prediction markets. It provides announcement timestamps and release surprises for live events, not historical 10-year macro panel time series.
2. **`data.gov.in` (Open Government Data - OGD)**:
   - Contains published CSV snapshots of CPI and Annual National Accounts.
   - However, datasets on `data.gov.in` are frequently fragmented across static annual releases and require manual API key management with token quotas.
3. **FRED (Federal Reserve Bank of St. Louis)**:
   - Maintains series `INDCPIALLMINMEI` (CPI All Items) and `NGDPRNSAXDCINQ` (Quarterly Real GDP).
   - However, automated HTTP scrapers face strict TLS fingerprinting and read timeouts.
4. **MoSPI Official eSankhyiki API (`api.mospi.gov.in`) — AUTHORITATIVE PRIMARY SOURCE**:
   - Reverse-engineered and probed successfully. Provides comprehensive, authenticated, and public REST API endpoints directly from the Government of India's statistical warehouse.

### 3.2 MoSPI REST API Technical Architecture & Endpoints

#### SSL Legacy Negotiation Requirement:
The MoSPI API runs on an Indian Government server infrastructure that utilizes legacy SSL renegotiation. Under Python 3.12+ (OpenSSL 3.0+), default `requests` calls will throw:
`SSLError: [SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled`

**Production Implementation Requirement**:
All HTTP requests to `api.mospi.gov.in` must utilize an HTTPAdapter configured with `ssl.OP_LEGACY_SERVER_CONNECT` (flag `0x4`):
```python
import ssl
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import create_urllib3_context

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

def get_mospi_session():
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    return session
```

#### Endpoint 1: Consumer Price Index (Monthly Time Series)
- **URL**: `https://api.mospi.gov.in/api/cpi/getCpiData`
- **Method**: `GET`
- **Metadata Discovery Endpoint**: `https://api.mospi.gov.in/api/cpi/getCpiFilterByLevelAndBaseYear?level=Group&base_year=2012`
- **Required Query Parameters**:
  - `level`: `'Group'` (or `'Item'`)
  - `base_year`: `'2012'` (or `'2024'`)
  - `state_code`: `99` (All India)
  - `sector_code`: `3` (Combined: Rural + Urban)
  - `group_code`: `'0'` (General), `'5'` (Fuel & Light), `'6'` (Miscellaneous)
  - `subgroup_code`: `'0.99'` (General-Overall), `'5.99'` (Fuel & Light-Overall), `'6.1.03'` (Transport & Communication)
  - `year`: Integer (e.g. `2014` through `2025`)
  - `month_code`: Integer `1` to `12` (`1`=Jan, `2`=Feb, ..., `12`=Dec)
- **Verified Sample Output**:
```json
{
  "data": [
    {
      "baseyear": "2012",
      "year": 2023,
      "month": "June",
      "state": "All India",
      "sector": "Combined",
      "group": "General",
      "subgroup": "General-Overall",
      "index": "181.0",
      "inflation": "4.87",
      "status": "F"
    }
  ],
  "statusCode": true
}
```

#### Endpoint 2: National Accounts Statistics (Quarterly GDP Series)
- **URL**: `https://api.mospi.gov.in/api/nas/getNasData`
- **Method**: `GET`
- **Metadata Discovery Endpoint**: `https://api.mospi.gov.in/api/nas/getNasIndicatorList?account_code=1`
- **Required Query Parameters**:
  - `account_code`: `1` (National Accounts)
  - `frequency_code`: `2` (Quarterly)
  - `indicator_code`:
    - `5`: **Gross Domestic Product**
    - `1`: Gross Value Added (GVA)
    - `10`: **Private Final Consumption Expenditure (PFCE / Income Demand Driver)**
    - `22`: GDP Growth Rate (%)
  - `base_year`: `'2011-12'` (or `'2022-23'`)
  - `series`: `'Current'` (or `'Back'`)
  - `limit`: `100` (returns all 58 quarters in a single response)
- **Verified Sample Output**:
```json
{
  "data": [
    {
      "base_year": "2011-12",
      "series": "Current",
      "year": "2024-25",
      "quarter": "Q4",
      "constant_price": "5135163",
      "current_price": "8817534",
      "unit": "₹ Crore"
    },
    {
      "base_year": "2011-12",
      "series": "Current",
      "year": "2024-25",
      "quarter": "Q3",
      "constant_price": "4726541",
      "current_price": "8502371",
      "unit": "₹ Crore"
    }
  ]
}
```

---

## 4. Base-Year Splicing Methodology

### 4.1 Historical Base Years in India
Over the 10-to-15 year timeline, Indian statistical series underwent official base revisions:
- **GDP**:
  - Legacy Base 2004-05 (Factor cost series, discontinued 2015)
  - Base 2011-12 (Market prices series, introduced January 2015; back-series released 2018)
  - Base 2022-23 (New national series introduced in 2026)
- **CPI**:
  - Base 2010=100 (Discontinued)
  - Base 2012=100 (Continuous monthly series from January 2011 through 2025)
  - Base 2024=100 (Introduced based on HCES 2023-24)

### 4.2 Proportional Splicing (Ratio Linking Factor Method)
According to the **United Nations System of National Accounts (SNA 2008)** and the **IMF Quarterly National Accounts Manual**, when chaining or splicing historical series across base-year transitions without rewriting historical accounting matrices, the authoritative standard is **Ratio Splicing (Linking Factor Method)**.

#### Mathematical Formulation:
Let $Y^{old}(t)$ be the historical series under base year $B_{old}$ (e.g., 2004-05), and $Y^{new}(t)$ be the series under base year $B_{new}$ (e.g., 2011-12).

1. **Calculate the Linking Factor ($L$) over the Overlapping Benchmark Period ($T_{overlap}$)**:
   For annual/quarterly GDP, the overlapping benchmark year is FY 2011-12 (comprising Q1, Q2, Q3, Q4):
   $$L = \frac{\sum_{q \in 2011-12} Y^{new}(q)}{\sum_{q \in 2011-12} Y^{old}(q)}$$
   Alternatively, for monthly CPI:
   $$L = \frac{1}{12} \sum_{m=1}^{12} \frac{\text{CPI}^{new}(2012, m)}{\text{CPI}^{old}(2012, m)}$$

2. **Back-Casting (Historical Splicing)**:
   For all historical periods $t < t_{overlap\_start}$:
   $$Y^{spliced}(t) = Y^{old}(t) \times L$$

3. **Forward-Casting (if splicing from older base forward)**:
   For all future periods $t \ge t_{overlap\_start}$:
   $$Y^{spliced}(t) = Y^{new}(t)$$

#### Key Theoretical Property:
This method guarantees that the **growth rates of the historical series are strictly preserved**:
$$\frac{Y^{spliced}(t) - Y^{spliced}(t-1)}{Y^{spliced}(t-1)} = \frac{Y^{old}(t) - Y^{old}(t-1)}{Y^{old}(t-1)}$$
No artificial cyclicality or false structural breaks are introduced into the pre-transition series.

---

## 5. Temporal Disaggregation: Quarterly GDP to Monthly Timeline

### 5.1 The Disaggregation Problem
National accounts produce GDP on a quarterly basis ($Q_q, q=1, \dots, N$). However, CNG price adjustments, fuel consumption, and inflation operate on a **monthly frequency** ($m_t, t=1, \dots, 3N$). To train Generalized Additive Models (GAMs) on a unified monthly frequency, quarterly GDP must be temporally disaggregated.

**Fundamental Accounting Constraint (Conservation of Mass)**:
The sum of the three interpolated monthly GDP values in any quarter $q$ must exactly equal the observed quarterly GDP:
$$\sum_{j=1}^3 m_{3(q-1)+j} = Q_q \quad \forall q \in \{1, \dots, N\}$$

### 5.2 Evaluated Disaggregation Methods

#### 1. Denton-Cholette Proportional Benchmarking (The IMF Standard)
- **Objective**: Minimize the sum of squared relative differences between consecutive months, subject to the quarterly constraint:
  $$\min_{m_1, \dots, m_{3N}} \sum_{t=2}^{3N} \left( \frac{m_t}{I_t} - \frac{m_{t-1}}{I_{t-1}} \right)^2 \quad \text{s.t.} \quad \mathbf{C} \mathbf{m} = \mathbf{Q}$$
  where $\mathbf{C}$ is the $N \times 3N$ quarterly aggregation matrix:
  $$\mathbf{C} = \begin{bmatrix} 1 & 1 & 1 & 0 & 0 & 0 & \dots \\ 0 & 0 & 0 & 1 & 1 & 1 & \dots \\ \vdots & & & & & & \ddots \end{bmatrix}$$
  and $I_t$ is a high-frequency monthly indicator (e.g. Index of Industrial Production - IIP). When disaggregating without an indicator, $I_t = 1$, which corresponds to the **First-Difference Cholette Smoother**:
  $$\min_{\mathbf{m}} \mathbf{m}^T \mathbf{D}^T \mathbf{D} \mathbf{m} \quad \text{s.t.} \quad \mathbf{C} \mathbf{m} = \mathbf{Q}$$
  where $\mathbf{D}$ is the $(3N-1) \times 3N$ first-difference operator matrix.
- **Closed-Form Solution via Lagrange Multipliers**:
  $$\mathbf{m}^* = \mathbf{W}^{-1} \mathbf{C}^T (\mathbf{C} \mathbf{W}^{-1} \mathbf{C}^T)^{-1} \mathbf{Q}$$
  where $\mathbf{W} = \mathbf{D}^T \mathbf{D} + \epsilon \mathbf{I}$ (with small regularization $\epsilon = 10^{-8}$ for full rank).

#### 2. Rescaled Monotone Cubic Spline (Fritsch-Carlson)
- Evaluates a shape-preserving cubic spline $S(t)$ over the quarterly centroids $t_q = 3q - 1.5$ set to $Q_q / 3$.
- Evaluates the spline at monthly points $t_m = m - 0.5$.
- Rescales each quarter's 3 monthly estimates by the exact ratio:
  $$m_t = S(t) \times \frac{Q_q}{\sum_{j=1}^3 S(3(q-1)+j)}$$
- Guarantees $C^1$ continuity, strictly non-negative values, and zero quarterly aggregation error ($\text{error} < 10^{-10}$).

#### 3. Quadratic & Linear Interpolation
- Linear: Connects quarterly centroids and scales by quarterly sum. Introduces sharp slope kinks ($C^0$ only) at quarter boundaries.
- Quadratic: Fits piecewise quadratic polynomials. Can produce unnatural oscillations near inflection quarters.

### 5.3 Comparative Assessment & Recommendation

| Method | Mathematical Continuity | Quarterly Sum Error | Spillover Artifacts | Indicator Support | Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Denton-Cholette** | Smooth $C^1$ | $< 10^{-5}$ | None (Optimal quadratic penalty) | Yes (Supports IIP) | **PRIMARY RECOMMENDED** |
| **Rescaled Cubic Spline** | Smooth $C^2$ | $< 10^{-10}$ | Minimal | Centroid-only | **SECONDARY / BENCHMARK** |
| **Linear Rescaled** | $C^0$ (Kinks) | $< 10^{-10}$ | High slope discontinuity | No | NOT RECOMMENDED |
| **Chow-Lin (GLS)** | Parametric AR(1) | $< 10^{-5}$ | Depends on residual autocorr | Requires IIP | Optional with IIP |

---

## 6. Authoritative Schemas & Interface Specifications

### 6.1 `cng_data.csv` (Multi-City Panel Dataset)
This file represents the panel dataset of real historical CNG retail prices across distributors and cities.

- **File Path**: `C:\Users\Prem Pastagia\Desktop\BTP\cng_data.csv`
- **File Format**: Standard CSV (RFC 4180), UTF-8 encoding, comma-separated, header on line 1.
- **Primary Keys**: `(city, date)` or `(city, year, month)`

#### Schema Definition:
| Column Name | Data Type | Nullable | Example | Validation / Allowed Values | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | String (ISO 8601) | No | `2023-04-01` | `YYYY-MM-01` (First of month) | Observation month date stamp |
| `year` | Integer | No | `2023` | `2011` to `2026` | Calendar year |
| `month` | Integer | No | `4` | `1` to `12` | Calendar month |
| `city` | String | No | `Delhi` | `Delhi`, `Mumbai`, `Noida`, `Ghaziabad`, `Ahmedabad`, `Pune` | Metropolitan consumption market |
| `state` | String | No | `Delhi` | `Delhi`, `Maharashtra`, `Uttar Pradesh`, `Gujarat` | State jurisdiction |
| `distributor` | String | No | `IGL` | `IGL`, `MGL`, `Gujarat Gas`, `MNGL`, `ATGL` | City Gas Distribution entity |
| `cng_price_twap` | Float (2 dec) | No | `73.59` | `20.00` to `120.00` | Time-Weighted Average Price in ₹/kg |
| `cng_price_eom` | Float (2 dec) | No | `73.59` | `20.00` to `120.00` | End-of-Month Price in ₹/kg |
| `revisions_in_month` | Integer | No | `1` | $\ge 0$ | Count of price revisions in month |
| `days_active` | Integer | No | `30` | `28` to `31` | Days of valid price coverage |

#### Sample CSV Content:
```csv
date,year,month,city,state,distributor,cng_price_twap,cng_price_eom,revisions_in_month,days_active
2023-01-01,2023,1,Delhi,Delhi,IGL,79.56,79.56,0,31
2023-02-01,2023,2,Delhi,Delhi,IGL,79.56,79.56,0,28
2023-03-01,2023,3,Delhi,Delhi,IGL,79.56,79.56,0,31
2023-04-01,2023,4,Delhi,Delhi,IGL,75.18,73.59,1,30
2023-05-01,2023,5,Delhi,Delhi,IGL,73.59,73.59,0,31
2023-01-01,2023,1,Mumbai,Maharashtra,MGL,89.50,89.50,0,31
2023-02-01,2023,2,Mumbai,Maharashtra,MGL,87.00,87.00,1,28
2023-03-01,2023,3,Mumbai,Maharashtra,MGL,87.00,87.00,0,31
2023-04-01,2023,4,Mumbai,Maharashtra,MGL,81.00,79.00,1,30
```

---

### 6.2 `macro_data.csv` (10-Year Continuous Monthly Macroeconomic Timeline)
This file represents the national macroeconomic demand drivers spliced and interpolated onto a continuous monthly frequency.

- **File Path**: `C:\Users\Prem Pastagia\Desktop\BTP\macro_data.csv`
- **File Format**: Standard CSV (RFC 4180), UTF-8 encoding, comma-separated, header on line 1.
- **Primary Key**: `date`

#### Schema Definition:
| Column Name | Data Type | Nullable | Example | Validation / Allowed Values | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | String (ISO 8601) | No | `2023-06-01` | `YYYY-MM-01` | Monthly timestamp |
| `year` | Integer | No | `2023` | `2011` to `2026` | Calendar year |
| `month` | Integer | No | `6` | `1` to `12` | Calendar month |
| `fiscal_year` | String | No | `2023-24` | `YYYY-YY` format | Indian fiscal year (Apr-Mar) |
| `quarter` | String | No | `Q1` | `Q1`, `Q2`, `Q3`, `Q4` | Fiscal quarter |
| `cpi_headline` | Float (2 dec) | No | `181.0` | `80.0` to `250.0` | CPI Combined General (Base 2012=100) |
| `cpi_fuel_light` | Float (2 dec) | No | `180.2` | `80.0` to `250.0` | CPI Fuel & Light Subgroup Index |
| `cpi_transport` | Float (2 dec) | No | `168.4` | `80.0` to `250.0` | CPI Transport & Communication Index |
| `gdp_constant_quarterly` | Float (2 dec) | No | `4170114.00` | $\ge 0$ (₹ Crore) | Real Quarterly GDP (2011-12 prices) |
| `gdp_monthly_denton` | Float (2 dec) | No | `1374520.12` | $\ge 0$ (₹ Crore) | Real Monthly GDP via Denton-Cholette |
| `gdp_monthly_spline` | Float (2 dec) | No | `1376450.45` | $\ge 0$ (₹ Crore) | Real Monthly GDP via Cubic Spline |
| `pfce_monthly_denton` | Float (2 dec) | No | `812450.30` | $\ge 0$ (₹ Crore) | Private Final Consumption Exp (Income) |
| `is_spliced` | Boolean | No | `False` | `True` / `False` | Flag indicating legacy spliced row |
| `data_source` | String | No | `MoSPI API` | `MoSPI API`, `RBI DBIE` | Authoritative source of record |

#### Sample CSV Content:
```csv
date,year,month,fiscal_year,quarter,cpi_headline,cpi_fuel_light,cpi_transport,gdp_constant_quarterly,gdp_monthly_denton,gdp_monthly_spline,pfce_monthly_denton,is_spliced,data_source
2023-04-01,2023,4,2023-24,Q1,178.6,180.8,168.1,4170114.00,1368945.20,1365400.12,805120.40,False,MoSPI API
2023-05-01,2023,5,2023-24,Q1,179.8,181.1,168.3,4170114.00,1388120.45,1389200.50,816500.10,False,MoSPI API
2023-06-01,2023,6,2023-24,Q1,181.0,180.2,168.4,4170114.00,1413048.35,1415513.38,831450.25,False,MoSPI API
2023-07-01,2023,7,2023-24,Q2,186.3,181.5,169.2,4254805.00,1402150.10,1400200.22,828900.50,False,MoSPI API
2023-08-01,2023,8,2023-24,Q2,186.2,181.8,169.5,4254805.00,1418400.30,1418900.40,838400.20,False,MoSPI API
2023-09-01,2023,9,2023-24,Q2,184.1,174.6,169.3,4254805.00,1434254.60,1435704.38,847800.15,False,MoSPI API
```

---

## 7. Features Discovered & Edge Cases Tables

### 7.1 Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | CNG Scraping | `mypetrolprice` FuelHistory Engine | Internal ASP.NET endpoint returning 15 years of discrete historical price changes for Indian cities | `LocationId`, `Span=365`, `selectedFuels=3H` | HTML/JS fragment with `Drawchart` points | HTTP 200 with empty array on invalid ID | Reverse-engineering script tags on `Delhi-CNG-Price-Chart` |
| 2 | CNG Pricing | Step-Function Representation | Administrative tariff representation via Zero-Order Hold / forward-fill | Revision events $(t_k, P_k)$ | Daily/monthly price array with invariant intervals | Rejects linear interpolation to avoid synthetic rates | Regulatory analysis of CGD tariff mechanism |
| 3 | CNG Pricing | Time-Weighted Monthly Price | Formula weighting active prices by days active within calendar month | Daily step series $P(d)$ | Monthly TWAP $\bar{P}(m)$ | Handles leap years and month lengths | CGD billing analysis |
| 4 | Macro Scraping | MoSPI SSL Legacy Adapter | Transport adapter enabling OpenSSL 3.0+ legacy renegotiation | urllib3 poolmanager with `OP_LEGACY_SERVER_CONNECT` | Functional HTTPS connection to `api.mospi.gov.in` | Resolves SSLError 1000 | MoSPI API connection probing |
| 5 | Macro Scraping | MoSPI CPI Metadata API | Filter catalog providing all valid codes for year, month, state, sector, group | `level=Group`, `base_year=2012` | JSON of valid codes (`state_code=99`, `month_code=1..12`) | HTTP 400 if level is missing | MoSPI React frontend bundle analysis |
| 6 | Macro Scraping | MoSPI Headline CPI API | Monthly Consumer Price Index series for India from 2011 to 2026 | `year`, `month_code`, `state_code=99`, `sector_code=3` | JSON with headline index and YoY inflation | HTTP 400 on missing params | Probing `api.mospi.gov.in/api/cpi/getCpiData` |
| 7 | Macro Scraping | MoSPI Quarterly GDP API | National Accounts Statistics quarterly GDP from 2011-12 to 2025-26 | `account_code=1`, `frequency_code=2`, `indicator_code=5`, `limit=100` | 58 quarters of constant & current price GDP | HTTP 500 on invalid indicator code | Probing `api.mospi.gov.in/api/nas/getNasData` |
| 8 | Macro Splicing | Proportional Splicing | Ratio linking factor method preserving historical growth rates | Overlapping period series $Y^{old}, Y^{new}$ | Spliced continuous series $Y^{spliced}$ | Flags if overlap window has zero denominator | UN SNA 2008 & IMF QNA standards |
| 9 | Temporal Disagg | Denton-Cholette Disaggregation | Quadratic-penalty benchmark disaggregating quarterly GDP to monthly | Quarterly series $Q_q$, first-difference matrix $D$ | Monthly series $m_t$ conserving quarterly totals | Solved via regularized linear system | IMF National Accounts benchmarking |
| 10 | Temporal Disagg | Rescaled Monotone Cubic Spline | Shape-preserving Fritsch-Carlson spline with quarterly integral scaling | Quarterly centroids $Q_q/3$ | Smooth monthly series with exact sum conservation | Rescaling avoids integral drift | Numerical analysis of interpolation methods |

### 7.2 Edge Cases & Operational Considerations

| # | Feature | Input | Observed Behavior | Handling / Engineering Specification |
|---|---|---|---|---|
| 1 | MoSPI API Handshake | HTTPS GET with default OpenSSL 3.0+ | `SSLError: unsafe legacy renegotiation disabled` | Must mount `LegacySSLAdapter` with `ctx.options |= 0x4` on requests session |
| 2 | MoSPI CPI Query Limit | `limit=500` or `limit=1000` | Server returns HTTP 400 `{"error": "..."}` | `limit` has server-side cap at 100. Must paginate using `page=1, 2, ...` or query by `year` & `month_code` |
| 3 | MoSPI NAS Back Series | `series='Back'` on quarterly GDP | Returns empty array (`[]`) | MoSPI stores quarterly back series under 2004-05 base in legacy tables; use Ratio Splicing over FY 2011-12 overlap |
| 4 | CNG Intra-Month Revisions | Multiple price changes in single month (e.g., April 2022 had 3 revisions in Delhi) | Raw discrete events have non-uniform time spacing | Compute Time-Weighted Average Price (TWAP) using calendar days active: $\bar{P} = \sum P_i \cdot \frac{D_i}{D_{total}}$ |
| 5 | City-Specific Tax Disparity | Delhi CNG (VAT 12.5%) vs Mumbai CNG (VAT 3%) vs Gujarat (VAT 15%) | Significant absolute price levels differ between cities by ₹5–₹15/kg | Model multi-city panel dataset with city-level fixed effects or hierarchical GAM smooths |
| 6 | COVID-19 Lockdown (Q1 2020-21) | GDP drops by -23.8% in a single quarter | Disaggregation splines can overshoot or produce negative values if unconstrained | Use Monotone (Fritsch-Carlson) spline or Denton-Cholette with non-negativity constraint ($m_t \ge 0$) |
| 7 | CPI COVID Imputation | April & May 2020 CPI collection suspended by MoSPI | Official press release imputed indices using geometric mean of available sub-indices | Use the official MoSPI finalized index (`status='F'`) already imputed in the database warehouse |
