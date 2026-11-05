# Project: Modeling and Forecasting Natural Gas Prices in India

## Architecture
The system consists of an end-to-end econometric modeling, forecasting, and academic publishing pipeline implemented in pure Python with standard scientific libraries (`numpy`, `pandas`, `scipy`, `statsmodels`, `scikit-learn`, `matplotlib`).

Data flows sequentially:
1. **Raw Scrapers & Extractors** (`scripts/scrape_cng.py`, `scripts/extract_macro.py`):
   - Scrapes real historical price points from verified distributor endpoints (`mypetrolprice.com`) for 6 major Indian cities (Delhi, Mumbai, Noida, Ghaziabad, Ahmedabad, Pune).
   - Extracts real quarterly GDP, PFCE (income proxy), and monthly CPI from the official MoSPI REST API (`api.mospi.gov.in`) using SSL legacy transport.
2. **Data Processors & Splicing Engine**:
   - Converts discrete CNG revision points into continuous monthly panel data via Step-Function Zero-Order Hold and Time-Weighted Average Price (TWAP).
   - Slices and splices GDP/CPI base years (2004-05, 2011-12) via SNA/IMF Ratio Linking Factors.
   - Disaggregates quarterly GDP to monthly frequency using Denton-Cholette Proportional Benchmarking and Rescaled Monotone Cubic Spline.
   - Outputs: `data/cng_data.csv` and `data/macro_data.csv`.
3. **Econometric & Machine Learning Engine** (`src/`):
   - `src/gram_schmidt.py`: Diagnostic check for multicollinearity (VIF > 5.0, |r| > 0.80). If and only if detected, performs Modified Gram-Schmidt orthogonalization projecting collinear regressors (CPI/Income) onto the orthogonal complement of GDP.
   - `src/gam_pipeline.py`: Fits Generalized Additive Model (`statsmodels.gam.api.GLMGam`) incorporating:
     - Standardized polynomial trend ($d \in \{1, 2, 3\}$)
     - Truncated Fourier harmonic basis for seasonality ($K=2$, exact orthogonal basis)
     - Penalized cubic B-splines (`BSplines(df=5, degree=3)`) for macro regressors.
     - Generates 300-DPI Partial Dependence Plots (PDPs) with Bayesian credible intervals.
   - `src/arima_baseline.py`: Automated grid-search ARIMA $(p, d, q)$ baseline.
   - `src/evaluate.py`: Expanding-window time-series cross-validation computing quantitative RMSE, MAE, and percentage improvement. Outputs `output/model_results.json` and figures.
4. **Academic Manuscript Engine** (`paper/`):
   - `paper/manuscript.tex`: 7-section academic manuscript in standard LaTeX `article` class with `amsmath`, `booktabs`, `graphicx`, and `natbib`. Embeds actual empirical metrics, tables, and high-resolution figures.
   - `scripts/validate_manuscript.py`: Pure-Python AST/regex parser verifying syntax, citation resolution, and table/figure links.
5. **Independent E2E Testing Track** (`tests/`):
   - 60-test, 4-tier requirement-driven test suite built on Python standard library `unittest`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | CNG Real Data Scraper | Scrape authentic historical CNG price revisions for major distributors (IGL, MGL, etc.) | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Step-Function TWAP Panel Engine | Construct continuous monthly panel dataset via zero-order hold & TWAP | M1 | ORIGINAL_REQUEST §R1 |
