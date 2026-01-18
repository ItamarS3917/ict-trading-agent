"""MCP client helper for Claude skills.

Provides utilities for parsing MCP tool responses into
pandas DataFrames and other usable formats.
"""

import json
from typing import Any

import pandas as pd


class MCPClient:
    """Helper for calling MCP tools from Claude skills."""

    @staticmethod
    def parse_chart_data(chart_json: str) -> pd.DataFrame:
        """
        Parse chart data from MCP response to DataFrame.

        Args:
            chart_json: JSON string from get_active_chart tool

        Returns:
            DataFrame with OHLCV data
        """
        data = json.loads(chart_json)

        if not data.get("bars"):
            return pd.DataFrame()

        # Convert bars to DataFrame
        df = pd.DataFrame(data["bars"])

        # Set timestamp as index
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.set_index("timestamp")

        # Rename columns to match expected format
        df = df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
        )

        return df

    @staticmethod
    def parse_indicators(indicators_json: str) -> dict[str, Any]:
        """
        Parse indicators from MCP response.

        Args:
            indicators_json: JSON string from get_indicators tool

        Returns:
            Dictionary of indicator values
        """
        data = json.loads(indicators_json)
        return data.get("indicators", {})

    @staticmethod
    def parse_drawings(drawings_json: str) -> list[dict[str, Any]]:
        """
        Parse drawings from MCP response.

        Args:
            drawings_json: JSON string from get_drawings tool

        Returns:
            List of drawing objects
        """
        return json.loads(drawings_json)

    @staticmethod
    def parse_watchlist(watchlist_json: str) -> list[str]:
        """
        Parse watchlist from MCP response.

        Args:
            watchlist_json: JSON string from get_watchlist tool

        Returns:
            List of symbols
        """
        data = json.loads(watchlist_json)
        return [item["symbol"] for item in data if "symbol" in item]

    @staticmethod
    def get_chart_metadata(chart_json: str) -> dict[str, Any]:
        """
        Extract metadata from chart response.

        Args:
            chart_json: JSON string from get_active_chart tool

        Returns:
            Dictionary with symbol, timeframe, fetched_at
        """
        data = json.loads(chart_json)
        return {
            "symbol": data.get("symbol"),
            "timeframe": data.get("timeframe"),
            "fetched_at": data.get("fetched_at"),
            "bar_count": len(data.get("bars", [])),
            "is_stub": data.get("is_stub", False),
        }
