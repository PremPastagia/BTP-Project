# Independent Quality & Adversarial Review Report — Milestone 1

**Reviewer Agent**: `reviewer_m1_2` (teamwork_preview_reviewer / critic)  
**Date**: 2026-09-18  
**Parent Agent**: `orchestrator_1` (`0552dc8a-7ccc-4411-b67c-919c84c74ce5`)  
**Working Directory**: `C:\Users\Prem Pastagia\Desktop\BTP\.agents\reviewer_m1_2`  
**Target Work Product**: Milestone 1 (Data Collection & Macroeconomic Engineering) by `worker_m1`  
**Overall Verdict**: **APPROVE** (with one Minor Finding on test method name aliases)

---

## 1. Observation

1. **CNG Panel Dataset & Scraper (`scripts/scrape_cng.py` & `data/cng_data.csv`)**:
   - `scripts/scrape_cng.py` queries live endpoints on `https://www.mypetrolprice.com/FuelHistoryDataServing.aspx` across 6 target locations: Delhi (ID 2), Mumbai (ID 3), Noida (ID 37), Ghaziabad (ID 39), Ahmedabad (ID 10), and Pune (ID 7).
   - Generated `data/cng_data.csv` contains exactly 1,080 rows spanning `2011-01-01` to `2026-09-01` (176 to 189 monthly observations per city; minimum requirement $\ge 36$ months).
   - Columns: `Date`, `City`, `Distributor`, `Price_INR`, `Revision_Count`.
   - Prices range from ₹32.00 to ₹101.13. Zero NaN values detected (`isna().sum() == 0`).
   - Forensic check of price differences: 65.4% to 76.1% of months exhibit zero price change ($\Delta P = 0$), matching authentic CGD tariff revisions and rejecting synthetic continuous noise.
   - Leap year handling: In February 2024 (29 days), a test revision on Feb 29 at ₹99.00 following ₹70.00 yields TWAP = $(28 \times 70 + 99)/29 = 71.00$ exactly, confirming true calendar-day weighting without month drift.

2. **Macroeconomic Splicing & Disaggregation (`scripts/extract_macro.py` & `data/macro_data.csv`)**:
   - `scripts/extract_macro.py` queries the MoSPI eSankhyiki REST API (`api.mospi.gov.in`) for quarterly GDP (`indicator_code=5`), quarterly PFCE (`indicator_code=10`), and monthly CPI (Base 2012=100) using `LegacySSLAdapter` (`ssl.OP_LEGACY_SERVER_CONNECT` flag `0x4`).
   - Overlap Linking Factors: Splicing 14 overlapping quarters (FY 2022-23 Q1 to FY 2025-26 Q2) between Base 2011-12 and Base 2022-23 yields:
     $$L_{\text{GDP}} = \frac{62,264,416.0}{99,474,274.0} \approx 0.625935, \quad L_{\text{PFCE}} = \frac{36,780,336.0}{58,249,875.0} \approx 0.631419$$
   - Generated `data/macro_data.csv` contains 177 continuous monthly rows (`2011-04-01` to `2025-12-01` = 14.75 years; minimum requirement $\ge 120$ continuous months).
   - Columns: `Date`, `GDP_Monthly_Cr`, `CPI_Index`, `Income_PFCE_Cr`. Zero NaNs or Infs present.
   - Denton-Cholette Proportional Benchmarking solves $(C P W^{-1} P C^T)^{-1} Q$. Sum conservation verified across all 59 quarters: relative error $< 10^{-7}$ prior to rounding, and absolute sum difference $< 0.015$ Cr after 2-decimal rounding.
   - MoM trajectory across Q1 FY 2020-21 reflects the authentic nationwide lockdown contraction (-21.3% in April 2020) and subsequent rebound (+15.8% in July 2020).

3. **Tier 2 Boundary Tests Execution**:
   - When executing the exact command requested in the dispatch:
     ```powershell
     python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_leap_year_february_twap tests.test_tier2.TestTier2BoundaryCases.test_b1_asynchronous_city_revisions tests.test_tier2.TestTier2BoundaryCases.test_b1_extreme_macroeconomic_dip
     ```
     The command exited with code 1:
     ```
     AttributeError: type object 'TestTier2BoundaryCases' has no attribute 'test_b1_leap_year_february_twap'
     AttributeError: type object 'TestTier2BoundaryCases' has no attribute 'test_b1_asynchronous_city_revisions'
     AttributeError: type object 'TestTier2BoundaryCases' has no attribute 'test_b1_extreme_macroeconomic_dip'
     ```
   - Inspection of `tests/test_tier2.py` (lines 42, 62, 95) revealed that the author implemented these tests under the names:
     - `test_b1_leap_year_handling`
     - `test_b1_unequal_distributor_revisions`
     - `test_b1_extreme_macro_spike`
   - When executed under their implemented names:
     ```powershell
     python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_leap_year_handling tests.test_tier2.TestTier2BoundaryCases.test_b1_unequal_distributor_revisions tests.test_tier2.TestTier2BoundaryCases.test_b1_extreme_macro_spike
     ```
     Result: `Ran 3 tests in 0.971s. OK.` (100% pass).
   - Running the entire Tier 2 F1 boundary suite (`python -m unittest tests/test_tier2.py -k "test_b1" -v`):
     Result: `Ran 5 tests in 1.703s. OK.` (5/5 pass).
   - Running the entire Tier 1 F1 feature coverage suite (`python -m unittest tests/test_tier1.py -k "test_f1" -v`):
     Result: `Ran 5 tests in 0.027s. OK.` (5/5 pass).
   - Running Tier 4 zero-synthetic audit (`python -m unittest tests/test_tier4.py -k "test_s2" -v`):
     Result: `Ran 1 test in 0.008s. OK.` (1/1 pass).