| 3 | MoSPI Macro API Extractor | Extract authentic quarterly GDP, PFCE, and monthly CPI via MoSPI REST API | M1 | ORIGINAL_REQUEST §R1 |
| 4 | Base-Year Splicing Engine | Splice legacy base-years into a continuous 10-year monthly timeline | M1 | ORIGINAL_REQUEST §R1 |
| 5 | Temporal Disaggregation Engine | Disaggregate quarterly GDP to monthly via Denton-Cholette & Monotone Spline | M1 | ORIGINAL_REQUEST §R1 |
| 6 | Multicollinearity Diagnostic | Calculate VIF and pairwise correlations to detect regressor collinearity | M2 | ORIGINAL_REQUEST §R2 |
| 7 | Modified Gram-Schmidt Engine | If and only if collinearity detected, orthogonalize regressors before GAM | M2 | ORIGINAL_REQUEST §R2 |
| 8 | GAM Polynomial Trend Basis | Model secular price changes via standardized polynomial trend terms | M2 | ORIGINAL_REQUEST §R2 |
| 9 | GAM Harmonic Seasonality Basis | Truncated Fourier series $\sin(2\pi kt/12), \cos(2\pi kt/12)$ for monthly seasonality | M2 | ORIGINAL_REQUEST §R2 |
| 10 | GAM Penalized B-Splines | Penalized smooth B-splines for macroeconomic demand drivers | M2 | ORIGINAL_REQUEST §R2 |
| 11 | Baseline ARIMA Grid Search | Auto-ARIMA baseline with AIC/BIC optimization | M2 | ORIGINAL_REQUEST §R3 |
| 12 | Time-Series Cross-Validation | Expanding-window walk-forward cross-validation preventing lookahead | M2 | ORIGINAL_REQUEST §R3 |
| 13 | Quantitative RMSE Benchmark | Calculate and compare out-of-sample RMSE between GAM and ARIMA | M2 | ORIGINAL_REQUEST §R3 |
| 14 | Partial Dependence Plotter | Generate publication-grade PDPs for GAM non-linear spline effects | M2 | ORIGINAL_REQUEST §R2 |
| 15 | Academic Manuscript Structure | Complete 7-section LaTeX manuscript (`paper/manuscript.tex`) | M3 | ORIGINAL_REQUEST §R3 |
| 16 | Empirical Table Generation | Export regression tables, diagnostics, and metrics in LaTeX `booktabs` format | M3 | ORIGINAL_REQUEST §R3 |
| 17 | Figure Generation & Embedding | High-resolution PDF/PNG figure export and embedding in `.tex` | M3 | ORIGINAL_REQUEST §R3 |
| 18 | Model Superiority Finding | Formulate conclusive empirical findings on GAM vs ARIMA performance | M3 | ORIGINAL_REQUEST §R3 |
| 19 | E2E Testing Framework | 60-test 4-tier test suite verifying all acceptance criteria and edge cases | E2E-Track | ORIGINAL_REQUEST §Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| E2E | E2E Testing Track | Requirement-driven test harness (Tiers 1-4, 60 tests), publishes TEST_READY.md | none | DONE |
| M1 | Data Collection & Macro Splicing | Scrape CNG panel, extract GDP/CPI, splice base years, disaggregate GDP | none | DONE |
| M2 | Econometric & GAM Modeling | VIF diagnostic, Gram-Schmidt, GAM with trend/harmonics/splines, ARIMA, CV, PDPs | M1 | PLANNED |
| M3 | Academic Manuscript & Reporting | Compile complete LaTeX manuscript with embedded empirical results and figures | M2 | PLANNED |
| M4 | Final Acceptance & Adversarial Hardening | Pass 100% E2E tests (Tiers 1-4) + Tier 5 Adversarial Coverage Hardening | E2E, M3 | PLANNED |

## Interface Contracts
### Data Engineering (M1) ↔ Modeling Engine (M2)
- Input: `data/cng_data.csv`
  - Columns: `Date` (YYYY-MM-01), `City` (str), `Distributor` (str), `Price_INR` (float), `Revision_Count` (int)
  - Constraint: >= 36 monthly rows per city; 0 synthetic points.
- Input: `data/macro_data.csv`
  - Columns: `Date` (YYYY-MM-01), `GDP_Monthly_Cr` (float), `CPI_Index` (float), `Income_PFCE_Cr` (float)
  - Constraint: >= 120 continuous monthly rows (10 years); 0 synthetic points.

### Modeling Engine (M2) ↔ Academic Manuscript (M3)
- Output: `output/model_results.json`
  - Keys: `rmse_gam` (float), `rmse_arima` (float), `mae_gam` (float), `mae_arima` (float), `pct_improvement` (float), `vif_before` (dict), `vif_after` (dict), `orthogonalization_applied` (bool), `superior_model` (str).
- Output: `output/figures/`
  - `fig_cng_historical.png`, `fig_macro_spliced.png`, `fig_gam_pdp.png`, `fig_forecast_comparison.png`, `fig_residual_diagnostics.png` (300 DPI PNG and vector PDF).
- Output: `output/tables/`
  - `table_descriptives.tex`, `table_model_comparison.tex`, `table_gam_components.tex` (`booktabs` format).

## Code Layout
```
BTP/
├── .agents/                      # Multi-agent coordination metadata
├── data/                         # Real scraped and spliced data (strictly 0 synthetic data)
│   ├── cng_data.csv              # Multi-city monthly CNG panel
│   └── macro_data.csv            # 10-year monthly spliced macroeconomic series
├── scripts/                      # Data extraction and standalone utility scripts
│   ├── scrape_cng.py             # Historical CNG scraper
│   ├── extract_macro.py          # MoSPI API extractor and splicing engine
│   └── validate_manuscript.py    # AST/regex LaTeX validator
├── src/                          # Econometric and machine learning pipeline
│   ├── __init__.py
│   ├── gram_schmidt.py           # VIF check & Modified Gram-Schmidt orthogonalizer
│   ├── gam_pipeline.py           # GLMGam with polynomial trend, Fourier seasonality, B-splines
│   ├── arima_baseline.py         # Automated ARIMA grid search
│   └── evaluate.py               # Time-series CV, RMSE benchmark, PDP generator
├── paper/                        # Academic research manuscript
│   ├── manuscript.tex            # Full academic paper
│   ├── references.bib            # BibTeX literature references
│   ├── figures/                  # Embedded high-res empirical figures
│   └── tables/                   # Embedded LaTeX regression tables
├── output/                       # Generated empirical outputs
│   ├── model_results.json        # Quantitative benchmark metrics
│   ├── figures/
│   └── tables/
└── tests/                        # 4-Tier E2E test suite
    ├── test_tier1.py             # Feature coverage tests (25 tests)
    ├── test_tier2.py             # Boundary and corner case tests (25 tests)
    ├── test_tier3.py             # Cross-feature interaction tests (5 tests)
    └── test_tier4.py             # Real-world workload scenarios (5 tests)
```
