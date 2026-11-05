"""
Milestone 2 Modeling Pipeline Unit and Integration Test Suite.
Tests all functions in:
- src.gram_schmidt
- src.gam_pipeline
- src.arima_baseline
- src.evaluate
"""

import json
import math
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

from src.gram_schmidt import (
    compute_vif,
    detect_multicollinearity,
    gram_schmidt_orthogonalize,
    process_regressors_conditionally,
)
from src.gam_pipeline import (
    build_gam_spec,
    build_harmonic_basis,
    build_polynomial_trend,
    build_spline_basis,
    fit_gam_model,
    predict_gam,
)
from src.arima_baseline import (
    fit_arima,
    forecast_arima,
    select_arima_order,
)
from src.evaluate import (
    calculate_mae,
    calculate_mape,
    calculate_rmse,
    determine_superior_model,
    evaluate_forecast_horizons,
    generate_pdp_plot,
    walk_forward_cv_splits,
)


class TestMilestone2Modeling(unittest.TestCase):
    """Behavioral and edge-case unit tests for Milestone 2."""

    def setUp(self):
        self.rng = np.random.RandomState(42)

    # -------------------------------------------------------------------------
    # Gram-Schmidt & Multicollinearity Tests
    # -------------------------------------------------------------------------
    def test_compute_vif_single_column(self):
        df = pd.DataFrame({"X": self.rng.normal(0, 1, 50)})
        vifs = compute_vif(df)
        self.assertEqual(vifs, {"X": 1.0})

    def test_compute_vif_orthogonal(self):
        x1 = self.rng.normal(0, 1, 100)
        x2 = self.rng.normal(0, 1, 100)
        df = pd.DataFrame({"x1": x1, "x2": x2})
        vifs = compute_vif(df)
        self.assertAlmostEqual(vifs["x1"], 1.0, delta=0.2)
        self.assertAlmostEqual(vifs["x2"], 1.0, delta=0.2)

    def test_detect_multicollinearity_clean(self):
        x1 = self.rng.normal(0, 1, 80)
        x2 = self.rng.normal(0, 1, 80)
        df = pd.DataFrame({"x1": x1, "x2": x2})
        triggered, reason = detect_multicollinearity(df, vif_threshold=5.0, corr_threshold=0.80)
        self.assertFalse(triggered)
        self.assertIn("No multicollinearity", reason)

    def test_detect_multicollinearity_triggered(self):
        x1 = self.rng.normal(0, 1, 80)
        x2 = 0.95 * x1 + self.rng.normal(0, 0.05, 80)
        df = pd.DataFrame({"x1": x1, "x2": x2})
        triggered, reason = detect_multicollinearity(df, vif_threshold=5.0, corr_threshold=0.80)
        self.assertTrue(triggered)
        self.assertIn("Multicollinearity detected", reason)

    def test_gram_schmidt_orthogonalize_properties(self):
        x1 = self.rng.normal(0, 1, 80)
        x2 = 0.8 * x1 + self.rng.normal(0, 0.2, 80)
        x3 = 0.5 * x1 + 0.5 * x2 + self.rng.normal(0, 0.1, 80)
        X = np.column_stack([x1, x2, x3])
        V = gram_schmidt_orthogonalize(X)
        self.assertEqual(V.shape, X.shape)
        # Verify pairwise dot products are zero
        for i in range(3):
            for j in range(i + 1, 3):
                norm_prod = np.linalg.norm(V[:, i]) * np.linalg.norm(V[:, j])
                dot = np.dot(V[:, i], V[:, j]) / norm_prod
                self.assertAlmostEqual(dot, 0.0, places=6)

    def test_process_regressors_conditionally(self):
        x1 = self.rng.normal(0, 1, 80)
        x2 = 2.0 * x1 + self.rng.normal(0, 0.05, 80)
        df = pd.DataFrame({"GDP": x1, "CPI": x2})
        out_df, applied = process_regressors_conditionally(df)
        self.assertTrue(applied)
        # GDP column must be preserved exactly
        np.testing.assert_allclose(out_df["GDP"].values, df["GDP"].values)
        # Post-orthogonal correlation must be zero
        r = np.corrcoef(out_df["GDP"].values, out_df["CPI"].values)[0, 1]
        self.assertAlmostEqual(r, 0.0, places=6)

    # -------------------------------------------------------------------------
    # GAM Pipeline Tests
    # -------------------------------------------------------------------------
    def test_polynomial_trend_degree_0_and_positive(self):
        t = np.arange(1, 21)
        d0 = build_polynomial_trend(t, degree=0)
        self.assertEqual(d0.shape, (20, 1))
        self.assertTrue((d0 == 1.0).all())

        d2 = build_polynomial_trend(t, degree=2)
        self.assertEqual(d2.shape, (20, 2))

    def test_harmonic_basis_orthogonality(self):
        t = np.arange(1, 13)
        basis = build_harmonic_basis(t, period=12, K=2)
        self.assertEqual(basis.shape, (12, 4))
        # Exact Fourier orthogonality over 12 months
        self.assertAlmostEqual(np.dot(basis[:, 0], basis[:, 1]), 0.0, places=6)
        self.assertAlmostEqual(np.dot(basis[:, 0], basis[:, 2]), 0.0, places=6)

    def test_spline_basis_shape(self):
        x = np.linspace(50, 150, 40)
        s = build_spline_basis(x, df=5, degree=3)
        self.assertEqual(s.shape, (40, 5))

    def test_fit_and_predict_gam(self):
        n = 45
        t = np.arange(1, n + 1)
        gdp = 1000 + 10 * t + self.rng.normal(0, 2, n)
        cpi = 100 + 0.3 * t + self.rng.normal(0, 0.5, n)
        price = 35 + 0.2 * t + 0.005 * gdp + self.rng.normal(0, 0.5, n)
        df = pd.DataFrame({"Price": price, "t": t, "GDP": gdp, "CPI": cpi})

        model = fit_gam_model(df, target_col="Price", trend_col="t", macro_cols=["GDP", "CPI"])
        self.assertIsNotNone(model)

        df_future = pd.DataFrame({
            "t": [46, 47, 48],
            "GDP": [1460, 1470, 1480],
            "CPI": [114, 114.3, 114.6],
        })
        preds = predict_gam(model, df_future)
        self.assertEqual(len(preds), 3)
        self.assertTrue((preds > 0).all())

    def test_gam_insufficient_sample_guard(self):
        short_df = pd.DataFrame({"Price": np.ones(10), "t": np.arange(10), "GDP": np.ones(10)})
        with self.assertRaises(ValueError):
            fit_gam_model(short_df, target_col="Price", trend_col="t", macro_cols=["GDP"])

    # -------------------------------------------------------------------------
    # ARIMA Baseline Tests
    # -------------------------------------------------------------------------
    def test_arima_fit_and_forecast(self):
        y = 30 + 0.3 * np.arange(50) + self.rng.normal(0, 0.5, 50)
        model = fit_arima(y, order=(1, 1, 1))
        self.assertIsNotNone(model)
        fc = forecast_arima(model, steps=4)
        self.assertEqual(len(fc), 4)
        self.assertFalse(np.isnan(fc).any())

    def test_arima_unit_root_selection(self):
        rw = np.cumsum(self.rng.normal(0.5, 1.0, 70))
        order = select_arima_order(rw)
        self.assertGreaterEqual(order[1], 1)

    # -------------------------------------------------------------------------
    # Evaluation & Metrics Tests
    # -------------------------------------------------------------------------
    def test_rmse_and_mae(self):
        y_t = np.array([10.0, 20.0, 30.0])
        y_p = np.array([12.0, 18.0, 30.0])
        self.assertAlmostEqual(calculate_rmse(y_t, y_p), math.sqrt(8.0 / 3.0), places=6)
        self.assertAlmostEqual(calculate_mae(y_t, y_p), 4.0 / 3.0, places=6)

    def test_mape_flat_regime_no_zero_division(self):
        y_t = np.array([50.0, 50.0, 50.0])
        y_p = np.array([50.0, 51.0, 49.0])
        mape = calculate_mape(y_t, y_p)
        self.assertFalse(np.isnan(mape))
        self.assertGreater(mape, 0.0)

    def test_walk_forward_splits_no_lookahead(self):
        splits = list(walk_forward_cv_splits(total_samples=30, min_train=24, horizon=2))
        self.assertGreater(len(splits), 0)
        for tr, te in splits:
            self.assertLess(np.max(tr), np.min(te))

    def test_walk_forward_splits_min_train_guard(self):
        with self.assertRaises(ValueError):
            list(walk_forward_cv_splits(total_samples=30, min_train=15, horizon=1))

    def test_determine_superior_model(self):
        self.assertEqual(determine_superior_model(rmse_gam=2.0, rmse_arima=3.0), "GAM")
        self.assertEqual(determine_superior_model(rmse_gam=3.5, rmse_arima=2.5), "ARIMA")
        # Tie break with AIC
        self.assertEqual(
            determine_superior_model(rmse_gam=2.0, rmse_arima=2.0, aic_gam=100.0, aic_arima=120.0),
            "GAM",
        )


if __name__ == "__main__":
    unittest.main()
