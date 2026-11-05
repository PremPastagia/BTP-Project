# Test Infrastructure Specification: 4-Tier E2E Testing Framework

**Project**: Modeling and Forecasting Natural Gas Prices in India using Generalized Additive Models  
**Framework**: Python Standard Library `unittest`  
**Total Tests**: 60 Tests (4 Tiers)  
**Execution Entrypoint**: `python run_tests.py` or `python -m unittest discover -s tests -p "test_*.py"`  

---

## 1. Architectural Overview & Design Philosophy

The testing framework serves as an independent, opaque-box, requirement-driven verification engine. It guarantees strict adherence to all scientific, statistical, and software engineering criteria specified in `ORIGINAL_REQUEST.md` and `PROJECT.md`.

### Core Engineering Principles
1. **Zero External Test Dependencies (Ponytail Principle)**: The harness is built exclusively on Python 3.12's standard library `unittest` module. No external test runners (`pytest`, `tox`, `nose`) are required, ensuring zero installation friction and 100% portability across environments.
2. **Progressive Testability & Graceful TDD Discovery**: Modules from `src/` (or `models/`) and data artifacts from `data/` are resolved dynamically. Tests discover and execute cleanly even before downstream workers (M1, M2, M3) complete implementation, reporting explicit contract requirement failures rather than crashing during test suite import.
3. **Strict Zero-Synthetic Integrity**: The framework enforces the core user directive: **under no circumstances may synthetic or fake data be utilized**. Cryptographic and step-function audits verify historical authenticity.
4. **Deterministic Exit Codes**: `run_tests.py` returns exit code `0` when all selected tests pass, and exit code `1` upon any test failure or error, enabling immediate integration with CI/CD and multi-agent orchestrators.

---

## 2. 4-Tier Testing Hierarchy Specification

