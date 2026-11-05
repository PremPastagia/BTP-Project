"""
Modified Gram-Schmidt Orthogonalization and Multicollinearity Diagnostic Engine.
Implements Requirement R2:
- Variance Inflation Factor (VIF) and Pearson correlation diagnostics.
- Conditional Modified Gram-Schmidt orthogonalization when VIF > 5.0 or |r| > 0.80.
- Reference vector preservation (GDP anchor) with projection of secondary regressors onto orthogonal complements.
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor


def compute_vif(df: pd.DataFrame) -> Dict[str, float]:
    """
    Computes Variance Inflation Factor (VIF) for each column in df.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of regressor series.
        
    Returns
    -------
    dict[str, float]
        Dictionary mapping column name to computed VIF.
    """
    cols = list(df.columns)
    p = len(cols)
    if p <= 1:
        return {col: 1.0 for col in cols}

    X = df.values.astype(float)
    n = len(X)
    X_const = np.column_stack([np.ones(n), X])

    vifs: Dict[str, float] = {}
    for i, col in enumerate(cols):
        try:
            v = float(variance_inflation_factor(X_const, i + 1))
            if np.isnan(v) or np.isinf(v):
                v = 1e6
        except Exception:
            v = 1.0
        vifs[col] = v

    return vifs


def detect_multicollinearity(
    df: pd.DataFrame,
    vif_threshold: float = 5.0,
    corr_threshold: float = 0.80,
) -> Tuple[bool, str]:
    """
    Tests for multicollinearity among regressors based on VIF and Pearson correlation.
    
    Parameters
    ----------
    df : pd.DataFrame
        Regressor DataFrame.
    vif_threshold : float, default=5.0
        VIF threshold triggering multicollinearity warning.
    corr_threshold : float, default=0.80
        Maximum absolute pairwise correlation threshold triggering multicollinearity.
        
    Returns
    -------
    tuple[bool, str]
        (triggered, reason)
    """
    X = df.values.astype(float)
    p = X.shape[1]
    vifs = compute_vif(df)
    max_vif = max(vifs.values()) if vifs else 1.0

    if p >= 2:
        corr_mat = np.corrcoef(X, rowvar=False)
        np.fill_diagonal(corr_mat, 0.0)
        max_corr = float(np.max(np.abs(corr_mat)))
    else:
        max_corr = 0.0

    triggered = (max_vif >= vif_threshold) or (max_corr >= corr_threshold)
    if triggered:
        reason = (
            f"Multicollinearity detected: max VIF {max_vif:.2f} >= {vif_threshold} "
            f"or max |r| {max_corr:.4f} >= {corr_threshold}"
        )
    else:
        reason = (
            f"No multicollinearity detected: max VIF {max_vif:.2f} < {vif_threshold} "
            f"and max |r| {max_corr:.4f} < {corr_threshold}"
        )

    return triggered, reason


def gram_schmidt_orthogonalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """
    Executes Modified Gram-Schmidt orthogonalization across columns of X.
    Guarantees pairwise inner products <v_i, v_j> = 0 for all i != j.
    Handles linearly dependent vectors, zero variance, and near-singular matrices.
    
    Parameters
    ----------
    X : np.ndarray
        Design matrix (n_samples, n_features).
    eps : float, default=1e-12
        Zero-norm tolerance threshold.
        
    Returns
    -------
    np.ndarray
        Orthogonalized matrix V of shape (n_samples, n_features).
    """
    X_arr = np.asarray(X, dtype=float)
    n, p = X_arr.shape
    V = np.zeros_like(X_arr, dtype=float)

    for i in range(p):
        v = X_arr[:, i].copy()
        for j in range(i):
            denom = float(np.dot(V[:, j], V[:, j]))
            if denom > eps:
                proj = (float(np.dot(v, V[:, j])) / denom) * V[:, j]
                v -= proj
        norm = float(np.linalg.norm(v))
        if norm < eps:
            v = np.zeros_like(v)
        V[:, i] = v

    return V


def process_regressors_conditionally(
    df: pd.DataFrame,
    vif_threshold: float = 5.0,
    corr_threshold: float = 0.80,
) -> Tuple[pd.DataFrame, bool]:
    """
    Conditional execution gate for multicollinearity:
    Runs Modified Gram-Schmidt orthogonalization IF AND ONLY IF multicollinearity is detected.
    Preserves column 0 (GDP reference anchor) unprojected, and projects secondary regressors
    (CPI, Income) onto the orthogonal complement of preceding vectors.
    
    Parameters
    ----------
    df : pd.DataFrame
        Regressor DataFrame.
    vif_threshold : float, default=5.0
    corr_threshold : float, default=0.80
    
    Returns
    -------
    tuple[pd.DataFrame, bool]
        (processed_df, applied)
    """
    triggered, reason = detect_multicollinearity(
        df, vif_threshold=vif_threshold, corr_threshold=corr_threshold
    )
    if not triggered:
        return df.copy(), False

    X = df.values.astype(float)
    n, p = X.shape

    means = np.mean(X, axis=0)
    X_c = X - means

    U = np.zeros_like(X_c)
    U[:, 0] = X_c[:, 0]

    for j in range(1, p):
        v = X_c[:, j].copy()
        for k in range(j):
            denom = float(np.dot(U[:, k], U[:, k]))
            if denom > 1e-12:
                proj = (float(np.dot(v, U[:, k])) / denom) * U[:, k]
                v -= proj
        U[:, j] = v

    for j in range(p):
        std_u = float(np.std(U[:, j]))
        std_orig = float(np.std(X[:, j]))
        if std_u > 1e-12:
            U[:, j] = (U[:, j] / std_u) * std_orig

    X_out = U + means
    # Preserve exact raw values for reference column 0
    X_out[:, 0] = X[:, 0]

    out_df = pd.DataFrame(X_out, columns=df.columns, index=df.index)
    return out_df, True
