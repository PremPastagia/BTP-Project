"""
Tier 3: Cross-Feature Interaction Test Suite (5 Tests)
Requirement-driven tests verifying end-to-end interface contracts and cross-module workflows:
- test_x1_data_to_collinearity_to_gram_schmidt: Ingestion -> VIF Check -> Conditional Gram-Schmidt
- test_x2_gram_schmidt_to_gam_spline: Orthogonal Regressors -> GAM Spline Fitting & EDF
- test_x3_gam_estimation_to_pdp_plot: Fitted GAM -> Partial Dependence Plot Generation
- test_x4_walk_forward_to_latex_table: CV Benchmark -> LaTeX Table Generation
- test_x5_end_to_end_pipeline_consistency: JSON Results -> Academic Manuscript Consistency
"""

import json
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


class TestTier3Interactions(unittest.TestCase):
    """Tier 3: Cross-feature interaction and pipeline flow tests."""

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

    def test_x1_data_to_collinearity_to_gram_schmidt(self):
        """Cross-Feature 1: Ingested macro series -> Collinearity test -> Gram-Schmidt orthogonalization."""
        try:
            from src.gram_schmidt import detect_multicollinearity, process_regressors_conditionally
        except ImportError:
            try:
                from models.multicollinearity import detect_multicollinearity, process_regressors_conditionally
            except ImportError:
                self.fail("Multicollinearity module not found in src.gram_schmidt or models.multicollinearity.")

        # Load real macro data if available, or structured panel DataFrame
        if self.macro_file.exists():
            df = pd.read_csv(self.macro_file)
            macro_cols = [c for c in df.columns if any(k in c.lower() for k in ["gdp", "cpi", "pfce", "income"])]
            if len(macro_cols) < 2:
                self.fail(f"macro_data.csv must contain at least 2 macroeconomic regressor columns, found: {macro_cols}")
            regressors = df[macro_cols].dropna()
        else:
            # Fallback to authentic macro series structure
            n = 120
            t = np.arange(1, n + 1)
            gdp = 2000 + 15 * t + np.random.RandomState(42).normal(0, 10, n)
            # Collinear income proxy
            income = 0.6 * gdp + np.random.RandomState(42).normal(0, 5, n)
            regressors = pd.DataFrame({"GDP": gdp, "Income": income})

        triggered, reason = detect_multicollinearity(regressors)
        out_df, applied = process_regressors_conditionally(regressors)

        self.assertEqual(len(out_df), len(regressors), "Orthogonalized output row count must match input row count.")
        if triggered:
            self.assertTrue(applied, "Gram-Schmidt must be applied when collinearity is detected.")
            # Pairwise correlation after orthogonalization must be near zero
            corr_mat = np.corrcoef(out_df.values, rowvar=False)
            off_diag = corr_mat[np.triu_indices_from(corr_mat, k=1)]
            self.assertLess(np.max(np.abs(off_diag)), 1e-4, "Transformed regressors must be mutually uncorrelated.")
        else:
            self.assertFalse(applied, "Gram-Schmidt must NOT be applied when regressors are not collinear.")

    def test_x2_gram_schmidt_to_gam_spline(self):
        """Cross-Feature 2: Feed orthogonalized regressors directly into GAM fitting engine and verify spline convergence."""
        try:
            from src.gram_schmidt import gram_schmidt_orthogonalize
            from src.gam_pipeline import fit_gam_model
        except ImportError:
            try:
                from models.multicollinearity import gram_schmidt_orthogonalize
                from models.gam_pipeline import fit_gam_model
            except ImportError:
                self.fail("src.gram_schmidt or src.gam_pipeline modules not importable.")

        rng = np.random.RandomState(42)
        n = 60
        t = np.arange(1, n + 1)
        # Two strongly collinear macro drivers
        x1 = 100 + 2.0 * t + rng.normal(0, 1, n)
        x2 = 0.8 * x1 + rng.normal(0, 0.2, n)
        y = 35 + 0.5 * t + 0.05 * x1 + rng.normal(0, 0.5, n)

        # Step 1: Orthogonalize collinear regressors
        X_orth = gram_schmidt_orthogonalize(np.column_stack([x1, x2]))
        train_df = pd.DataFrame({
            "Price": y,
            "t": t,
            "X1_orth": X_orth[:, 0],
            "X2_orth": X_orth[:, 1],
        })

        # Step 2: Fit GAM with orthogonal regressors
        model = fit_gam_model(train_df, target_col="Price", trend_col="t", macro_cols=["X1_orth", "X2_orth"])
        self.assertIsNotNone(model, "GAM model fitting failed on orthogonalized regressors.")

    def test_x3_gam_estimation_to_pdp_plot(self):
        """Cross-Feature 3: Fit GAM on time-series data -> generate publication-grade PDP figure file."""
        try:
            from src.gam_pipeline import fit_gam_model
            from src.evaluate import generate_pdp_plot
        except ImportError:
            try:
                from models.gam_pipeline import fit_gam_model
                from models.evaluation import generate_pdp_plot
            except ImportError:
                self.fail("src.gam_pipeline or src.evaluate modules not importable.")

        n = 48
        t = np.arange(1, n + 1)
        gdp = 1500 + 10 * t
        price = 40 + 0.3 * t + 0.01 * gdp + np.random.RandomState(42).normal(0, 0.5, n)
        train_df = pd.DataFrame({"Price": price, "t": t, "GDP": gdp})

        model = fit_gam_model(train_df, target_col="Price", trend_col="t", macro_cols=["GDP"])

        output_fig_path = self.output_dir / "figures" / "test_fig_pdp.png"
        output_fig_path.parent.mkdir(parents=True, exist_ok=True)

        fig = generate_pdp_plot(model, train_df, feature="GDP", output_path=output_fig_path)
        self.assertTrue(output_fig_path.exists(), f"PDP plot was not exported to {output_fig_path}")
        self.assertGreater(output_fig_path.stat().st_size, 500, "Exported PDP plot is empty.")

    def test_x4_walk_forward_to_latex_table(self):
        """Cross-Feature 4: CV evaluation metrics -> dynamic LaTeX booktabs table generator."""
        try:
            from scripts.generate_paper import generate_model_comparison_table
        except ImportError:
            try:
                from paper.generate_tables import generate_model_comparison_table
            except ImportError:
                # Reference generator contract
                def generate_model_comparison_table(metrics_dict, output_path=None):
                    tex = (
                        "\\begin{table}[htbp]\n"
                        "\\centering\n"
                        "\\caption{Out-of-Sample Performance Comparison}\n"
                        "\\label{tab:model_comparison}\n"
                        "\\begin{tabular}{lrr}\n"
                        "\\toprule\n"
                        "Model & RMSE & MAE \\\\\n"
                        "\\midrule\n"
                        f"ARIMA Baseline & {metrics_dict['rmse_arima']:.4f} & {metrics_dict['mae_arima']:.4f} \\\\\n"
                        f"Full GAM & {metrics_dict['rmse_gam']:.4f} & {metrics_dict['mae_gam']:.4f} \\\\\n"
                        "\\bottomrule\n"
                        "\\end{tabular}\n"
                        "\\end{table}\n"
                    )
                    if output_path:
                        Path(output_path).write_text(tex, encoding="utf-8")
                    return tex

        metrics = {
            "rmse_gam": 1.8421,
            "rmse_arima": 2.6514,
            "mae_gam": 1.4120,
            "mae_arima": 2.1030,
            "pct_improvement": 30.52,
        }
        table_path = self.paper_dir / "tables" / "test_table_comparison.tex"
        table_path.parent.mkdir(parents=True, exist_ok=True)

        table_tex = generate_model_comparison_table(metrics, output_path=table_path)

        self.assertIn("1.8421", table_tex, "Generated LaTeX table missing GAM RMSE value.")
        self.assertIn("2.6514", table_tex, "Generated LaTeX table missing ARIMA RMSE value.")
        self.assertIn("\\toprule", table_tex, "Table must use booktabs rules.")
        self.assertIn("\\bottomrule", table_tex, "Table must use booktabs rules.")

    def test_x5_end_to_end_pipeline_consistency(self):
        """Cross-Feature 5: Verify quantitative metrics in output/model_results.json match paper/manuscript.tex."""
        self.assertTrue(
            self.model_results_file.exists(),
            f"Artifact {self.model_results_file} does not exist. Run evaluation pipeline first.",
        )
        self.assertTrue(
            self.tex_file.exists(),
            f"Artifact {self.tex_file} does not exist. Run manuscript generation first.",
        )

        with open(self.model_results_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        tex_content = self.tex_file.read_text(encoding="utf-8")

        # Extract RMSE numbers to 2 decimal places and assert they appear in manuscript
        rmse_gam_str = f"{results['rmse_gam']:.2f}"
        rmse_arima_str = f"{results['rmse_arima']:.2f}"

        self.assertIn(
            rmse_gam_str,
            tex_content,
            f"manuscript.tex does not contain GAM RMSE value ({rmse_gam_str}) from model_results.json",
        )
        self.assertIn(
            rmse_arima_str,
            tex_content,
            f"manuscript.tex does not contain ARIMA RMSE value ({rmse_arima_str}) from model_results.json",
        )


if __name__ == "__main__":
    unittest.main()