```
┌────────────────────────────────────────────────────────────────────────┐
│               TIER 4: REAL-WORLD WORKLOAD SCENARIOS                    │
│   5 Tests — Cold-start execution, Zero-synthetic forensic audit,       │
│   Regime shift stress test, Incremental ingestion, Publication package │
├────────────────────────────────────────────────────────────────────────┤
│               TIER 3: CROSS-FEATURE INTERACTIONS                       │
│   5 Tests — Data ingestion -> Collinearity gate -> Gram-Schmidt        │
│   -> GAM Spline -> PDP Plotter -> LaTeX Table -> Manuscript Sync       │
├────────────────────────────────────────────────────────────────────────┤
│               TIER 2: BOUNDARY & CORNER CASES                          │
│   25 Tests (5 per feature) — Leap years, sparse revisions, shocks,     │
│   degree-0 trend, extreme lambda, perfect collinearity, near-singular  │
│   matrices, flat price regimes, LaTeX special characters & balance     │
├────────────────────────────────────────────────────────────────────────┤
│               TIER 1: FEATURE COVERAGE                                 │
│   25 Tests (5 per feature) — Core functionality across Data Ingestion, │
│   GAM Model, Gram-Schmidt, ARIMA Benchmarking, Academic Manuscript     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Test Inventory & Traceability Matrix

| Requirement | Test Tier | Test Method Name | Verification Logic | Target Component |
|---|---|---|---|---|
| **REQ-1 / REQ-2** | Tier 1 (F1) | `test_f1_cng_data_schema` | Schema, numeric types, distributor coverage | `data/cng_data.csv` |
| **REQ-3** | Tier 1 (F1) | `test_f1_cng_temporal_span` | Span $\ge 36$ calendar months | `data/cng_data.csv` |
| **REQ-4 / REQ-5** | Tier 1 (F1) | `test_f1_macro_temporal_span` | Span $\ge 120$ continuous months (10 yrs) | `data/macro_data.csv` |
| **REQ-5** | Tier 1 (F1) | `test_f1_macro_no_nans` | Zero NaN, null, or Inf values | `data/macro_data.csv` |
| **REQ-4** | Tier 1 (F1) | `test_f1_base_year_continuity` | Continuous splicing without base-shift jumps | `data/macro_data.csv` |
| **REQ-6** | Tier 1 (F2) | `test_f2_gam_polynomial_trend` | Polynomial trend $P_d(t)$ of order $d \ge 1$ | `src/gam_pipeline.py` |
| **REQ-6** | Tier 1 (F2) | `test_f2_gam_harmonic_seasonality` | Orthogonal Fourier basis $\sin/\cos$ ($K=1,2$) | `src/gam_pipeline.py` |
| **REQ-6** | Tier 1 (F2) | `test_f2_gam_smooth_splines` | Penalized B-splines for macro drivers | `src/gam_pipeline.py` |
| **REQ-6 / REQ-8** | Tier 1 (F2) | `test_f2_gam_fit_execution` | Convergence & finite log-likelihood | `src/gam_pipeline.py` |
| **REQ-6** | Tier 1 (F2) | `test_f2_gam_prediction_shape` | Positive forecast horizon array | `src/gam_pipeline.py` |
| **REQ-7** | Tier 1 (F3) | `test_f3_vif_calculation` | Exact VIF calculation on orthogonal & collinear matrices | `src/gram_schmidt.py` |
| **REQ-7** | Tier 1 (F3) | `test_f3_collinearity_detection_threshold` | Detection trigger if VIF > 5.0 or $|r| > 0.80$ | `src/gram_schmidt.py` |
| **REQ-7** | Tier 1 (F3) | `test_f3_conditional_execution_gate` | Gram-Schmidt runs IF AND ONLY IF collinear | `src/gram_schmidt.py` |
| **REQ-7** | Tier 1 (F3) | `test_f3_gram_schmidt_orthogonality` | Inner product $|\langle v_i, v_j \rangle| < 10^{-7}$ | `src/gram_schmidt.py` |
| **REQ-7** | Tier 1 (F3) | `test_f3_gram_schmidt_span_preservation` | Matrix rank & column space projection preserved | `src/gram_schmidt.py` |
| **REQ-9** | Tier 1 (F4) | `test_f4_arima_estimation` | ARIMA baseline estimation & forecasting | `src/arima_baseline.py` |
| **REQ-9** | Tier 1 (F4) | `test_f4_walk_forward_cv` | Strict temporal ordering (no lookahead) | `src/evaluate.py` |
| **REQ-9** | Tier 1 (F4) | `test_f4_rmse_calculation` | Mathematical RMSE formula verification | `src/evaluate.py` |
| **REQ-9** | Tier 1 (F4) | `test_f4_model_comparison_output` | Metric dictionary in `output/model_results.json` | `output/model_results.json` |
| **REQ-8** | Tier 1 (F4) | `test_f4_pdp_generation` | Partial Dependence Plot generation on disk | `output/figures/fig_gam_pdp.png` |
| **REQ-10** | Tier 1 (F5) | `test_f5_tex_file_generation` | Manuscript exists, non-empty (>5,000 bytes) | `paper/manuscript.tex` |
| **REQ-10** | Tier 1 (F5) | `test_f5_tex_section_headers` | 7 required academic sections present | `paper/manuscript.tex` |
| **REQ-10** | Tier 1 (F5) | `test_f5_tex_figure_inclusion` | Referenced figures exist on disk | `paper/figures/` |
| **REQ-10** | Tier 1 (F5) | `test_f5_tex_table_inclusion` | LaTeX `booktabs` format (no vertical rules) | `paper/manuscript.tex` |
| **REQ-10** | Tier 1 (F5) | `test_f5_tex_conclusive_finding` | Explicit statement on model superiority | `paper/manuscript.tex` |
| **Boundary** | Tier 2 (F1) | `test_b1_leap_year_handling` | Feb 29 leap years (2016, 2020, 2024) | `scripts/scrape_cng.py` |
| **Boundary** | Tier 2 (F1) | `test_b1_unequal_distributor_revisions` | Asynchronous price revisions TWAP | `scripts/scrape_cng.py` |
| **Boundary** | Tier 2 (F1) | `test_b1_sparse_monthly_points` | Extended price freezes zero-order hold | `data/cng_data.csv` |
| **Boundary** | Tier 2 (F1) | `test_b1_extreme_macro_spike` | Q1 2020 COVID dip (-24% GDP) stability | `scripts/extract_macro.py` |
| **Boundary** | Tier 2 (F1) | `test_b1_zero_negative_price_guard` | Rejection of non-positive prices ($P \le 0$) | `scripts/scrape_cng.py` |
| **Boundary** | Tier 2 (F2) | `test_b2_degree_zero_polynomial` | Degree-0 polynomial trend (constant intercept) | `src/gam_pipeline.py` |
| **Boundary** | Tier 2 (F2) | `test_b2_high_degree_polynomial_guard` | Standardization prevents Runge explosion ($d \ge 5$) | `src/gam_pipeline.py` |
| **Boundary** | Tier 2 (F2) | `test_b2_extreme_smoothing_penalty` | Spline collapses to linear as $\lambda \to \infty$ | `src/gam_pipeline.py` |
| **Boundary** | Tier 2 (F2) | `test_b2_zero_smoothing_penalty` | Stability against singularity as $\lambda \to 0$ | `src/gam_pipeline.py` |
| **Boundary** | Tier 2 (F2) | `test_b2_short_time_series` | Informative error for sample size $N < 20$ | `src/gam_pipeline.py` |
| **Boundary** | Tier 2 (F3) | `test_b3_perfectly_collinear_vectors` | Zero-norm guard for linearly dependent vectors | `src/gram_schmidt.py` |
| **Boundary** | Tier 2 (F3) | `test_b3_zero_collinearity_passthrough` | Invariant passthrough for orthogonal vectors | `src/gram_schmidt.py` |
| **Boundary** | Tier 2 (F3) | `test_b3_near_singular_matrix` | Stability under condition number $\kappa > 10^{12}$ | `src/gram_schmidt.py` |
| **Boundary** | Tier 2 (F3) | `test_b3_vector_order_invariance` | Subspace projection invariant to column order | `src/gram_schmidt.py` |
| **Boundary** | Tier 2 (F3) | `test_b3_zero_variance_constant_regressor`| Clean handling of constant regressors | `src/gram_schmidt.py` |
| **Boundary** | Tier 2 (F4) | `test_b4_single_step_vs_multi_step` | Separate tracking for 1-step vs multi-step | `src/evaluate.py` |
| **Boundary** | Tier 2 (F4) | `test_b4_flat_price_regime` | MAPE & RMSE calculation under price freeze | `src/evaluate.py` |
| **Boundary** | Tier 2 (F4) | `test_b4_identical_model_error` | Deterministic tie-breaking logic | `src/evaluate.py` |
| **Boundary** | Tier 2 (F4) | `test_b4_arima_unit_root_boundary` | Enforce differencing ($d \ge 1$) on unit roots | `src/arima_baseline.py` |
| **Boundary** | Tier 2 (F4) | `test_b4_minimal_train_split` | Degrees-of-freedom guard for $N_{\text{train}} < 24$ | `src/evaluate.py` |
| **Boundary** | Tier 2 (F5) | `test_b5_missing_figure_detection` | Detects missing image file before compilation | `scripts/validate_manuscript.py` |
| **Boundary** | Tier 2 (F5) | `test_b5_special_character_escaping` | Escapes LaTeX special characters (`_`, `%`, etc.) | `scripts/validate_manuscript.py` |
| **Boundary** | Tier 2 (F5) | `test_b5_extreme_coefficient_formatting` | Formats extreme values in scientific notation | `scripts/generate_paper.py` |
| **Boundary** | Tier 2 (F5) | `test_b5_empty_table_cell_guard` | Flags bare NaNs or empty cells in tables | `scripts/validate_manuscript.py` |
| **Boundary** | Tier 2 (F5) | `test_b5_nested_environment_balance` | Verifies LIFO closing of LaTeX environments | `scripts/validate_manuscript.py` |
| **Cross-Feature** | Tier 3 | `test_x1_data_to_collinearity_to_gram_schmidt` | Ingestion -> VIF -> Conditional Gram-Schmidt | `src/gram_schmidt.py` |
| **Cross-Feature** | Tier 3 | `test_x2_gram_schmidt_to_gam_spline` | Orthogonal Regressors -> GAM Spline fit & EDF | `src/gam_pipeline.py` |
| **Cross-Feature** | Tier 3 | `test_x3_gam_estimation_to_pdp_plot` | Fitted GAM -> PDP Plot file generation | `src/evaluate.py` |
| **Cross-Feature** | Tier 3 | `test_x4_walk_forward_to_latex_table` | CV metrics -> Dynamic booktabs table generation | `scripts/generate_paper.py` |
| **Cross-Feature** | Tier 3 | `test_x5_end_to_end_pipeline_consistency` | JSON results sync with manuscript.tex numbers | `paper/manuscript.tex` |
| **Workload** | Tier 4 | `test_s1_cold_start_full_execution` | Scratch execution generates all core outputs | `scripts/run_pipeline.py` |
| **Workload** | Tier 4 | `test_s2_zero_synthetic_data_audit` | Forensic audit for step-function fuel revisions | `data/cng_data.csv` |
| **Workload** | Tier 4 | `test_s3_regime_shift_stress_scenario` | 2022 Crisis Spike & April 2023 Parikh Cap | `src/gam_pipeline.py` |
| **Workload** | Tier 4 | `test_s4_incremental_monthly_ingestion` | 12-month panel ingestion & model re-estimation | `src/gam_pipeline.py` |
| **Workload** | Tier 4 | `test_s5_publication_package_verification` | Paper, figures, tables, bibtex bundle audit | `paper/` |

---

## 4. Execution & Usage Instructions

### Running the Full Test Suite
```powershell
python run_tests.py
```
Or via standard unittest discovery:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

### Running Individual Tiers
```powershell
# Tier 1: Feature Coverage (25 tests)
python run_tests.py --tier 1

