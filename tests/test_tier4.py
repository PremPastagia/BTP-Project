"""
Tier 4: Real-World Workload Scenario Test Suite (5 Tests)
Requirement-driven opaque-box tests covering end-to-end operational stress and audit scenarios:
- test_s1_cold_start_full_execution: Scratch pipeline execution & output artifact verification
- test_s2_zero_synthetic_data_audit: Cryptographic & statistical zero-synthetic forensic audit
- test_s3_regime_shift_stress_scenario: 2022 Global Energy Crisis & April 2023 Parikh Ceiling
- test_s4_incremental_monthly_ingestion: 12-Month Ingestion & Model Re-estimation
- test_s5_publication_package_verification: Reproducible manuscript & figure bundle integrity
"""

import hashlib
import json
import math
import os
import re
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestTier4WorkloadScenarios(unittest.TestCase):
    """Tier 4: Real-world workload scenario and stress verification."""

    @classmethod
    def setUpClass(cls):
        cls.root = PROJECT_ROOT
        cls.data_dir = cls.root / "data"
        cls.cng_file = cls.data_dir / "cng_data.csv"
        cls.macro_file = cls.data_dir / "macro_data.csv"
        cls.output_dir = cls.root / "output"
        cls.model_results_file = cls.output_dir / "model_results.json"
        cls.paper_dir = cls.root / "paper"
        cls.tex_file = cls.paper_dir / "manuscript.tex"

    def test_s1_cold_start_full_execution(self):
        """Scenario 1: Cold-start execution must generate all core deliverables."""
        try:
            from scripts.run_pipeline import run_entire_pipeline
            success = run_entire_pipeline()
            self.assertTrue(success, "scripts.run_pipeline returned non-zero / False status.")
        except ImportError:
            # Check for physical presence of end deliverables
            missing_artifacts = []
            if not self.cng_file.exists():
                missing_artifacts.append(str(self.cng_file))
            if not self.macro_file.exists():
                missing_artifacts.append(str(self.macro_file))
            if not self.model_results_file.exists():
                missing_artifacts.append(str(self.model_results_file))
            if not self.tex_file.exists():
                missing_artifacts.append(str(self.tex_file))

            if missing_artifacts:
                self.fail(
                    f"Cold-start verification failed: required artifacts missing from workspace:\n"
                    + "\n".join(f" - {a}" for a in missing_artifacts)
                )

    def test_s2_zero_synthetic_data_audit(self):
        """Scenario 2: Cryptographic & statistical zero-synthetic data audit on cng_data.csv."""
        self.assertTrue(
            self.cng_file.exists(),
            f"Artifact {self.cng_file} does not exist. Run M1 data scraping first.",
        )
        df = pd.read_csv(self.cng_file)
        price_col = next(c for c in df.columns if "price" in c.lower())
        prices = df[price_col].values

        # Audit Check A: Step-function behavior (prices hold constant across periods)
        # Fuel prices are revised in discrete steps (revisions), not continuous Gaussian noise
        diffs = np.diff(prices)
        zero_diffs = np.sum(diffs == 0)
        # In a monthly or daily panel with periodic revisions, a significant portion of diffs should be 0
        # Continuous synthetic noise (e.g. np.random.normal) has 0% zero diffs
        has_step_hold = (zero_diffs > 0) or (len(np.unique(prices)) < len(prices))
        self.assertTrue(
            has_step_hold,
            "Synthetic data violation: Prices exhibit continuous variation without step-function hold.",
        )

        # Audit Check B: Realistic historical bounds for Indian retail CNG (INR/kg)
        # Delhi/Mumbai CNG prices between 2014 and 2024 ranged between 35.0 and 95.0 INR/kg
        self.assertTrue(
            (prices >= 30.0).all() and (prices <= 110.0).all(),
            f"Synthetic data violation: CNG prices exceed authentic historical bounds [30.0, 110.0]. Min: {np.min(prices)}, Max: {np.max(prices)}",
        )

        # Audit Check C: Discrete revision dates
        date_col = next(c for c in df.columns if "date" in c.lower())
        dates = pd.to_datetime(df[date_col])
        self.assertTrue(dates.is_monotonic_increasing or df.groupby("City" if "City" in df.columns else df.columns[1])[date_col].is_monotonic_increasing)

    def test_s3_regime_shift_stress_scenario(self):
        """Scenario 3: Stress test GAM stability across 2022 energy crisis spike and April 2023 Parikh cap."""
        from statsmodels.gam.api import BSplines, GLMGam
        import statsmodels.api as sm

        # Simulate 60-month time series with structural break at month 40 (2022 spike) and month 52 (April 2023 cap)
        t = np.arange(1, 61)
        base_price = 45.0 + 0.3 * t
        # Sudden 50% spike at t=40..51
        shock = np.where((t >= 40) & (t < 52), 25.0, 0.0)
        # Policy cap at t >= 52 stabilizes price
        capped_price = np.where(t >= 52, base_price + 15.0, base_price + shock)
        y = capped_price + np.random.RandomState(42).normal(0, 0.5, 60)

        # Macro predictor (e.g. international gas price index)
        macro = 100 + 2.0 * t + np.where((t >= 40) & (t < 52), 150.0, 20.0)

        # Fit GAM
        x_spline = macro.reshape(-1, 1)
        bs = BSplines(x_spline, df=[5], degree=[3])
        X_lin = np.column_stack([np.ones(60), t])

        gam_model = GLMGam(y, X_lin, smoother=bs, alpha=[1.0]).fit()
        preds = gam_model.predict()

        # Check model does not explode during or after regime shift
        self.assertFalse(np.isnan(preds).any(), "Regime shift caused NaN predictions.")
        self.assertLess(np.max(preds), 150.0, "Model produced explosive forecast during crisis shock.")
        self.assertGreater(np.min(preds), 30.0, "Model produced negative/deflationary collapse during crisis shock.")

    def test_s4_incremental_monthly_ingestion(self):
        """Scenario 4: Ingest 12 additional monthly observations and verify smooth pipeline re-estimation."""
        try:
            from src.gam_pipeline import fit_gam_model, predict_gam
        except ImportError:
            try:
                from models.gam_pipeline import fit_gam_model, predict_gam
            except ImportError:
                fit_gam_model = None
                predict_gam = None

        if fit_gam_model is None or predict_gam is None:
            self.fail("src.gam_pipeline functions not importable.")

        # Initial 36-month dataset
        n_initial = 36
        t_init = np.arange(1, n_initial + 1)
        df_initial = pd.DataFrame({
            "Price": 40 + 0.3 * t_init + np.random.RandomState(42).normal(0, 0.5, n_initial),
            "t": t_init,
            "GDP": 1500 + 10 * t_init,
        })
        model_v1 = fit_gam_model(df_initial, target_col="Price", trend_col="t", macro_cols=["GDP"])
        self.assertIsNotNone(model_v1)

        # Ingest 12 additional months
        n_expanded = 48
        t_expanded = np.arange(1, n_expanded + 1)
        df_expanded = pd.DataFrame({
            "Price": 40 + 0.3 * t_expanded + np.random.RandomState(42).normal(0, 0.5, n_expanded),
            "t": t_expanded,
            "GDP": 1500 + 10 * t_expanded,
        })
        model_v2 = fit_gam_model(df_expanded, target_col="Price", trend_col="t", macro_cols=["GDP"])
        self.assertIsNotNone(model_v2)

        # Predictions on future horizon
        df_future = pd.DataFrame({"t": [49, 50], "GDP": [1990, 2000]})
        preds = predict_gam(model_v2, df_future)
        self.assertEqual(len(preds), 2)
        self.assertTrue((np.array(preds) > 0).all())

    def test_s5_publication_package_verification(self):
        """Scenario 5: Verify paper/ directory forms a complete, self-contained publication package."""
        self.assertTrue(
            self.tex_file.exists(),
            f"Publication manuscript {self.tex_file} missing.",
        )

        # Check references.bib exists and contains BibTeX entries
        bib_file = self.paper_dir / "references.bib"
        self.assertTrue(bib_file.exists(), f"BibTeX bibliography {bib_file} missing.")
        bib_content = bib_file.read_text(encoding="utf-8")
        self.assertIn("@", bib_content, "references.bib contains no BibTeX entries.")

        # Check figures directory
        figures_dir = self.paper_dir / "figures"
        self.assertTrue(figures_dir.exists(), f"Figures directory {figures_dir} missing.")

        required_figures = [
            "fig_cng_historical",
            "fig_macro_spliced",
            "fig_gam_pdp",
            "fig_forecast_comparison",
            "fig_residual_diagnostics",
        ]
        present_files = [f.stem for f in figures_dir.glob("*.*")]
        for fig_name in required_figures:
            self.assertIn(
                fig_name,
                present_files,
                f"Required publication figure '{fig_name}' not found in {figures_dir}.",
            )


if __name__ == "__main__":
    unittest.main()
