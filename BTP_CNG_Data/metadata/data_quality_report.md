# BTP Stage 3: Data Quality, Integrity & Provenance Audit Report

**Audit Execution Timestamp:** `2026-11-05T10:37:20.454374+00:00`  
**Working Directory:** `BTP_CNG_Data/`  
**Validation Status:** `ALL 9 INTEGRITY GATES PASSED`

## 1. Executive Summary & Verification Gates

| Integrity Gate | Status | Findings & Audit Evidence |
| :--- | :---: | :--- |
| **file_existence_and_non_emptiness** | `PASSED` | All 12 core datasets present and non-empty. |
| **zero_unlabelled_synthetic_data** | `PASSED` | Synthetic VAHAN proxy successfully quarantined; active monthly series is strictly unobserved/NaN. |
| **current_month_boundary** | `PASSED` | November 2026 isolated in provisional table; finalized panel strictly terminates at complete month 2026-10. |
| **arithmetic_and_price_bounds** | `PASSED` | TWAP strictly bounded by min/max; 265 revision price deltas verified; 275 revisions extracted from 2293 observations. |
| **anti_lookahead_lag_alignment** | `PASSED` | All 1-month lags strictly match shift(1) with zero forward contamination. |
| **release_timing_provenance** | `PASSED` | Verified observation_date <= publication_release_date across 100% of panel records. |
| **corporate_and_news_integrity** | `PASSED` | Verified 799 BSE corporate disclosures, 10 hashed news records, and 8 regulatory timeline events. |
| **city_coverage_matrix_generation** | `PASSED` | Generated coverage matrix for 10 cities saved to C:\Users\Prem Pastagia\Desktop\BTP\BTP_CNG_Data\metadata\city_coverage_matrix.csv |

## 2. City Coverage and Target Continuity

| City | State | Operator | Start Month | End Month | Months | Discrete Revisions | Total Scraped Points | Min Price (₹) | Max Price (₹) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Ahmedabad | Gujarat | Adani Total Gas Limited (ATGL) | 2011-12 | 2026-10 | 179 | 37 | 239 | ₹45.25 | ₹94.02 |
| Bengaluru | Karnataka | GAIL Gas Limited | 2025-03 | 2026-10 | 20 | 6 | 206 | ₹88.00 | ₹102.50 |
| Delhi | Delhi NCR | Indraprastha Gas Limited (IGL) | 2011-10 | 2026-10 | 181 | 46 | 249 | ₹32.00 | ₹101.90 |
| Gurgaon | Haryana | Haryana City Gas / IGL | 2012-02 | 2026-10 | 177 | 28 | 230 | ₹33.75 | ₹92.01 |
| Hyderabad | Telangana | Bhagyanagar Gas Limited (BGL) | 2012-08 | 2026-10 | 171 | 16 | 220 | ₹43.50 | ₹112.00 |
| Kanpur | Uttar Pradesh | Central U.P. Gas Limited (CUGL) | 2021-11 | 2026-10 | 60 | 16 | 216 | ₹67.82 | ₹102.00 |
| Lucknow | Uttar Pradesh | Green Gas Limited (GGL) | 2012-08 | 2026-10 | 171 | 21 | 222 | ₹42.14 | ₹107.00 |
| Mumbai | Maharashtra | Mahanagar Gas Limited (MGL) | 2011-01 | 2026-10 | 190 | 35 | 236 | ₹32.00 | ₹89.50 |
| Noida | Uttar Pradesh | Indraprastha Gas Limited (IGL) | 2012-01 | 2026-10 | 178 | 37 | 239 | ₹37.90 | ₹95.59 |
| Pune | Maharashtra | Maharashtra Natural Gas Limited (MNGL) | 2012-03 | 2026-10 | 176 | 33 | 236 | ₹39.50 | ₹98.50 |

## 3. Discrepancies Repaired & Quarantined Data

1. **Separation of Discrete Revisions vs Static Observations:**
   - Originally, scraped MyPetrolPrice data contained 2,293 rows where unchanged prices were recorded repeatedly.
   - Rebuilt parser to isolate true discrete price changes (ΔP ≠ 0). Exactly 275 revision events (including initial baselines) identified.
   - Raw observation points preserved in `structured/price_revisions/discrete_observations.parquet`.

2. **Quarantine of Synthetic VAHAN Registrations:**
   - Identified synthetic formula `15000 * np.exp(0.0078 * i)` previously generating monthly vehicle registrations.
   - Quarantined formula series to `quarantine/quarantined_vahan_synthetic_proxy.csv`.
   - Replaced monthly registrations in `demand_factors_monthly` with `NaN` and flagged as `unobserved_monthly_pending_manual_rto_export`.
   - Preserved authentic annual MoRTH/PPAC vehicle stock statistics.

3. **Current Incomplete Month Truncation (November 2026):**
   - November 2026 is an in-progress month (Day 5); month-end price and complete-month TWAP do not exist.
   - Finalized panel truncated strictly at `2026-10-31` (1,503 complete monthly observations across 10 cities).
   - Partial November 2026 observations isolated in `structured/price_revisions/cng_monthly_provisional.parquet` with `is_complete_month = False`.

4. **Authentic APM Gas Pricing vs Fixed Ceiling:**
   - Replaced static assumed APM ceiling ($6.50/MMBTU) with historical official series:
     - Pre-2023 Rangarajan semi-annual formula prices (PPAC official notifications).
     - April 2023 - March 2025: Kirit Parikh formula with $4.00 floor and $6.50 cap.
     - FY2025-26: Escalated ceiling of $6.75/MMBTU.
     - FY2026-27: Escalated ceiling of $7.00/MMBTU.
     - HPHT deepwater ceiling series tracked separately.

5. **Elimination of Lookahead Leakage & Backward-Fills:**
   - Removed all undocumented `.bfill()` operations.
   - Annual GDP preserved as annual series; monthly mapping enforces documented release vintage lag (~151 days) without linear interpolation.
   - Verified that all lagged features ($x_{t-1}$) perfectly equal `shift(1)` of original series.

6. **Reconstruction of Corporate Disclosures & News Archives:**
   - Ingested 799 genuine BSE corporate announcements across IGL, MGL, GGL, and ATGL.
   - Replaced bare Wayback homepage URLs with 10 authentic, dated policy decisions, PIB press releases, and statutory circulars with verified SHA-256 content hashes.
   - Indexed local statutory PDF filings (`IGL_Reduction_Domestic_Gas_Allocation_Nov2024.pdf`, `PPAC_Domestic_Gas_Price_Oct_2026.pdf`) with verified SHA-256 hashes.

## 4. Open Gaps Routed to Manual Collection Queue

The following variables require proprietary, paid, or manual portal extraction and have been logged in `metadata/manual_collection_queue.csv`:
- **PPAC Ready Reckoner Monthly Archives (Pre-2023):** NIC internal portal routing (`10.246.166.57`) blocks automated scraping.
- **VAHAN RTO-Level Monthly CNG Registrations:** Requires VAHAN 4 dashboard manual OTP/CAPTCHA export.
- **Historical City-Level VAT Gazette Circulars (Pre-2017):** State commercial tax department gazette archives.
- **Detailed Quarterly CGD Sourcing Breakdown:** Domestic APM vs RLNG percentages from quarterly investor transcripts.
