"""
Data Utilities for ICT Trading Agent

Provides data cleaning, validation, and caching utilities.
Data fetching is handled by MCP server - this module processes the data.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd


class DataUtils:
    """
    Data cleaning, validation, and caching utilities.

    This replaces DataHandler - data now comes from MCP server instead of yfinance.
    """

    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize DataUtils.

        Args:
            cache_dir: Directory for data caching
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def clean_ohlcv_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate OHLCV data.

        Args:
            df: DataFrame with OHLCV columns

        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df

        # Ensure required columns exist
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Remove rows with NaN values
        df = df.dropna()

        # Ensure High >= Low
        if (df["High"] < df["Low"]).any():
            df = df[df["High"] >= df["Low"]]

        # Ensure High >= Open, Close and Low <= Open, Close
        df = df[
            (df["High"] >= df["Open"])
            & (df["High"] >= df["Close"])
            & (df["Low"] <= df["Open"])
            & (df["Low"] <= df["Close"])
        ]

        # Remove duplicate timestamps
        if isinstance(df.index, pd.DatetimeIndex):
            df = df[~df.index.duplicated(keep="first")]

        # Sort by index
        df = df.sort_index()

        return df

    def validate_ohlcv_data(self, df: pd.DataFrame) -> bool:
        """
        Validate OHLCV data structure and quality.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        if df.empty:
            return False

        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required_cols):
            return False

        # Check for negative prices or volumes
        if (df[["Open", "High", "Low", "Close", "Volume"]] < 0).any().any():
            return False

        # Check price relationships
        return not (df["High"] < df["Low"]).any()

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).

        Args:
            df: OHLC DataFrame
            period: ATR calculation period

        Returns:
            Series with ATR values
        """
        high = df["High"]
        low = df["Low"]
        close = df["Close"].shift(1)

        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)

        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return true_range.rolling(window=period).mean()

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).

        Args:
            prices: Price series
            period: RSI calculation period

        Returns:
            Series with RSI values
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add common technical indicators to the DataFrame.

        Args:
            df: OHLC DataFrame

        Returns:
            DataFrame with additional technical indicators
        """
        df = df.copy()

        # Moving averages
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()
        df["EMA_20"] = df["Close"].ewm(span=20).mean()

        # ATR
        df["ATR"] = self.calculate_atr(df)

        # RSI
        df["RSI"] = self.calculate_rsi(df["Close"])

        return df

    def cache_analysis(self, symbol: str, analysis_type: str, data: dict) -> None:
        """
        Cache analysis results.

        Args:
            symbol: Trading symbol
            analysis_type: Type of analysis (e.g., 'patterns', 'signals')
            data: Analysis data to cache
        """
        cache_file = (
            self.cache_dir / f"{symbol}_{analysis_type}_{datetime.now().strftime('%Y%m%d')}.json"
        )

        with open(cache_file, "w") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "analysis_type": analysis_type,
                    "data": data,
                },
                f,
                indent=2,
            )

    def load_cached_analysis(
        self, symbol: str, analysis_type: str, max_age_minutes: int = 60
    ) -> Optional[dict]:
        """
        Load cached analysis if not expired.

        Args:
            symbol: Trading symbol
            analysis_type: Type of analysis
            max_age_minutes: Maximum age of cache in minutes

        Returns:
            Cached data or None if not found/expired
        """
        cache_file = (
            self.cache_dir / f"{symbol}_{analysis_type}_{datetime.now().strftime('%Y%m%d')}.json"
        )

        if not cache_file.exists():
            return None

        with open(cache_file) as f:
            cached = json.load(f)

        # Check if expired
        cached_time = datetime.fromisoformat(cached["timestamp"])
        if datetime.now() - cached_time > timedelta(minutes=max_age_minutes):
            return None

        return cached["data"]


# Backwards compatibility - alias DataHandler to DataUtils
DataHandler = DataUtils
