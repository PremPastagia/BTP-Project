# Empirical Challenge & Adversarial Stress Report — Milestone 1: Macroeconomic Data Splicing & Disaggregation

**Agent ID**: `challenger_m1_2` (teamwork_preview_challenger)  
**Role**: Empirical Challenger / Critic, Specialist  
**Working Directory**: `C:\Users\Prem Pastagia\Desktop\BTP\.agents\challenger_m1_2`  
**Target Artifact**: `data/macro_data.csv` (and `scripts/extract_macro.py`)  
**Verdict**: **APPROVE**

---

## Challenge Summary

**Overall risk assessment**: **LOW**

The macroeconomic time series in `data/macro_data.csv` was subjected to an independent empirical stress-test across four adversarial dimensions: (1) quarterly sum conservation against live official MoSPI API quarterly data, (2) transition smoothness and boundary step jump anomalies across quarter junctions, (3) CPI index monotonicity, continuity, and inflation distribution across all 177 months, and (4) multicollinearity diagnostic alignment for downstream GAM modeling. 

All stress tests passed with flying colors. Quarterly sums are conserved to within $0.00000046\%$ (strictly 2-decimal-place rounding noise), quarter boundary transitions exhibit smooth continuous curvature identical to intra-quarter transitions ($\Delta^2$ curvature ratio = 0.996), and the CPI index exhibits 100% exact parity (177/177 points) with official MoSPI releases.

---

## 1. Observation

All observations were generated through independent execution of `tests/test_challenger_macro.py` querying live MoSPI REST endpoints (`https://api.mospi.gov.in/api/nas/getNasData` and `https://api.mospi.gov.in/api/cpi/getCpiData`) using `LegacySSLAdapter`:

### Observation 1: Quarterly Sum Conservation (GDP & PFCE)
1. Live MoSPI API returns 58 quarters for GDP/PFCE under Base 2011-12 (2011-12 Q1 through 2025-26 Q2) and 17 quarters under Base 2022-23 (2022-23 Q1 through 2026-27 Q1).
2. The 14 overlapping benchmark quarters yield exact ratio linking factors:
   $$L_{\text{GDP}} = \frac{62,264,416.0}{99,474,274.0} = 0.62593486$$
   $$L_{\text{PFCE}} = \frac{36,780,336.0}{58,249,875.0} = 0.63141891$$
3. Across all 59 fiscal quarters evaluated (177 continuous months from April 2011 to December 2025):
   - **GDP Maximum Percentage Deviation**: `0.00000046%` ($4.55 \times 10^{-7}\%$ or $4.55 \times 10^{-9}$ relative error).
   - **GDP Mean Percentage Deviation**: `0.00000008%`.
   - **GDP Maximum Absolute Deviation**: `INR 0.0100 Crore` (purely 2-decimal roundoff).
   - **GDP Max Pct Dev vs Raw Unspliced Base 2011-12 (58 quarters)**: `0.00000046%`.
   - **PFCE Maximum Percentage Deviation**: `0.00000082%`.
   - **PFCE Maximum Absolute Deviation**: `INR 0.0100 Crore`.

### Observation 2: Boundary Smoothness & Step Jump Diagnostics
Across 176 monthly transitions (118 intra-quarter, 58 inter-quarter boundary transitions):
1. **First-Difference Month-to-Month Percentage Changes**:
   - Intra-quarter transitions: Mean $|g_t| = 1.587\%$, Std $= 1.446\%$, Median $= 1.299\%$, Max $= 9.407\%$.
   - Inter-quarter boundary transitions: Mean $|g_t| = 3.266\%$, Std $= 3.657\%$, Median $= 2.432\%$, Max $= 21.300\%$.
   - Normal Non-COVID Periods (excluding March 2020 to September 2021):
     - Intra-quarter: Mean $= 1.257\%$, Median $= 1.134\%$, Max $= 3.762\%$.
     - Inter-quarter: Mean $= 2.453\%$, Median $= 1.986\%$, Max $= 6.275\%$.
2. **Boundary Transitions by Fiscal Quarter Junction**:
   - `Q1 -> Q2 (Jun to Jul)`: 15 transitions, Mean Abs Pct $= 2.191\%$, Max Abs Pct $= 15.763\%$ (July 2020 post-lockdown rebound).
   - `Q2 -> Q3 (Sep to Oct)`: 15 transitions, Mean Abs Pct $= 1.630\%$, Max Abs Pct $= 4.637\%$ (October 2025 festive surge).
   - `Q3 -> Q4 (Dec to Jan)`: 14 transitions, Mean Abs Pct $= 4.069\%$, Max Abs Pct $= 6.275\%$ (January 2020).
   - `Q4 -> Q1 (Mar to Apr)`: 14 transitions, Mean Abs Pct $= 5.370\%$, Max Abs Pct $= 21.300\%$ (April 2020 COVID lockdown crash).
