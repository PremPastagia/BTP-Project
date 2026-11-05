## 2026-09-17T22:28:43Z
You are worker_m1 (teamwork_preview_worker).
Your working directory is: C:\Users\Prem Pastagia\Desktop\BTP\.agents\worker_m1
You MUST read C:\Users\Prem Pastagia\Desktop\BTP\.agents\ORIGINAL_REQUEST.md before beginning.
You must also read:
- C:\Users\Prem Pastagia\Desktop\BTP\PROJECT.md
- C:\Users\Prem Pastagia\Desktop\BTP\.agents\survey_explorer_1\report.md
- C:\Users\Prem Pastagia\Desktop\BTP\.agents\survey_explorer_1\handoff.md

Your exclusive write ownership:
- scripts/scrape_cng.py
- scripts/extract_macro.py
- data/cng_data.csv
- data/macro_data.csv

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

CRITICAL DATA INTEGRITY CONSTRAINT:
Do NOT synthesize or fake data under any circumstances. Use only real scraped/extracted data. If only 9 points can be found, the team must figure out how to model it or fail.

Your mission:
Implement Milestone 1 (Data Collection & Macroeconomic Engineering):
1. Create `scripts/scrape_cng.py`:
   - Scrape historical CNG price changes for major distributors from the verified endpoint: `https://www.mypetrolprice.com/FuelHistoryDataServing.aspx?LocationId={id}&Span=365&selectedFuels=3H&HikeChartId=FuelHikeChartDetails` for Delhi (2, IGL), Mumbai (3, MGL), Noida (37, IGL), Ghaziabad (39, IGL), Ahmedabad (10, ATGL/GGL), Pune (7, MNGL).
   - Apply step forward-fill (zero-order hold) across calendar dates and compute monthly Time-Weighted Average Price (TWAP).
   - Generate `data/cng_data.csv` containing at least 3 years (up to 15 years available) of monthly CNG panel data with columns: `Date`, `City`, `Distributor`, `Price_INR`, `Revision_Count`.
2. Create `scripts/extract_macro.py`:
   - Extract real quarterly GDP and PFCE (income proxy) from MoSPI API (`https://api.mospi.gov.in/api/nas/getNasData`) using the `LegacySSLAdapter` documented in survey_explorer_1's report.
   - Extract real monthly CPI from MoSPI API (`https://api.mospi.gov.in/api/cpi/getCpiData`).
   - Implement base-year splicing (Ratio Linking Factor) and temporal disaggregation of quarterly GDP to monthly frequency using Denton-Cholette benchmarking and monotone cubic spline, strictly preserving quarterly totals.
   - Generate `data/macro_data.csv` containing at least 10 years (120+ months) of continuous monthly macroeconomic data with columns: `Date`, `GDP_Monthly_Cr`, `CPI_Index`, `Income_PFCE_Cr`.
3. Run the scripts, verify that `data/cng_data.csv` and `data/macro_data.csv` exist and contain genuine non-synthetic data, and document exact row counts, date ranges, and verification outputs.
4. Write your handoff to C:\Users\Prem Pastagia\Desktop\BTP\.agents\worker_m1\handoff.md and send a message to orchestrator upon completion.
