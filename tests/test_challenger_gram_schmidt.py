"""
Empirical Challenger Test Suite for src/gram_schmidt.py.
Adversarial Stress Testing for Milestone 2:
1. Multicollinearity Detection under Extreme Scenarios:
   - Perfect collinearity (y = 2x, y = 100x + 50)
   - Zero correlation / orthogonal matrices
   - Negative correlations (r = -1.0, -0.99, -0.85, -0.50)
   - Near-singular matrices (condition numbers 10^4 to 10^15)
   - Multivariate collinearity without pairwise high correlation (z = x1 + x2)
2. Modified Gram-Schmidt Numerical Stability:
   - Pairwise orthogonality |<v_i, v_j>| / (||v_i|| * ||v_j||) < 10^-7
   - Preservation of column space span
   - Anchor column invariance (GDP direction & values preserved)
   - Dynamic range and degenerate cases (zero columns, constant columns, duplicate columns)
3. End-to-End Compatibility with GAM Regressors.
"""

import math
import unittest
import numpy as np
import pandas as pd
from scipy.linalg import hilbert

from src.gram_schmidt import (
    compute_vif,
    detect_multicollinearity,
    gram_schmidt_orthogonalize,
    process_regressors_conditionally,
)


class TestAdversarialMulticollinearity(unittest.TestCase):
    """Adversarially challenge multicollinearity detection."""

    def setUp(self):
        self.rng = np.random.RandomState(42)

    # -------------------------------------------------------------------------
    # 1. Perfect Collinearity
    # -------------------------------------------------------------------------
    def test_perfect_positive_collinearity_y_equals_2x(self):
        """Test y = 2x exact linear dependency."""
        x = self.rng.normal(10, 2, 100)
        y = 2.0 * x
        df = pd.DataFrame({"X": x, "Y": y})
        
        vifs = compute_vif(df)
        triggered, reason = detect_multicollinearity(df)
        
        # Max correlation must be 1.0
        r = np.corrcoef(x, y)[0, 1]
        self.assertAlmostEqual(r, 1.0, places=7)
        self.assertTrue(triggered, f"Failed to detect perfect collinearity: {reason}")
        self.assertTrue(vifs["X"] >= 5.0 or vifs["Y"] >= 5.0, f"VIF unexpectedly low: {vifs}")

    def test_perfect_affine_collinearity(self):
        """Test y = 100 * x + 500 (affine scaling)."""
        x = self.rng.normal(5, 1, 120)
        y = 100.0 * x + 500.0
        df = pd.DataFrame({"X": x, "Y": y})
        
        triggered, reason = detect_multicollinearity(df)
        self.assertTrue(triggered, f"Failed to detect affine collinearity: {reason}")

    def test_multivariate_collinearity_low_pairwise_corr(self):
        """
        Multivariate collinearity where no pair has |r| >= 0.80,
        but z is an exact linear combination: z = x1 + x2.
        For independent standard normals, corr(x1, z) = 1/sqrt(2) approx 0.7071 < 0.80.
        Detection must rely on VIF.
        """
        n = 200
        x1 = self.rng.normal(0, 1, n)
        x2 = self.rng.normal(0, 1, n)
        z = x1 + x2  # Exact linear combination
        df = pd.DataFrame({"x1": x1, "x2": x2, "z": z})
        
        # Verify pairwise correlations are below 0.80 threshold
        corr = df.corr().values
        np.fill_diagonal(corr, 0.0)
        max_corr = np.max(np.abs(corr))
        self.assertLess(max_corr, 0.80, f"Max corr is {max_corr}, expected < 0.80")
        
        # Multicollinearity check
        vifs = compute_vif(df)
        triggered, reason = detect_multicollinearity(df)
        
        # VIF for z must be huge (inf or capped at 1e6)
        self.assertTrue(
            vifs["z"] >= 5.0 or triggered,
            f"Failed to detect multivariate collinearity with low pairwise correlation! VIFs: {vifs}, reason: {reason}"
        )
        self.assertTrue(triggered)

    # -------------------------------------------------------------------------
    # 2. Zero Correlation / Orthogonal Regressors
    # -------------------------------------------------------------------------
    def test_zero_correlation_independent_features(self):
        """Features with zero correlation must NOT trigger multicollinearity."""
        n = 500
        x1 = self.rng.normal(0, 1, n)
        x2 = self.rng.normal(0, 1, n)
        x3 = self.rng.normal(0, 1, n)
        df = pd.DataFrame({"x1": x1, "x2": x2, "x3": x3})
        
        vifs = compute_vif(df)
        triggered, reason = detect_multicollinearity(df)
        
        for col, v in vifs.items():
            self.assertLess(v, 2.0, f"VIF for {col} unexpectedly high: {v}")
        self.assertFalse(triggered, f"Incorrectly triggered for independent features: {reason}")
        
        # Verify process_regressors_conditionally does NOT alter data
        out_df, applied = process_regressors_conditionally(df)
        self.assertFalse(applied)
        pd.testing.assert_frame_equal(out_df, df)

    def test_exact_orthogonal_matrix(self):
        """Deterministically orthogonal columns (e.g. Q from QR) must NOT trigger."""
        n = 100
        A = self.rng.normal(0, 1, (n, 3))
        Q, _ = np.linalg.qr(A)
        df = pd.DataFrame(Q, columns=["q1", "q2", "q3"])
        
        vifs = compute_vif(df)
        triggered, reason = detect_multicollinearity(df)
        
        for col, v in vifs.items():
            self.assertAlmostEqual(v, 1.0, delta=0.05)
        self.assertFalse(triggered, f"Incorrectly triggered on orthogonal matrix: {reason}")
        
        out_df, applied = process_regressors_conditionally(df)
        self.assertFalse(applied)
        pd.testing.assert_frame_equal(out_df, df)

    # -------------------------------------------------------------------------
    # 3. Negative Correlations
    # -------------------------------------------------------------------------
    def test_perfect_negative_collinearity(self):
        """y = -2x (perfect negative collinearity, r = -1.0)."""
        x = self.rng.normal(10, 3, 100)
        y = -2.0 * x
        df = pd.DataFrame({"x": x, "y": y})
        
        r = np.corrcoef(x, y)[0, 1]
        self.assertAlmostEqual(r, -1.0, places=7)
        
        triggered, reason = detect_multicollinearity(df)
        self.assertTrue(triggered, f"Failed to detect r = -1.0: {reason}")

    def test_strong_negative_correlation(self):
        """r = -0.95 (strong negative correlation) must trigger."""
        n = 150
        x = self.rng.normal(0, 1, n)
        noise = self.rng.normal(0, 0.1, n)
        y = -x + noise
        df = pd.DataFrame({"x": x, "y": y})
        
        r = np.corrcoef(x, y)[0, 1]
        self.assertLess(r, -0.90)
        
        triggered, reason = detect_multicollinearity(df)
        self.assertTrue(triggered, f"Failed to trigger on strong negative correlation r={r:.4f}: {reason}")

    def test_moderate_negative_correlation_below_threshold(self):
        """r = -0.50 should NOT trigger (threshold is 0.80 and VIF is 1.33 < 5.0)."""
        n = 500
        x = self.rng.normal(0, 1, n)
        noise = self.rng.normal(0, math.sqrt(3), n)  # var(noise) = 3, var(x) = 1 -> corr = -1/2 = -0.5
        y = -x + noise
        df = pd.DataFrame({"x": x, "y": y})
        
        r = np.corrcoef(x, y)[0, 1]
        self.assertAlmostEqual(r, -0.50, delta=0.10)
        
        triggered, reason = detect_multicollinearity(df)
        self.assertFalse(triggered, f"Incorrectly triggered on moderate negative correlation r={r:.4f}: {reason}")

    # -------------------------------------------------------------------------
    # 4. Near-Singular Matrices
    # -------------------------------------------------------------------------
    def test_near_singular_matrix_eps_perturbation(self):
        """Near-singular matrix: x2 = x1 + eps with eps = 1e-6, 1e-10."""
        for eps in [1e-4, 1e-6, 1e-10]:
            x1 = self.rng.normal(10, 2, 100)
            x2 = x1 + eps * self.rng.normal(0, 1, 100)
            df = pd.DataFrame({"x1": x1, "x2": x2})
            
            triggered, reason = detect_multicollinearity(df)
            self.assertTrue(triggered, f"Failed on near-singular eps={eps}: {reason}")

    def test_hilbert_matrix_severe_ill_conditioning(self):
        """Hilbert matrix is notoriously ill-conditioned."""
        H = hilbert(4)
        # Replicate rows to form samples
        X = np.tile(H, (25, 1)) + self.rng.normal(0, 1e-8, (100, 4))
        df = pd.DataFrame(X, columns=[f"h{i}" for i in range(4)])
        
        cond_num = np.linalg.cond(X)
        self.assertGreater(cond_num, 1e4)
        
        triggered, reason = detect_multicollinearity(df)
        self.assertTrue(triggered, f"Failed to detect ill-conditioned Hilbert matrix: {reason}")


