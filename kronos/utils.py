"""Utility functions for Kronos time series prediction."""

import numpy as np
import pandas as pd
from typing import Tuple, Optional


def normalize_series(series: np.ndarray) -> Tuple[np.ndarray, float, float]:
    """Normalize a time series to [0, 1] range.

    Args:
        series: Input time series array.

    Returns:
        Tuple of (normalized_series, min_value, max_value).
    """
    min_val = np.min(series)
    max_val = np.max(series)
    if max_val - min_val == 0:
        return np.zeros_like(series, dtype=float), min_val, max_val
    normalized = (series - min_val) / (max_val - min_val)
    return normalized, min_val, max_val


def denormalize_series(normalized: np.ndarray, min_val: float, max_val: float) -> np.ndarray:
    """Reverse normalization of a time series.

    Args:
        normalized: Normalized time series array.
        min_val: Original minimum value.
        max_val: Original maximum value.

    Returns:
        Denormalized series.
    """
    return normalized * (max_val - min_val) + min_val


def prepare_dataframe(df: pd.DataFrame, date_col: str = 'date', price_col: str = 'close') -> pd.DataFrame:
    """Prepare a stock dataframe for use with KronosPredictor.

    Args:
        df: Raw dataframe with date and price columns.
        date_col: Name of the date column.
        price_col: Name of the price/close column.

    Returns:
        Cleaned and sorted dataframe with datetime index.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)
    df = df.dropna(subset=[price_col])
    df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
    df = df.dropna(subset=[price_col])
    return df


def compute_returns(prices: np.ndarray, log: bool = False) -> np.ndarray:
    """Compute returns from a price series.

    Args:
        prices: Array of prices.
        log: If True, compute log returns; otherwise simple returns.

    Returns:
        Array of returns (length = len(prices) - 1).
    """
    if log:
        return np.diff(np.log(prices))
    return np.diff(prices) / prices[:-1]


def split_train_test(
    series: np.ndarray,
    test_ratio: float = 0.2
) -> Tuple[np.ndarray, np.ndarray]:
    """Split a time series into training and test sets.

    Args:
        series: Full time series array.
        test_ratio: Fraction of data to use as test set.

    Returns:
        Tuple of (train_series, test_series).
    """
    split_idx = int(len(series) * (1 - test_ratio))
    return series[:split_idx], series[split_idx:]


def mape(actual: np.ndarray, predicted: np.ndarray, epsilon: float = 1e-8) -> float:
    """Mean Absolute Percentage Error.

    Args:
        actual: Ground truth values.
        predicted: Predicted values.
        epsilon: Small value to avoid division by zero.

    Returns:
        MAPE as a percentage.
    """
    return float(np.mean(np.abs((actual - predicted) / (np.abs(actual) + epsilon))) * 100)


def rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Root Mean Squared Error.

    Args:
        actual: Ground truth values.
        predicted: Predicted values.

    Returns:
        RMSE value.
    """
    return float(np.sqrt(np.mean((actual - predicted) ** 2)))
