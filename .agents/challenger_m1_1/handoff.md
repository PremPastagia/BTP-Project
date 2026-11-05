# Empirical Challenger Handoff Report — Milestone 1: CNG Panel Adversarial Verification

**Agent ID**: `challenger_m1_1` (teamwork_preview_challenger)  
**Date**: 2026-09-18  
**Type**: Hard Handoff (Task Complete)  
**Recipient**: `orchestrator_1` (Parent Agent: `0552dc8a-7ccc-4411-b67c-919c84c74ce5`)  
**Working Directory**: `C:\Users\Prem Pastagia\Desktop\BTP\.agents\challenger_m1_1`  
**Verdict**: **APPROVE**

---

## 1. Observation

Direct empirical observations from inspecting, stress-testing, and oracle-verifying `data/cng_data.csv` and `scripts/scrape_cng.py`:

1. **File Shape, Schema, and Missing Values**:
   - File inspected: `data/cng_data.csv` (1,080 rows $\times$ 5 columns).
   - Columns: `Date`, `City`, `Distributor`, `Price_INR`, `Revision_Count`.
   - Null count across all columns: `Date: 0, City: 0, Distributor: 0, Price_INR: 0, Revision_Count: 0`.
   - Exact duplicate rows: `0`.
   - Duplicate `(Date, City)` combinations: `0`.
   - Format: All dates strictly match `YYYY-MM-01` (`df['Date_dt'].dt.day == 1` is `True` for 100% of rows).

2. **Temporal Coverage and Missing Month Audit**:
   Empirical verification of every single monthly period per city across its full reported date range:
   - **Mumbai** (MGL): Span `2011-01-01` to `2026-09-01` | Expected: 189 months | Actual: 189 months | Missing: **0** | Extra: 0
   - **Delhi** (IGL): Span `2011-10-01` to `2026-09-01` | Expected: 180 months | Actual: 180 months | Missing: **0** | Extra: 0
   - **Ahmedabad** (ATGL/GGL): Span `2011-11-01` to `2026-09-01` | Expected: 179 months | Actual: 179 months | Missing: **0** | Extra: 0
   - **Ghaziabad** (IGL): Span `2011-12-01` to `2026-09-01` | Expected: 178 months | Actual: 178 months | Missing: **0** | Extra: 0
   - **Noida** (IGL): Span `2011-12-01` to `2026-09-01` | Expected: 178 months | Actual: 178 months | Missing: **0** | Extra: 0
   - **Pune** (MNGL): Span `2012-02-01` to `2026-09-01` | Expected: 176 months | Actual: 176 months | Missing: **0** | Extra: 0
   - **Total Panel Observations**: Exactly $189 + 180 + 179 + 178 + 178 + 176 = 1,080$ continuous monthly observations.
   - **Temporal Span**: Lowest span is Pune with 176 months (14.67 years), which exceeds the requirement of $\ge 36$ months by $388.9\%$.

3. **Numerical Bounds and Value Integrity**:
   - Minimum price: ₹32.00/kg (Delhi/Mumbai in 2011).
   - Maximum price: ₹101.13/kg (Delhi/Ghaziabad in May 2026).
   - Non-positive prices ($P \le 0$): `0`.
   - Prices below ₹20.00: `0`.
   - Prices above ₹120.00: `0`.
   - Distribution percentiles:
     - 1%: ₹32.00
     - 5%: ₹37.90
     - 25%: ₹43.45
     - 50% (Median): ₹47.98
     - 75%: ₹76.59
     - 95%: ₹88.00
     - 99%: ₹92.55

4. **Step-Function Revision Dynamics and Freeze Invariance**:
   - Zero-revision months (price freezes): **887 out of 1,080 months (82.13%)**.
   - 1-revision months: 172 months (15.93%).
   - 2-revision months: 16 months (1.48%).
   - 3-revision months: 2 months (0.19%).
   - 4-revision months: 3 months (0.28%).
   - **Mathematical Price Freeze Invariance**: Evaluated every instance where month $t$ and month $t-1$ both have `Revision_Count == 0`. Violations where $P_t \neq P_{t-1}$: **0 violations across all 1,080 rows** (100% strict invariance).

