"""Data freshness validator.

Ensures data from MCP is recent enough for analysis.
Stale data can lead to incorrect trading decisions.
"""

from datetime import datetime, timedelta
from typing import Any


class DataFreshnessError(Exception):
    """Raised when data is too old for analysis."""

    pass


class DataFreshnessValidator:
    """Validates that market data is fresh enough for analysis."""

    def __init__(self, max_age_minutes: int = 5):
        """
        Initialize the validator.

        Args:
            max_age_minutes: Maximum age of data in minutes (default: 5)
        """
        self.max_age_minutes = max_age_minutes

    def validate(self, chart_data: dict[str, Any]) -> bool:
        """
        Validate that chart data is fresh.

        Args:
            chart_data: Chart data from MCP get_active_chart tool

        Returns:
            True if data is fresh

        Raises:
            DataFreshnessError: If data is too old
        """
        fetched_at = chart_data.get("fetched_at")

        if not fetched_at:
            raise DataFreshnessError("Chart data missing 'fetched_at' timestamp")

        try:
            fetch_time = datetime.fromisoformat(fetched_at)
        except ValueError:
            raise DataFreshnessError(f"Invalid timestamp format: {fetched_at}")

        age = datetime.now() - fetch_time

        if age > timedelta(minutes=self.max_age_minutes):
            raise DataFreshnessError(
                f"Data is {age.total_seconds() / 60:.1f} minutes old, "
                f"max allowed is {self.max_age_minutes} minutes"
            )

        return True

    def get_age_seconds(self, chart_data: dict[str, Any]) -> float:
        """
        Get the age of chart data in seconds.

        Args:
            chart_data: Chart data from MCP

        Returns:
            Age in seconds
        """
        fetched_at = chart_data.get("fetched_at")

        if not fetched_at:
            return float("inf")

        try:
            fetch_time = datetime.fromisoformat(fetched_at)
            age = datetime.now() - fetch_time
            return age.total_seconds()
        except ValueError:
            return float("inf")

    def is_fresh(self, chart_data: dict[str, Any]) -> bool:
        """
        Check if data is fresh without raising exception.

        Args:
            chart_data: Chart data from MCP

        Returns:
            True if data is fresh, False otherwise
        """
        try:
            return self.validate(chart_data)
        except DataFreshnessError:
            return False
