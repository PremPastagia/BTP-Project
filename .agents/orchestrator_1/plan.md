# Master Project Plan — Natural Gas Prices in India Research Paper

## Project Objective
Deliver an academic-grade, end-to-end research paper and codebase modeling and forecasting natural gas / CNG prices in India using Generalized Additive Models (GAM) compared against ARIMA baselines, built entirely on authentic scraped distributor price data and real macroeconomic series (data.gov.in / econpulse / official sources).

## Constraints & Requirements
1. **Zero Data Faking / Integrity Benchmark**: Only authentic scraped and spliced series. Strict forensic audit gate.
2. **Data Splicing**: Legacy base-years for GDP and CPI spliced into a continuous 10-year monthly timeline (with appropriate interpolation where needed for quarterly GDP). At least 3 years of monthly CNG panel data across major distributors (IGL, MGL, etc.).
3. **GAM Architecture**: Polynomial trend, harmonic basis for seasonality, smooth splines for macroeconomic drivers.
4. **Multicollinearity Protocol**: Statistical test (VIF / correlation / condition number). If and only if detected, automated Gram-Schmidt orthogonalization before GAM estimation.
5. **Empirical Evaluation**: Walk-forward or k-fold time-series cross-validation comparing GAM vs ARIMA with quantitative RMSE reporting and partial dependence plots.
6. **Academic Manuscript**: Publication-quality LaTeX paper (`.tex` + compiled PDF if environment allows), embedding empirical figures, tables, methodology, and empirical findings.

## Dual-Track Execution Architecture
- **Track 1: E2E Testing Track**:
  - Independent requirement-driven test suite (Tiers 1-4: feature coverage, boundary/corner cases, cross-feature combinations, real-world research workload scenarios).
  - Publishes `TEST_READY.md`.
- **Track 2: Implementation Track**:
  - Phase 0: Survey (3 Explorers / Spec Miners).
  - Milestone 1: Data Scraping & Macroeconomic Engineering (`cng_data.csv`, `macro_data.csv`).
  - Milestone 2: Econometric & Machine Learning Modeling (`model_pipeline.py` with GAM, ARIMA, Gram-Schmidt, PDP generator, RMSE comparison).
  - Milestone 3: Academic Manuscript & Empirical Reporting (`paper/manuscript.tex`, figures, tables).
  - Final Milestone: Pass 100% E2E tests (Phase 1: Tiers 1-4, Phase 2: Adversarial Coverage Hardening Tier 5).