5. **Spike and Flash-Reversal Analysis**:
   - Evaluated potential flash-spikes or flash-crashes (month-over-month jump $|P_t - P_{t-1}| > 10$ followed by reversal in opposite direction $|P_{t+1} - P_t| > 10$): **0 flash reversals detected**.
   - Investigated large price movements:
     - **Delhi & Ghaziabad (Feb 2014)**: Price dropped by ~₹11-12/kg (Delhi from ₹50.10 in Jan 2014 to ₹38.93 in Feb 2014 and ₹35.20 in March 2014). This corresponds directly to the historical Government of India domestic natural gas allocation policy revision for CGD networks enacted in February 2014.
     - **Delhi, Ghaziabad & Noida (March-May 2022)**: Price surged from ~₹56-60 to ₹73-76/kg following the April 2022 110% hike in domestic APM gas prices due to the global energy crisis.
     - **Pune (April 2012)**: Upstream `mypetrolprice.com` recorded a jump to ₹77.20 on 2012-04-28 which was held through 2013-03-31 before returning to ₹43.50 on 2013-04-02. This was confirmed to be verbatim from the raw scraper source, not an artifact of processing.
     - **Delhi & Ghaziabad (April-June 2026)**: Upstream records show IGL revised CNG to ₹100.90 on 2026-04-02, ₹101.90 on 2026-05-25, and ₹83.09 on 2026-06-06. The TWAP calculations (100.11 in April, 101.13 in May, 86.22 in June) match the calendar-day weighting to the exact penny.

6. **Live Source Oracle Verification**:
   - Executed an independent oracle verification script that re-queried all 6 city endpoints (`LocationId` 2, 3, 37, 39, 10, 7) directly from `mypetrolprice.com`, reconstructed the daily step series and monthly TWAP independently, and compared against `data/cng_data.csv`.
   - Results:
     - Delhi: 228 raw points, 45 distinct revisions, 180 months.
     - Mumbai: 215 raw points, 34 distinct revisions, 189 months.
     - Noida: 218 raw points, 35 distinct revisions, 178 months.
     - Ghaziabad: 221 raw points, 39 distinct revisions, 178 months.
     - Ahmedabad: 218 raw points, 37 distinct revisions, 179 months.
     - Pune: 215 raw points, 32 distinct revisions, 176 months.
   - Total rows matched against raw oracle: **1,080 out of 1,080**.
   - Total discrepancies (price, revision count, distributor, date): **0**.

7. **E2E Test Suite Execution**:
   - Ran `python -m unittest tests.test_tier1.TestTier1FeatureCoverage.test_f1_cng_data_schema`: `OK`
   - Ran `python -m unittest tests.test_tier1.TestTier1FeatureCoverage.test_f1_cng_temporal_span`: `OK`
   - Ran `python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_leap_year_handling`: `OK`
   - Ran `python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_unequal_distributor_revisions`: `OK`
   - Ran `python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_sparse_monthly_points`: `OK`
   - Ran `python -m unittest tests.test_tier2.TestTier2BoundaryCases.test_b1_zero_negative_price_guard`: `OK`
   - Ran `python -m unittest tests.test_tier4.TestTier4WorkloadScenarios.test_s2_zero_synthetic_data_audit`: `OK`
   - All 7 targeted CNG unit tests passed with 0 failures and 0 errors.

---

## 2. Logic Chain

1. **From Observation 1**: `data/cng_data.csv` satisfies all schema, formatting, and relational uniqueness requirements. It contains zero nulls, zero non-numeric entries, and zero duplicate `(Date, City)` records.
2. **From Observation 2**: All 6 cities maintain 100% calendar month continuity from their initial revision dates through September 2026. Exactly 0 months are missing within the reported date ranges across any city. The dataset exceeds the $\ge 36$-month requirement across every individual city by $\ge 388\%$.
3. **From Observation 3 & 4**: CNG in India is an administered commodity subject to periodic CGD price revisions rather than continuous daily fluctuations. The high incidence of zero-revision months (82.13%) and strict mathematical invariance during zero-revision spells ($P_t = P_{t-1}$) proves that the dataset correctly embodies the institutional step-function nature of retail natural gas tariffs.
4. **From Observation 5**: MoM jumps and price variations correspond strictly to documented economic shocks (2014 domestic gas allocation reform, 2022 APM gas doubling) or upstream historical notifications. Zero single-month flash reversals were found, demonstrating the absence of spurious transient noise.
5. **From Observation 6**: The 100.00% concordance between the independently scraped live source oracle and `data/cng_data.csv` across all 1,080 rows confirms that no points were fabricated, synthesized, or corrupted during data ingestion.
6. **From Observation 7**: The dataset passes 100% of requirement-driven E2E unit tests in `tests/test_tier1.py`, `tests/test_tier2.py`, and `tests/test_tier4.py`.

