## 2026-09-18T04:11:25+05:30
You are worker_m2 (teamwork_preview_worker).
Your working directory is: C:\Users\Prem Pastagia\Desktop\BTP\.agents\worker_m2
You MUST read C:\Users\Prem Pastagia\Desktop\BTP\.agents\ORIGINAL_REQUEST.md before beginning.
You must also read:
- C:\Users\Prem Pastagia\Desktop\BTP\PROJECT.md
- C:\Users\Prem Pastagia\Desktop\BTP\TEST_INFRA.md
- C:\Users\Prem Pastagia\Desktop\BTP\TEST_READY.md
- C:\Users\Prem Pastagia\Desktop\BTP\.agents\survey_explorer_2\report.md
- C:\Users\Prem Pastagia\Desktop\BTP\.agents\survey_explorer_2\handoff.md

Your exclusive write ownership:
- src/__init__.py
- src/gram_schmidt.py
- src/gam_pipeline.py
- src/arima_baseline.py
- src/evaluate.py
- output/model_results.json
- output/figures/ (and paper/figures/)
- output/tables/ (and paper/tables/)

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your mission:
Implement Milestone 2 (Econometric & Machine Learning Modeling Pipeline):
1. `src/gram_schmidt.py`:
   - Implement diagnostic test for multicollinearity: compute Variance Inflation Factors (VIF) and Pearson correlation matrix across macroeconomic regressors (GDP and Income/PFCE).
   - MULTICOLLINEARITY CONSTRAINT: If and only if multicollinearity is detected (e.g. VIF > 5.0 or |r| > 0.80), automatically execute Modified Gram-Schmidt orthogonalization before passing variables to GAM. Keep GDP as reference vector and project Income/CPI onto its orthogonal complement. Return orthogonalized design matrix and diagnostic before/after VIF metrics.
2. `src/gam_pipeline.py`:
   - Implement Generalized Additive Model using `statsmodels.gam.api.GLMGam` (with Gaussian family and identity link).
   - Incorporate:
     a. Standardized polynomial trend term (degree d in {1, 2, 3}).
     b. Harmonic Fourier seasonal basis: sin(2*pi*k*t/12) and cos(2*pi*k*t/12) for k in {1, 2} (period 12 months).
     c. Penalized smooth B-splines (`BSplines(df=5, degree=3)`) for macroeconomic drivers (GDP, orthogonalized Income/CPI).
   - Generate high-resolution Partial Dependence Plots (PDPs) with 95% Bayesian credible intervals using `plot_partial(plot_se=True)` saving to `output/figures/fig_gam_pdp.png` and `paper/figures/fig_gam_pdp.png`.
3. `src/arima_baseline.py`:
   - Implement baseline linear model (ARIMA) using `statsmodels.tsa.arima.model.ARIMA`.
   - Implement automated grid-search over (p, d, q) selecting optimal order via AIC/BIC.
4. `src/evaluate.py`:
   - Merge `data/cng_data.csv` and `data/macro_data.csv`.
   - Implement rolling / expanding window walk-forward time-series cross-validation (zero lookahead bias).
   - Compute quantitative out-of-sample RMSE, MAE, and percentage improvement for GAM vs ARIMA.
   - Generate forecast comparison plot (`fig_forecast_comparison.png`) and residual diagnostics (`fig_residual_diagnostics.png`).
   - Export quantitative benchmark results to `output/model_results.json` containing: `rmse_gam`, `rmse_arima`, `mae_gam`, `mae_arima`, `pct_improvement`, `vif_before`, `vif_after`, `orthogonalization_applied`, `superior_model`.
   - Export summary tables to `output/tables/` and `paper/tables/` (`table_descriptives.tex`, `table_model_comparison.tex`, `table_gam_components.tex`).
5. Run the test suite: verify that all Tier 1 and Tier 2 modeling tests (`test_f2_*`, `test_f3_*`, `test_f4_*`, `test_b2_*`, `test_b3_*`, `test_b4_*`) pass.
6. Write your handoff to C:\Users\Prem Pastagia\Desktop\BTP\.agents\worker_m2\handoff.md and notify orchestrator.