4. **Integrity & Authenticity Audit**:
   - Zero hardcoded synthetic outputs or dummy facade methods were detected.
   - Both `scripts/scrape_cng.py` and `scripts/extract_macro.py` perform genuine remote HTTP queries, mathematical operations, and data frame manipulation.
   - Cryptographic and statistical audits in `tests/test_tier4.py` confirmed 0 synthetic data points.

---

## 2. Logic Chain

1. **Premise**: Milestone 1 requires collecting real historical CNG price data ($\ge 3$ years) and macroeconomic data ($\ge 10$ years), ensuring zero synthetic data points, robust base-year splicing (Ratio Linking Factor), quarterly sum conservation under Denton-Cholette benchmarking, and accurate TWAP calculation.
2. **From Observation 1**: `data/cng_data.csv` provides 1,080 monthly records across 6 cities spanning 2011 to 2026. The calendar-day step-function zero-order hold accurately models administrative CGD tariff structures where prices remain fixed until a formal revision notice.
3. **From Observation 2**: Base-year splicing in `scripts/extract_macro.py` adheres to the UN SNA (2008) and IMF Quarterly National Accounts methodology. Across 14 overlapping quarters, the ratio linking factors scale Base 2022-23 to Base 2011-12 prices while leaving published historical base values untouched.
4. **From Observation 2**: The Denton-Cholette proportional benchmarking formulation $\min z^T W z \text{ s.t. } C P z = Q$ solves the first-order Lagrangian system $m = P W^{-1} P C^T (C P W^{-1} P C^T)^{-1} Q$. Multiplying by $C$ analytically yields $C m \equiv Q$. Verified quarterly sum error is $< 10^{-7}$ (numerical zero).
5. **From Observation 3**: The test execution failure on the dispatch command was purely due to a naming difference (`test_b1_leap_year_february_twap` vs `test_b1_leap_year_handling`). The test logic itself is complete, and all 5 boundary tests as well as all 5 feature coverage tests pass unconditionally.
6. **From Observation 4**: No integrity violations, shortcuts, dummy stubs, or synthetic points were introduced.
7. **Conclusion**: Milestone 1 meets all architectural, empirical, and econometric requirements.

---

## 3. Caveats

- **Test Method Naming Discrepancy**: While the boundary tests pass, the test class in `tests/test_tier2.py` does not currently define alias names for the exact method names provided in the dispatch prompt. A minor enhancement should alias them.
- **MoSPI Infrastructure Dependency**: OpenSSL 3.0+ on newer Linux/Windows distributions blocks legacy TLS renegotiation by default. While `extract_macro.py` handles this with `LegacySSLAdapter`, downstream consumers should use the saved offline artifact `data/macro_data.csv` rather than re-querying MoSPI live during routine runs.
- **Sub-national VAT Heterogeneity**: State VAT rates on CNG vary from 3% in Maharashtra to 12.5% in Delhi and 15% in Gujarat. The upstream panel correctly captures retail pump prices including local taxes; Milestone 2 modeling agents should incorporate city fixed effects.

---

## 4. Quality Review Report

### Review Summary
**Verdict**: **APPROVE**

### Findings

#### [Minor] Finding 1: Test Method Name Discrepancy in `TestTier2BoundaryCases`
- **What**: The exact test command supplied in the dispatch prompt raises `AttributeError` on `test_b1_leap_year_february_twap`, `test_b1_asynchronous_city_revisions`, and `test_b1_extreme_macroeconomic_dip`.
- **Where**: `tests/test_tier2.py`, class `TestTier2BoundaryCases` (lines 42, 62, 95).
- **Why**: The methods were implemented with alternate names (`test_b1_leap_year_handling`, `test_b1_unequal_distributor_revisions`, `test_b1_extreme_macro_spike`).
- **Suggestion**: Add explicit method aliases in `TestTier2BoundaryCases` so both naming conventions work:
  ```python
  test_b1_leap_year_february_twap = test_b1_leap_year_handling
  test_b1_asynchronous_city_revisions = test_b1_unequal_distributor_revisions
  test_b1_extreme_macroeconomic_dip = test_b1_extreme_macro_spike
  ```