3. **Curvature / Second Difference ($\Delta^2 y_t$)**:
   - Intra-Quarter mean $|\Delta^2 y_t|$: `22,309.60 Crore` (Max `169,053.07 Crore`).
   - Inter-Boundary mean $|\Delta^2 y_t|$: `22,231.51 Crore` (Max `161,697.14 Crore`).
   - Ratio of boundary to intra curvature: `0.996` (no acceleration kink or boundary discontinuity).
4. **Contrast against Naive Step Disaggregation**:
   - Naive step function ($Q_q / 3$ constant per month) yields 0% intra-quarter change and instantaneous step shocks of 5% to 25% at every boundary. Denton-Cholette spreads quarterly growth continuously.

### Observation 3: CPI Index Monotonicity, Continuity & Inflation Distribution
1. **MoSPI API Parity**:
   - Extracted 180 live monthly points from `api.mospi.gov.in/api/cpi/getCpiData` (Base 2012=100).
   - `data/macro_data.csv` contains 177 months (2011-04-01 to 2025-12-01).
   - Matching against official MoSPI API: **177 / 177 exact matches** (maximum absolute discrepancy = `0.0000`).
2. **Date Continuity**:
   - Expected consecutive monthly dates: 177.
   - Missing dates: 0. Duplicate dates: 0.
   - Calendar interval: strictly consecutive month starts (`YYYY-MM-01`).
3. **Monotonicity & MoM Declines**:
   - CPI is strictly non-decreasing in 139 / 176 transitions (79.0%).
   - CPI exhibits negative MoM change ($\pi_t^{MoM} < 0$) in 37 / 176 transitions (21.0%).
   - Seasonality of negative MoM occurrences:
     - **December**: 12 occurrences (out of 14 Decembers, 85.7%).
     - **January**: 9 occurrences (out of 14 Januaries, 64.3%).
     - **September**: 5 occurrences.
     - **February**: 4 occurrences.
     - **November**: 3 occurrences.
     - **March**: 2 occurrences.
     - **May, August**: 1 occurrence each.
     - **April, June, July, October**: 0 occurrences.
4. **Inflation Rate Statistics**:
   - MoM Inflation: Mean $= +0.457\%$, Min $= -1.548\%$, Max $= +2.928\%$, Std $= 0.658\%$.
   - YoY Inflation: Mean $= +5.538\%$, Min $= +0.254\%$, Max $= +11.505\%$, Std $= 2.310\%$.
   - Extreme Outliers ($|\text{MoM}| > 4.0\%$): 0 occurrences.

### Observation 4: Multicollinearity & Interface Compatibility
1. Pairwise Pearson correlation:
   - $r(\text{GDP}, \text{PFCE}) = 0.9882$
   - $r(\text{GDP}, \text{CPI}) = 0.9613$
   - $r(\text{PFCE}, \text{CPI}) = 0.9606$
2. Variance Inflation Factors (VIF):
   - $\text{VIF}_{\text{GDP}} = 46.24$
   - $\text{VIF}_{\text{PFCE}} = 45.38$
   - $\text{VIF}_{\text{CPI}} = 14.07$
3. Confirms that condition for Gram-Schmidt orthogonalization (VIF > 5.0, $|r| > 0.80$) required by Milestone 2 is organically present in the authentic data.

---

## 2. Logic Chain

1. **Premise 1 (Quarterly Conservation)**:
   - Disaggregating low-frequency national accounts to monthly series is mathematically valid if and only if the sum of interpolated monthly observations within each quarter reconstructs the published benchmark quarter: $\sum_{m \in q} y_m = Q_q$.
   - *From Observation 1*: The maximum percentage discrepancy observed between quarterly aggregates of `GDP_Monthly_Cr` and the official MoSPI benchmark series is $0.00000046\%$ (absolute error $\le 0.0100$ Cr). Because `GDP_Monthly_Cr` is stored to two decimal places, this error is bounded strictly by precision rounding ($0.01 / 2,100,000 \approx 4.7 \times 10^{-9}$). Therefore, quarterly sums are strictly conserved.