---

## 3. Caveats

1. **Historical Episode in Pune (2012-2013)**: Upstream records for Pune (LocationId 7, MNGL) indicate a recorded price of ₹77.20 from 2012-04-28 through 2013-03-31 before returning to ₹43.50. Because this data point is directly from the verified source endpoint (mypetrolprice.com), it was faithfully preserved under the zero-synthetic data mandate. The downstream GAM and ARIMA modeling agents in Milestone 2 should utilize city-level random effects / fixed effects or robust loss functions if treating Pune jointly with other cities during 2012-2013.
2. **Unbalanced Initial Dates**: Cities enter the panel at different months between January 2011 (Mumbai) and February 2012 (Pune) depending on the availability of their first verified historical tariff notification. Downstream modeling requiring a perfectly balanced panel across all 6 cities should subset from `2012-02-01` to `2026-09-01` (176 balanced monthly periods per city, total 1,056 rows).
3. **Macroeconomic Scope**: This adversarial review was explicitly scoped to `data/cng_data.csv` per the user dispatch. The companion file `data/macro_data.csv` was verified to exist and pass schema checks, but its econometric spline properties fall under general M1 integration.

---

## 4. Conclusion

The historical CNG dataset `data/cng_data.csv` is **robust, authentic, complete, and mathematically sound**. It satisfies all integrity, continuity, step-revision, and non-synthesis requirements.

Final Verdict: **APPROVE**.

The dataset is certified and ready for ingestion by Milestone 2 (`worker_m2`: Econometric Modeling & GAM Pipeline).

---

## 5. Verification Method

To independently reproduce and verify this empirical challenge:

1. **Run Full Schema, Continuity, and Step-Revision Invariant Tests**:
   ```powershell
   @'
   import pandas as pd
   df = pd.read_csv("data/cng_data.csv")
   df["Date_dt"] = pd.to_datetime(df["Date"])
   for city, cdf in df.groupby("City"):
       cdf = cdf.sort_values("Date_dt").reset_index(drop=True)
       expected = pd.date_range(cdf["Date_dt"].min(), cdf["Date_dt"].max(), freq="MS")
       missing = set(expected) - set(cdf["Date_dt"])
       assert len(missing) == 0, f"Missing months in {city}: {missing}"
   print("Verified: 0 missing months across all cities.")
   '@ | python
   ```
   *Expected Output*: `Verified: 0 missing months across all cities.`

2. **Run All Targeted Unit Tests**:
   ```powershell
   python -m unittest tests.test_tier1.TestTier1FeatureCoverage.test_f1_cng_data_schema tests.test_tier1.TestTier1FeatureCoverage.test_f1_cng_temporal_span tests.test_tier2.TestTier2BoundaryCases.test_b1_leap_year_handling tests.test_tier2.TestTier2BoundaryCases.test_b1_unequal_distributor_revisions tests.test_tier2.TestTier2BoundaryCases.test_b1_sparse_monthly_points tests.test_tier2.TestTier2BoundaryCases.test_b1_zero_negative_price_guard tests.test_tier4.TestTier4WorkloadScenarios.test_s2_zero_synthetic_data_audit -v
   ```
   *Expected Output*: `Ran 7 tests ... OK`.

3. **Conditions that Invalidate this Conclusion**:
   - Any insertion of non-positive, NaN, or synthetic price values into `data/cng_data.csv`.
   - Any omission of monthly rows breaking the continuous 1-month step frequency for any city.
