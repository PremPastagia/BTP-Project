"""
Baseline Linear Econometric Model: Autoregressive Integrated Moving Average (ARIMA).
Implements Requirement R3:
- Automated grid search over (p, d, q) order space minimizing Akaike Information Criterion (AIC).
- Enforces unit-root differencing (d >= 1) on non-stationary random-walk series.
- Out-of-sample recursive forecasting for comparative benchmark.
"""

from typing import Optional, Tuple
import warnings
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller


def select_arima_order(
    series: np.ndarray,
    max_p: int = 3,
    max_d: int = 2,
    max_q: int = 3,
) -> Tuple[int, int, int]:
    """
    Automated grid-search order selection for ARIMA(p, d, q) optimizing AIC.
    Enforces differencing d >= 1 if series contains a unit root (ADF p > 0.05).
    
    Parameters
    ----------
    series : np.ndarray
        Historical 1D time series.
    max_p : int, default=3
    max_d : int, default=2
    max_q : int, default=3
    
    Returns
    -------
    tuple[int, int, int]
        Optimal (p, d, q) order tuple.
    """
    series_arr = np.asarray(series, dtype=float).flatten()
    # Check for unit roots via Augmented Dickey-Fuller test
    try:
        adf_stat, adf_p, *rest = adfuller(series_arr, maxlag=min(12, len(series_arr) // 4))
    except Exception:
        adf_p = 0.5

    # Enforce differencing if series is non-stationary (unit root)
    min_d = 1 if adf_p > 0.05 else 0

    best_aic = np.inf
    best_order = (1, max(min_d, 1), 1)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        for d in range(min_d, max_d + 1):
            for p in range(max_p + 1):
                for q in range(max_q + 1):
                    if p == 0 and d == 0 and q == 0:
                        continue
                    try:
                        m = ARIMA(series_arr, order=(p, d, q)).fit()
                        if m.aic < best_aic:
                            best_aic = m.aic
                            best_order = (p, d, q)
                    except Exception:
                        continue

    return best_order


def fit_arima(
    series: np.ndarray,
    order: Optional[Tuple[int, int, int]] = None,
) -> object:
    """
    Estimates ARIMA(p, d, q) baseline model on historical series.
    
    Parameters
    ----------
    series : np.ndarray
        Target time series.
    order : tuple[int, int, int], optional
        (p, d, q) specification. If None, automated grid search selects optimal order.
        
    Returns
    -------
    ARIMAResults
        Fitted statsmodels ARIMA results object.
    """
    series_arr = np.asarray(series, dtype=float).flatten()
    if order is None:
        order = select_arima_order(series_arr)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        model = ARIMA(series_arr, order=order).fit()
    return model


def forecast_arima(model: object, steps: int = 1) -> np.ndarray:
    """
    Generates out-of-sample forecast vector of specified length.
    
    Parameters
    ----------
    model : ARIMAResults
        Fitted ARIMA model.
    steps : int, default=1
        Forecast horizon steps.
        
    Returns
    -------
    np.ndarray
        Forecast array of length steps.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        preds = model.forecast(steps=steps)
    return np.asarray(preds, dtype=float)
