"""
Generalized Additive Model (GAM) Pipeline for Natural Gas Price Forecasting.
Implements Requirement R2:
- Standardized polynomial trend component (order d in {1, 2, 3}).
- Truncated Fourier harmonic basis for monthly seasonality (k in {1, 2}, period 12).
- Penalized smooth B-splines (BSplines(df=5, degree=3)) for macroeconomic demand drivers.
- Convergence execution, model fitting, and out-of-sample positive prediction.
"""

from typing import List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import patsy
import statsmodels.api as sm
from statsmodels.gam.api import BSplines, GLMGam


def build_polynomial_trend(t: np.ndarray, degree: int = 1) -> np.ndarray:
    """
    Constructs standardized polynomial trend basis of degree d.
    Standardization prevents Runge phenomenon and ill-conditioned matrix explosion.
    
    Parameters
    ----------
    t : np.ndarray
        Time index array.
    degree : int, default=1
        Polynomial degree. If 0, returns column of ones (flat intercept).
        
    Returns
    -------
    np.ndarray
        Array of shape (len(t), max(degree, 1)).
    """
    t_arr = np.asarray(t, dtype=float)
    n = len(t_arr)
    if degree == 0:
        return np.ones((n, 1), dtype=float)

    std_val = float(np.std(t_arr))
    t_std = (t_arr - float(np.mean(t_arr))) / (std_val if std_val > 1e-12 else 1.0)
    return np.column_stack([t_std**d for d in range(1, degree + 1)])


def build_harmonic_basis(t: np.ndarray, period: int = 12, K: int = 2) -> np.ndarray:
    """
    Constructs exact orthogonal Fourier harmonic seasonal basis.
    For each harmonic k in {1, ..., K}, adds sin(2*pi*k*t/period) and cos(2*pi*k*t/period).
    
    Parameters
    ----------
    t : np.ndarray
        Time or month index.
    period : int, default=12
        Seasonal period (12 for monthly).
    K : int, default=2
        Number of Fourier harmonics.
        
    Returns
    -------
    np.ndarray
        Array of shape (len(t), 2*K).
    """
    t_arr = np.asarray(t, dtype=float)
    cols = []
    for k in range(1, K + 1):
        cols.append(np.sin(2.0 * np.pi * k * t_arr / float(period)))
        cols.append(np.cos(2.0 * np.pi * k * t_arr / float(period)))
    return np.column_stack(cols)


def build_spline_basis(x: np.ndarray, df: int = 5, degree: int = 3) -> np.ndarray:
    """
    Constructs B-spline basis matrix of given degrees of freedom and degree.
    
    Parameters
    ----------
    x : np.ndarray
        Regressor variable array.
    df : int, default=5
        Degrees of freedom.
    degree : int, default=3
        Spline degree (3 for cubic).
        
    Returns
    -------
    np.ndarray
        Array of shape (len(x), df).
    """
    x_arr = np.asarray(x, dtype=float).flatten()
    formula = f"bs(x, df={df}, degree={degree}, include_intercept=True) - 1"
    mat = patsy.dmatrix(formula, {"x": x_arr}, return_type="matrix")
    return np.asarray(mat, dtype=float)


def build_gam_spec(
    t: np.ndarray,
    macro_data: np.ndarray,
    trend_degree: int = 1,
    fourier_k: int = 2,
    df_spline: int = 5,
    degree_spline: int = 3,
) -> Tuple[np.ndarray, BSplines]:
    """
    Constructs the linear exogenous design matrix and BSplines smoother specification.
    
    Parameters
    ----------
    t : np.ndarray
        Time index.
    macro_data : np.ndarray
        Macroeconomic regressor matrix.
    trend_degree : int, default=1
    fourier_k : int, default=2
    df_spline : int, default=5
    degree_spline : int, default=3
    
    Returns
    -------
    tuple[np.ndarray, BSplines]
        (exog_linear, smoother)
    """
    t_arr = np.asarray(t, dtype=float)
    macro_mat = np.asarray(macro_data, dtype=float)
    if macro_mat.ndim == 1:
        macro_mat = macro_mat.reshape(-1, 1)
    p = macro_mat.shape[1]

    trend_terms = build_polynomial_trend(t_arr, degree=trend_degree)
    harmonic_terms = build_harmonic_basis(t_arr, period=12, K=fourier_k)
    exog_linear = np.column_stack([np.ones(len(t_arr)), trend_terms, harmonic_terms])

    knot_kwds = []
    for j in range(p):
        c_min = float(np.min(macro_mat[:, j]))
        c_max = float(np.max(macro_mat[:, j]))
        span = max(c_max - c_min, 1.0)
        knot_kwds.append({
            "lower_bound": c_min - 5.0 * span,
            "upper_bound": c_max + 5.0 * span,
        })

    smoother = BSplines(
        macro_mat,
        df=[df_spline] * p,
        degree=[degree_spline] * p,
        knot_kwds=knot_kwds,
    )
    return exog_linear, smoother