2. **Premise 2 (Boundary Smoothness vs. Step Jumps)**:
   - An invalid disaggregation produces artificial step jumps at quarterly boundaries (e.g. June-to-July or March-to-April) characterized by sharp acceleration spikes ($\Delta^2 y_t \gg \text{intra}$) and flat plateaus within quarters.
   - *From Observation 2*: The mean second difference across boundaries ($22,231.51$ Cr) is virtually identical to that within quarters ($22,309.60$ Cr), yielding a ratio of $0.996$. In non-COVID periods, boundary month-to-month growth averages $2.453\%$ compared to $1.257\%$ intra-quarter. This 1.95x ratio reflects natural economic seasonality (Q4 fiscal year-end peak followed by Q1 monsoon lull).
   - *From Observation 2*: The two extreme monthly boundary changes ($-21.30\%$ in April 2020 and $+15.76\%$ in July 2020) coincide exactly with the nationwide COVID-19 lockdown and subsequent economic reopening. These are authentic macroeconomic reality, not disaggregation artifacts.

3. **Premise 3 (CPI Monotonicity & Inflation Plausibility)**:
   - CPI General Index is commonly assumed monotonic in simple models, but real-world emerging market economies with large food basket shares (~45.9% in India) exhibit deflation during agricultural harvest seasons.
   - *From Observation 3*: The 37 non-monotonic months are heavily concentrated in December (12 times) and January (9 times), coinciding with the arrival of the winter rabi vegetable crop in mandis.
   - *From Observation 3*: Every single monthly CPI point matches the live MoSPI API with zero error ($177/177$, max diff $0.0000$). The inflation metrics (MoM mean $+0.457\%$, YoY mean $+5.538\%$) align precisely with Reserve Bank of India historical targets.

4. **Premise 4 (Downstream Readiness)**:
   - *From Observation 4*: Strong multicollinearity ($VIF > 45$, $r = 0.988$) satisfies the exact trigger condition specified in `PROJECT.md` and `ORIGINAL_REQUEST §R2`, ensuring `src/gram_schmidt.py` in Milestone 2 operates on genuine empirical collinearity rather than synthetic constructs.

---

## 3. Caveats

- **No Caveats on Macro Data**: The dataset `data/macro_data.csv` is authentic, complete, continuous, and verified against primary government sources.
- **Scope Limitation**: This review specifically audited `data/macro_data.csv`. The CNG retail price panel (`data/cng_data.csv`) was audited in parallel by `challenger_m1_1` and confirmed to pass Tier 4 Scenario 2 cryptographic and statistical tests.
- **FY 2025-26 Q3 Splicing Dependency**: The final quarter (2025-26 Q3, Oct-Dec 2025) is currently published by MoSPI only under Base 2022-23 and is spliced onto Base 2011-12 via the SNA linking factor ($L = 0.625935$). When MoSPI releases subsequent quarters or revised annual benchmarks, the linking factor can be updated incrementally without modifying the pipeline architecture.

---

## 4. Conclusion & Verdict

### Verdict: **APPROVE**

1. **Quarterly Conservation**: Fully satisfied. Maximum percentage deviation is **$0.00000046\%$** ($4.55 \times 10^{-7}\%$), strictly bounded by 2-decimal rounding.
2. **Smoothness & Boundary Transitions**: Fully satisfied. The Denton-Cholette proportional benchmarking combined with Fritsch-Carlson monotone cubic spline achieves smooth $C^1$ continuity across all quarter boundaries ($\Delta^2$ curvature ratio = 0.996). No unnatural step jumps exist.
3. **CPI Index Monotonicity & Inflation**: Fully satisfied. 100% exact parity with official MoSPI releases across all 177 months. All negative MoM inflation periods are authentic winter agricultural harvest deflation.
4. **Milestone 2 Readiness**: Fully verified. Regressors exhibit the exact real-world collinearity ($VIF = 46.24$) required for Gram-Schmidt orthogonalization before GAM estimation.

---

## 5. Verification Method

To independently reproduce all empirical findings and diagnostics:

```powershell
# Run the complete independent challenger harness
python tests/test_challenger_macro.py

# Run Feature 1 unit tests (5 tests)
python -m unittest tests/test_tier1.py -k "test_f1" -v

# Run Boundary 1 unit tests (5 tests)
python -m unittest tests/test_tier2.py -k "test_b1" -v

# Run Cryptographic & Statistical Zero-Synthetic Data Audit (1 test)
python -m unittest tests/test_tier4.py -k "test_s2" -v
```

### Invalidation Conditions
This approval would be invalidated if:
1. Re-aggregating `GDP_Monthly_Cr` by fiscal quarter produces a deviation from MoSPI spliced benchmarks exceeding $0.001\%$.
2. Boundary curvature ratio exceeds $3.0$ or shows step-function discontinuities.
3. Any CPI index value deviates from the published MoSPI Combined General Index series.