class TestAdversarialGramSchmidtStability(unittest.TestCase):
    """Adversarially challenge Modified Gram-Schmidt numerical stability."""

    def setUp(self):
        self.rng = np.random.RandomState(123)

    # -------------------------------------------------------------------------
    # 1. Pairwise Orthogonality |<v_i, v_j>| < 10^-7
    # -------------------------------------------------------------------------
    def test_pairwise_orthogonality_random_collinear(self):
        """Verify normalized pairwise inner product |<v_i, v_j>| / (||v_i|| ||v_j||) < 10^-7."""
        n = 120
        x1 = self.rng.normal(50, 10, n)
        x2 = 0.9 * x1 + self.rng.normal(0, 2, n)
        x3 = -0.5 * x1 + 0.8 * x2 + self.rng.normal(0, 1, n)
        x4 = x1 + 2 * x2 - x3 + self.rng.normal(0, 0.5, n)
        X = np.column_stack([x1, x2, x3, x4])
        
        V = gram_schmidt_orthogonalize(X)
        
        p = X.shape[1]
        for i in range(p):
            norm_i = np.linalg.norm(V[:, i])
            self.assertGreater(norm_i, 1e-8, f"Unexpected zero vector at column {i}")
            for j in range(i + 1, p):
                norm_j = np.linalg.norm(V[:, j])
                cos_sim = abs(float(np.dot(V[:, i], V[:, j]))) / (norm_i * norm_j)
                self.assertLess(
                    cos_sim,
                    1e-7,
                    f"Pairwise orthogonality violated between col {i} and col {j}: {cos_sim:.2e} >= 1e-7"
                )

    def test_pairwise_orthogonality_real_macro_data(self):
        """Verify orthogonality on the actual project macro_data.csv regressors."""
        from pathlib import Path
        macro_csv = Path(__file__).resolve().parent.parent / "data" / "macro_data.csv"
        self.assertTrue(macro_csv.exists(), f"macro_data.csv not found at {macro_csv}")
        
        df = pd.read_csv(macro_csv)
        reg_cols = ["GDP_Monthly_Cr", "CPI_Index", "Income_PFCE_Cr"]
        X = df[reg_cols].values
        
        V = gram_schmidt_orthogonalize(X)
        p = X.shape[1]
        for i in range(p):
            norm_i = np.linalg.norm(V[:, i])
            for j in range(i + 1, p):
                norm_j = np.linalg.norm(V[:, j])
                cos_sim = abs(float(np.dot(V[:, i], V[:, j]))) / (norm_i * norm_j)
                self.assertLess(
                    cos_sim,
                    1e-7,
                    f"Macro data orthogonality violated between {reg_cols[i]} and {reg_cols[j]}: {cos_sim:.2e}"
                )

    def test_pairwise_orthogonality_severe_ill_conditioning(self):
        """Verify orthogonality under condition number > 10^10."""
        n = 100
        x1 = self.rng.normal(0, 1, n)
        x2 = x1 + 1e-6 * self.rng.normal(0, 1, n)
        x3 = x1 + x2 + 1e-6 * self.rng.normal(0, 1, n)
        X = np.column_stack([x1, x2, x3])
        
        V = gram_schmidt_orthogonalize(X)
        for i in range(3):
            norm_i = np.linalg.norm(V[:, i])
            for j in range(i + 1, 3):
                norm_j = np.linalg.norm(V[:, j])
                if norm_i > 1e-10 and norm_j > 1e-10:
                    cos_sim = abs(float(np.dot(V[:, i], V[:, j]))) / (norm_i * norm_j)
                    self.assertLess(
                        cos_sim,
                        1e-7,
                        f"Ill-conditioned orthogonality failure between col {i} and {j}: {cos_sim:.2e}"
                    )

    # -------------------------------------------------------------------------
    # 2. Preservation of Column Space Span
    # -------------------------------------------------------------------------
    def test_preservation_of_column_space_span_full_rank(self):
        """For full rank X, span(V) == span(X). Reconstruction ||X - V(V^+ X)||_F / ||X||_F < 1e-7."""
        n = 100
        X = self.rng.normal(10, 5, (n, 4))
        V = gram_schmidt_orthogonalize(X)
        
        # Projection of X onto span(V): P_V X
        # Since columns of V are orthogonal: P_V x = sum_k (<x, v_k> / <v_k, v_k>) v_k
        P_V_X = np.zeros_like(X)
        for k in range(V.shape[1]):
            v_k = V[:, k]
            denom = np.dot(v_k, v_k)
            for j in range(X.shape[1]):
                coeff = np.dot(X[:, j], v_k) / denom
                P_V_X[:, j] += coeff * v_k
                
        rel_error = np.linalg.norm(X - P_V_X, "fro") / np.linalg.norm(X, "fro")
        self.assertLess(
            rel_error,
            1e-7,
            f"Column space span not preserved! Relative reconstruction error {rel_error:.2e} >= 1e-7"
        )

    def test_preservation_of_column_space_span_rank_deficient(self):
        """For rank-deficient X (y = 2x), non-zero columns of V must span col(X)."""
        n = 80
        x1 = self.rng.normal(0, 1, n)
        x2 = 2.0 * x1  # exact duplicate
        x3 = self.rng.normal(0, 1, n)
        X = np.column_stack([x1, x2, x3])
        
        V = gram_schmidt_orthogonalize(X)
        
        # Column 1 should be zero-normed
        norm_v2 = np.linalg.norm(V[:, 1])
        self.assertAlmostEqual(norm_v2, 0.0, places=10, msg="Redundant column was not zeroed out")
        
        # The non-zero columns of V (columns 0 and 2) must span all columns of X
        V_active = V[:, [0, 2]]
        # Project X onto V_active
        P_V_X = np.zeros_like(X)
        for k in range(V_active.shape[1]):
            v_k = V_active[:, k]
            denom = np.dot(v_k, v_k)
            for j in range(X.shape[1]):
                coeff = np.dot(X[:, j], v_k) / denom
                P_V_X[:, j] += coeff * v_k
                
        rel_error = np.linalg.norm(X - P_V_X, "fro") / np.linalg.norm(X, "fro")
        self.assertLess(
            rel_error,
            1e-7,
            f"Active subspace failed to reconstruct rank-deficient X: {rel_error:.2e}"
        )

    # -------------------------------------------------------------------------
    # 3. Anchor Column Invariance
    # -------------------------------------------------------------------------
    def test_anchor_column_identity_in_gram_schmidt_orthogonalize(self):
        """In gram_schmidt_orthogonalize, V[:, 0] must identically equal X[:, 0]."""
        n = 60
        X = self.rng.normal(100, 20, (n, 3))
        V = gram_schmidt_orthogonalize(X)
        np.testing.assert_array_equal(
            V[:, 0],
            X[:, 0],
            err_msg="Anchor column 0 modified in gram_schmidt_orthogonalize!"
        )

    def test_anchor_column_identity_in_process_regressors_conditionally(self):
        """In process_regressors_conditionally, df.iloc[:, 0] must be preserved verbatim."""
        n = 100
        gdp = 1e5 + 500 * np.arange(n) + self.rng.normal(0, 50, n)
        cpi = 100 + 0.5 * np.arange(n) + 0.001 * gdp + self.rng.normal(0, 0.2, n)
        income = 0.6 * gdp + self.rng.normal(0, 20, n)
        df = pd.DataFrame({"GDP": gdp, "CPI": cpi, "Income": income})
        
        out_df, applied = process_regressors_conditionally(df)
        self.assertTrue(applied)
        
        # Verbatim equality on GDP anchor column
        np.testing.assert_array_equal(
            out_df["GDP"].values,
            df["GDP"].values,
            err_msg="GDP anchor column modified in process_regressors_conditionally!"
        )
        
        # Post-processed correlations of CPI and Income with GDP must be zero
        r_gdp_cpi = np.corrcoef(out_df["GDP"].values, out_df["CPI"].values)[0, 1]
        r_gdp_inc = np.corrcoef(out_df["GDP"].values, out_df["Income"].values)[0, 1]
        self.assertAlmostEqual(abs(r_gdp_cpi), 0.0, places=7, msg=f"Post-processed r(GDP, CPI) = {r_gdp_cpi:.2e}")
        self.assertAlmostEqual(abs(r_gdp_inc), 0.0, places=7, msg=f"Post-processed r(GDP, Inc) = {r_gdp_inc:.2e}")

    # -------------------------------------------------------------------------
    # 4. Extreme Degenerate and Dynamic Range Cases
    # -------------------------------------------------------------------------
    def test_extreme_dynamic_range(self):
        """Regressors differing in scale by 10^12."""
        n = 100
        x1 = self.rng.normal(0, 1e8, n)   # Scale 10^8
        x2 = 0.9 * x1 + self.rng.normal(0, 1e-4, n)  # Scale 10^8 with tiny noise
        x3 = self.rng.normal(0, 1e-6, n)  # Scale 10^-6
        X = np.column_stack([x1, x2, x3])
        
        V = gram_schmidt_orthogonalize(X)
        self.assertEqual(V.shape, X.shape)
        self.assertFalse(np.isnan(V).any(), "NaN found in dynamic range test")
        self.assertFalse(np.isinf(V).any(), "Inf found in dynamic range test")
        
        # Orthogonality for non-zero vectors
        for i in range(3):
            norm_i = np.linalg.norm(V[:, i])
            for j in range(i + 1, 3):
                norm_j = np.linalg.norm(V[:, j])
                if norm_i > 1e-12 and norm_j > 1e-12:
                    cos_sim = abs(float(np.dot(V[:, i], V[:, j]))) / (norm_i * norm_j)
                    self.assertLess(cos_sim, 1e-7)

    def test_constant_column(self):
        """One column has zero variance (constant)."""
        n = 50
        x1 = self.rng.normal(5, 1, n)
        x2 = np.full(n, 42.0)  # Constant
        df = pd.DataFrame({"x1": x1, "x2": x2})
        
        vifs = compute_vif(df)
        self.assertIn("x1", vifs)
        self.assertIn("x2", vifs)
        # Check that compute_vif does not crash
        self.assertFalse(math.isnan(vifs["x1"]))
        self.assertFalse(math.isnan(vifs["x2"]))

    def test_single_column_input(self):
        """Single column dataframe should return VIF=1.0 and applied=False."""
        df = pd.DataFrame({"X": np.arange(50, dtype=float)})
        vifs = compute_vif(df)
        self.assertEqual(vifs, {"X": 1.0})
        
        triggered, _ = detect_multicollinearity(df)
        self.assertFalse(triggered)
        
        out_df, applied = process_regressors_conditionally(df)
        self.assertFalse(applied)
        pd.testing.assert_frame_equal(out_df, df)


if __name__ == "__main__":
    unittest.main()
