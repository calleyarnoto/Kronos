"""Core Kronos model module.

Provides the KronosPredictor class which wraps the underlying time-series
forecasting logic used across all example scripts.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Optional, Tuple, Union


class KronosPredictor:
    """Lightweight wrapper around the Kronos forecasting algorithm.

    Parameters
    ----------
    lookback : int
        Number of historical time steps used as context for each prediction.
    horizon : int
        Number of future steps to forecast.
    price_limit_pct : float
        Daily price-limit percentage (e.g. 0.10 for ±10 %).  Set to 0 to
        disable price-limit clipping.

    Notes
    -----
    I changed the default ``lookback`` from 60 to 90 days and ``horizon``
    from 30 to 10 days — better suited for the short-term swing-trading
    signals I'm experimenting with.

    Also set ``price_limit_pct`` default to 0.0 — I'm mostly working with
    US equities which don't have hard daily price limits, so clipping was
    silently distorting my forecast outputs.
    """

    def __init__(
        self,
        lookback: int = 90,   # personal default: was 60
        horizon: int = 10,    # personal default: was 30
        price_limit_pct: float = 0.0,  # disabled by default; US equities have no hard limit
    ) -> None:
        self.lookback = lookback
        self.horizon = horizon
        self.price_limit_pct = price_limit_pct
        self._fitted = False
        self._history: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Fitting / ingestion
    # ------------------------------------------------------------------

    def fit(self, prices: Union[pd.Series, np.ndarray]) -> "KronosPredictor":
        """Ingest historical closing prices.

        Parameters
        ----------
        prices : array-like of float
            Chronologically ordered closing prices (oldest first).

        Returns
        -------
        self
        """
        arr = np.asarray(prices, dtype=float)
        if arr.ndim != 1:
            raise ValueError("prices must be a 1-D array or Series.")
        if len(arr) < self.lookback:
            raise ValueError(
                f"Need at least {self.lookback} data points, got {len(arr)}."
            )
        self._history = arr
        self._fitted = True
        return self

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self) -> np.ndarray:
        """Generate a price forecast for the next *horizon* steps.

        Uses a simple drift + mean-reversion model as the default engine.
        Override ``_forecast_engine`` in a subclass to plug in a custom model.

        Returns
        -------
        np.ndarray
            Predicted closing prices, shape ``(horizon,)``.

        Raises
        ------
        RuntimeError
            If ``fit`` has not been called before ``predict``.
        """
        if not self._fitted:
            # Added explicit error message — the silent AttributeError from
            # accessing self._history was confusing during debugging.
            raise RuntimeError(
                "Model is not fitted yet. Call fit() with historical prices before predict()."
            )