# Tier 2: Boundary & Corner Cases (25 tests)
python run_tests.py --tier 2

# Tier 3: Cross-Feature Interactions (5 tests)
python run_tests.py --tier 3

# Tier 4: Real-World Workload Scenarios (5 tests)
python run_tests.py --tier 4
```

### Verbose Mode
```powershell
python run_tests.py -v
```

---

## 5. Interface Contracts for Downstream Developers

Downstream worker agents (M1, M2, M3) can consult these interface definitions to implement compliant modules that will turn the test suite 100% green:

### 1. Data Engineering (`M1`)
- **`data/cng_data.csv`**:
  - Columns: `Date` (YYYY-MM-01), `City` (str), `Distributor` (str), `Price_INR` (float > 0), `Revision_Count` (int >= 0).
  - Requirements: $\ge 36$ distinct monthly periods, step-function price hold.
- **`data/macro_data.csv`**:
  - Columns: `Date` (YYYY-MM-01), `GDP_Monthly_Cr` (float > 0), `CPI_Index` (float > 0), `Income_PFCE_Cr` (float > 0).
  - Requirements: $\ge 120$ continuous monthly periods (10 years), 0 NaNs, continuous base-year splicing factor.

### 2. Econometric & Multicollinearity Engine (`M2`)
- **`src/gram_schmidt.py`**:
  - `compute_vif(df: pd.DataFrame) -> dict[str, float]`
  - `detect_multicollinearity(df: pd.DataFrame, vif_threshold=5.0, corr_threshold=0.80) -> tuple[bool, str]`
  - `process_regressors_conditionally(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]`
  - `gram_schmidt_orthogonalize(X: np.ndarray) -> np.ndarray`
- **`src/gam_pipeline.py`**:
  - `build_polynomial_trend(t: np.ndarray, degree: int = 1) -> np.ndarray`
  - `build_harmonic_basis(t: np.ndarray, period: int = 12, K: int = 2) -> np.ndarray`
  - `fit_gam_model(df: pd.DataFrame, target_col: str, trend_col: str, macro_cols: list[str]) -> object`
  - `predict_gam(model: object, df_future: pd.DataFrame) -> np.ndarray`
- **`src/arima_baseline.py`**:
  - `select_arima_order(series: np.ndarray) -> tuple[int, int, int]`
  - `fit_arima(series: np.ndarray, order: tuple[int, int, int]) -> object`
  - `forecast_arima(model: object, steps: int) -> np.ndarray`
- **`src/evaluate.py`**:
  - `calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float`
  - `walk_forward_cv_splits(total_samples: int, min_train: int, horizon: int) -> generator`
  - `generate_pdp_plot(model: object, data: pd.DataFrame, feature: str, output_path: Path) -> object`

### 3. Academic Reporting & Manuscript (`M3`)
- **`output/model_results.json`**:
  - Keys: `rmse_gam`, `rmse_arima`, `mae_gam`, `mae_arima`, `pct_improvement`, `superior_model`.
- **`paper/manuscript.tex`**:
  - 7 academic sections, booktabs tables, embedded figures, empirical superiority finding.
- **`paper/figures/`**:
  - `fig_cng_historical.png`, `fig_macro_spliced.png`, `fig_gam_pdp.png`, `fig_forecast_comparison.png`, `fig_residual_diagnostics.png`.