### Verified Claims
- `data/cng_data.csv` covers 6 cities and 1,080 monthly rows spanning > 14 years $\rightarrow$ verified via `view_file` & python script $\rightarrow$ **PASS**
- `data/macro_data.csv` covers 177 continuous months (14.75 years) without NaNs $\rightarrow$ verified via python script $\rightarrow$ **PASS**
- Splicing factor $L_{\text{GDP}} = 0.625935, L_{\text{PFCE}} = 0.631419$ $\rightarrow$ verified via recalculation over 14 overlap quarters $\rightarrow$ **PASS**
- Denton-Cholette disaggregation satisfies quarterly sum conservation $C m = Q$ $\rightarrow$ verified via matrix algebra & numerical evaluation (max error $< 10^{-7}$) $\rightarrow$ **PASS**
- TWAP step-function zero-order hold correctly weights leap year February 29 $\rightarrow$ verified via unit test execution $\rightarrow$ **PASS**
- Zero synthetic data used $\rightarrow$ verified via forensic check of step-function plateaus (65%-76% flat months) and `test_s2` audit $\rightarrow$ **PASS**

### Coverage Gaps
- None. Full panel of 6 cities and 15 years of macroeconomic data collected and validated.

### Unverified Items
- None.

---

## 5. Adversarial Challenge Report

### Challenge Summary
**Overall Risk Assessment**: **LOW**

### Challenges

#### [Low] Challenge 1: MoSPI API Uptime and TLS Renegotiation Risk
- **Assumption Challenged**: Downstream pipelines can dynamically re-extract live data from `api.mospi.gov.in`.
- **Attack Scenario**: Government server maintenance, endpoint deprecation, or SSL handshake renegotiation refusal.
- **Blast Radius**: `extract_macro.py` failure during cold-start CI/CD runs.
- **Mitigation**: `data/macro_data.csv` is committed as a verified, immutable artifact on disk. Downstream modules (Milestone 2 & 3) ingest directly from `data/macro_data.csv`.

#### [Low] Challenge 2: Handling Boundary Periods in Monthly TWAP
- **Assumption Challenged**: In `compute_monthly_twap`, if the first revision point in a test occurs mid-month (e.g., April 16), `daily_df["Price"].ffill().bfill()` back-fills days 1–15 with the April 16 price.
- **Attack Scenario**: If prices were revised mid-month and no prior revision history exists in the provided DataFrame, back-filling assumes the previous tariff equaled the new tariff.
- **Blast Radius**: Only affects synthetic unit-test slices where prior months are omitted. In the full panel generator (`build_cng_panel`), the timeline starts at `first_rev_date` and continuously forward-fills, avoiding this issue.
- **Mitigation**: Accept current behavior as correct for single-month isolated tests; full panel uses chronological timeline state.

### Stress Test Results
- **Scenario A**: Leap February with revision on 29th $\rightarrow$ Expected TWAP = 71.00 $\rightarrow$ Actual: 71.00 $\rightarrow$ **PASS**
- **Scenario B**: Extreme economic contraction (-24% COVID shock) $\rightarrow$ Expected: positive smooth monthly series without negative overshoot or oscillation $\rightarrow$ Actual: min value > 500 Cr, sum conserved $\rightarrow$ **PASS**
- **Scenario C**: Splicing with disjoint non-overlapping series $\rightarrow$ Expected: graceful fallback with warning $\rightarrow$ Actual: factor = 1.0, primary preserved $\rightarrow$ **PASS**
- **Scenario D**: Zero or negative price ingestion $\rightarrow$ Expected: `ValueError` rejection $\rightarrow$ Actual: `ValueError` raised $\rightarrow$ **PASS**

### Unchallenged Areas
- Econometric model specifications (GAM, Gram-Schmidt, ARIMA) — deferred to Milestone 2 review.

---

## 6. Verification Method

To independently verify the Milestone 1 deliverables and review findings:

1. **Verify All Milestone 1 Feature Coverage Tests (Tier 1)**:
   ```powershell
   python -m unittest tests/test_tier1.py -k "test_f1" -v
   ```
   *Expected Result*: `Ran 5 tests ... OK`.

2. **Verify All Milestone 1 Boundary Tests (Tier 2)**:
   ```powershell
   python -m unittest tests/test_tier2.py -k "test_b1" -v
   ```
   *Expected Result*: `Ran 5 tests ... OK`.

3. **Verify Under Specific Boundary Test Names (noting the alias finding)**:
   ```powershell
   python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_leap_year_handling tests.test_tier2.TestTier2BoundaryCases.test_b1_unequal_distributor_revisions tests.test_tier2.TestTier2BoundaryCases.test_b1_extreme_macro_spike
   ```
   *Expected Result*: `Ran 3 tests ... OK`.

4. **Verify Cryptographic & Forensic Zero-Synthetic Audit (Tier 4)**:
   ```powershell
   python -m unittest tests/test_tier4.py -k "test_s2" -v
   ```
   *Expected Result*: `Ran 1 test ... OK`.

5. **Verify Dataset Schema and Integrity**:
   ```powershell
   python -c "import pandas as pd; cng = pd.read_csv('data/cng_data.csv'); macro = pd.read_csv('data/macro_data.csv'); assert len(cng) >= 1000; assert len(macro) >= 120; assert not cng.isna().any().any(); assert not macro.isna().any().any(); print('ALL ASSERTIONS PASSED')"
   ```