def fit_gam_model(
    df: pd.DataFrame,
    target_col: str = "Price",
    trend_col: str = "t",
    macro_cols: Optional[List[str]] = None,
    trend_degree: int = 1,
    fourier_k: int = 2,
    df_spline: int = 5,
    degree_spline: int = 3,
    alpha: Union[float, List[float]] = 1.0,
) -> object:
    """
    Fits Generalized Additive Model (statsmodels.gam.api.GLMGam) using Gaussian family.
    
    Parameters
    ----------
    df : pd.DataFrame
        Training data containing target, trend, and macro columns.
    target_col : str, default='Price'
    trend_col : str, default='t'
    macro_cols : list[str], optional
        List of continuous macroeconomic regressor columns.
    trend_degree : int, default=1
    fourier_k : int, default=2
    df_spline : int, default=5
    degree_spline : int, default=3
    alpha : float or list[float], default=1.0
        Smoothing penalty weight.
        
    Returns
    -------
    GLMGamResults
        Fitted GAM model results object with attached pipeline metadata.
    """
    n_samples = len(df)
    if n_samples < 20:
        raise ValueError(
            f"Insufficient sample size N={n_samples} for GAM estimation with splines (minimum N=20)."
        )

    if macro_cols is None:
        exclude = {target_col.lower(), trend_col.lower(), "date", "city", "distributor"}
        macro_cols = [c for c in df.columns if c.lower() not in exclude]

    y = df[target_col].values.astype(float)
    t = df[trend_col].values.astype(float)
    macro_mat = df[macro_cols].values.astype(float)
    if macro_mat.ndim == 1:
        macro_mat = macro_mat.reshape(-1, 1)
    p = macro_mat.shape[1]

    macro_mean = np.mean(macro_mat, axis=0)
    macro_std = np.std(macro_mat, axis=0)
    macro_std = np.where(macro_std > 1e-12, macro_std, 1.0)
    macro_scaled = (macro_mat - macro_mean) / macro_std

    exog_linear, smoother = build_gam_spec(
        t,
        macro_scaled,
        trend_degree=trend_degree,
        fourier_k=fourier_k,
        df_spline=df_spline,
        degree_spline=degree_spline,
    )

    alpha_list = [alpha] * p if isinstance(alpha, (int, float)) else list(alpha)
    gam = GLMGam(
        endog=y,
        exog=exog_linear,
        smoother=smoother,
        alpha=alpha_list,
        family=sm.families.Gaussian(),
    )
    try:
        res = gam.fit()
    except Exception as exc:
        if "PerfectSeparationError" in type(exc).__name__ or "separation" in str(exc).lower():
            # Perfect mathematical fit detected (zero residual); add micro-perturbation to prevent false-positive separation error
            rng = np.random.RandomState(12345)
            y_pert = y + rng.normal(0, 1e-4, len(y))
            gam_pert = GLMGam(
                endog=y_pert,
                exog=exog_linear,
                smoother=smoother,
                alpha=alpha_list,
                family=sm.families.Gaussian(),
            )
            res = gam_pert.fit()
        else:
            raise

    # Attach model metadata for prediction and diagnostics
    res.target_col = target_col
    res.trend_col = trend_col
    res.macro_cols = list(macro_cols)
    res.trend_degree = trend_degree
    res.fourier_k = fourier_k
    res.df_spline = df_spline
    res.degree_spline = degree_spline
    res.t_mean = float(np.mean(t))
    std_t = float(np.std(t))
    res.t_std = std_t if std_t > 1e-12 else 1.0
    res.macro_mat = macro_mat
    res.macro_mean = macro_mean
    res.macro_std = macro_std
    res.smoother = smoother

    return res


def predict_gam(model: object, df_future: pd.DataFrame) -> np.ndarray:
    """
    Computes out-of-sample forecast predictions from a fitted GLMGam model.
    Guarantees non-negative, finite positive prediction output.
    
    Parameters
    ----------
    model : GLMGamResults
        Fitted model returned by fit_gam_model.
    df_future : pd.DataFrame
        Future or test feature matrix.
        
    Returns
    -------
    np.ndarray
        Array of predicted values.
    """
    n_test = len(df_future)
    trend_col = getattr(model, "trend_col", "t")

    if trend_col in df_future.columns:
        t_future = df_future[trend_col].values.astype(float)
    elif "t" in df_future.columns:
        t_future = df_future["t"].values.astype(float)
    else:
        t_future = np.arange(n_test, dtype=float) + 1.0

    t_mean = getattr(model, "t_mean", float(np.mean(t_future)))
    t_std = getattr(model, "t_std", float(np.std(t_future)) if np.std(t_future) > 1e-12 else 1.0)
    trend_deg = getattr(model, "trend_degree", 1)
    fourier_k = getattr(model, "fourier_k", 2)

    t_std_arr = (t_future - t_mean) / t_std
    if trend_deg >= 1:
        trend_mat = np.column_stack([t_std_arr**d for d in range(1, trend_deg + 1)])
    else:
        trend_mat = np.ones((n_test, 1), dtype=float)

    harmonic_mat = build_harmonic_basis(t_future, period=12, K=fourier_k)
    exog_future = np.column_stack([np.ones(n_test), trend_mat, harmonic_mat])

    macro_cols = getattr(model, "macro_cols", None)
    if macro_cols is None:
        exclude = {trend_col.lower(), "t", "price", "price_inr", "date"}
        macro_cols = [c for c in df_future.columns if c.lower() not in exclude]

    macro_future = df_future[macro_cols].values.astype(float)
    if macro_future.ndim == 1:
        macro_future = macro_future.reshape(-1, 1)

    macro_mean = getattr(model, "macro_mean", np.mean(macro_future, axis=0))
    macro_std = getattr(model, "macro_std", np.ones(macro_future.shape[1]))
    macro_scaled = (macro_future - macro_mean) / macro_std

    # Predict using statsmodels GLMGam
    preds = model.predict(exog=exog_future, exog_smooth=macro_scaled)
    preds_arr = np.asarray(preds, dtype=float).flatten()

    # Economic constraint: retail CNG prices are strictly positive
    preds_arr = np.maximum(preds_arr, 0.01)
    return preds_arr
