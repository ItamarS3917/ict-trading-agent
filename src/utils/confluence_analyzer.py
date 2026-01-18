"""Confluence analyzer for ICT patterns.

Identifies and scores multi-factor confluence zones where
ICT patterns align with TradingView indicators and drawings.
"""

from typing import Any


class ConfluenceAnalyzer:
    """
    Analyzes confluence between ICT patterns and other technical factors.

    Confluence scoring helps prioritize high-probability setups.
    """

    def __init__(self, min_confluence_score: int = 2):
        """
        Initialize the analyzer.

        Args:
            min_confluence_score: Minimum score to consider a setup valid
        """
        self.min_confluence_score = min_confluence_score

    def analyze(
        self,
        patterns: list[dict[str, Any]],
        indicators: dict[str, Any],
        drawings: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Analyze confluence for detected patterns.

        Args:
            patterns: List of ICT patterns (FVGs, Order Blocks, etc.)
            indicators: Indicator values from TradingView
            drawings: User drawings from TradingView

        Returns:
            List of patterns with confluence scores and factors
        """
        results = []

        for pattern in patterns:
            confluence_factors = []
            score = 0

            # Check indicator confluence
            indicator_confluence = self._check_indicator_confluence(
                pattern, indicators
            )
            confluence_factors.extend(indicator_confluence)
            score += len(indicator_confluence)

            # Check drawing confluence
            drawing_confluence = self._check_drawing_confluence(pattern, drawings)
            confluence_factors.extend(drawing_confluence)
            score += len(drawing_confluence)

            # Add pattern strength as a factor
            if pattern.get("strength", 0) >= 7:
                confluence_factors.append("Strong pattern (7+/10)")
                score += 1

            # Create enriched pattern
            enriched = {
                **pattern,
                "confluence_score": score,
                "confluence_factors": confluence_factors,
                "meets_minimum": score >= self.min_confluence_score,
            }

            results.append(enriched)

        # Sort by confluence score (highest first)
        results.sort(key=lambda x: x["confluence_score"], reverse=True)

        return results

    def _check_indicator_confluence(
        self, pattern: dict[str, Any], indicators: dict[str, Any]
    ) -> list[str]:
        """Check if indicators support the pattern direction."""
        factors = []
        direction = pattern.get("direction", "").upper()

        # RSI
        rsi = indicators.get("RSI_14", {})
        if isinstance(rsi, dict):
            rsi_value = rsi.get("value", 50)
        else:
            rsi_value = rsi if isinstance(rsi, (int, float)) else 50

        if direction == "BULLISH" and rsi_value < 30:
            factors.append(f"RSI oversold ({rsi_value:.1f})")
        elif direction == "BEARISH" and rsi_value > 70:
            factors.append(f"RSI overbought ({rsi_value:.1f})")

        # MACD
        macd = indicators.get("MACD", {})
        if isinstance(macd, dict):
            macd_value = macd.get("value", 0)
            macd_signal = macd.get("signal", 0)

            if direction == "BULLISH" and macd_value > macd_signal:
                factors.append("MACD bullish crossover")
            elif direction == "BEARISH" and macd_value < macd_signal:
                factors.append("MACD bearish crossover")

        # EMA trend
        ema_20 = indicators.get("EMA_20", {})
        ema_50 = indicators.get("EMA_50", {})

        if isinstance(ema_20, dict):
            ema_20 = ema_20.get("value", 0)
        if isinstance(ema_50, dict):
            ema_50 = ema_50.get("value", 0)

        if ema_20 and ema_50:
            if direction == "BULLISH" and ema_20 > ema_50:
                factors.append("EMA bullish alignment (20 > 50)")
            elif direction == "BEARISH" and ema_20 < ema_50:
                factors.append("EMA bearish alignment (20 < 50)")

        return factors

    def _check_drawing_confluence(
        self, pattern: dict[str, Any], drawings: list[dict[str, Any]]
    ) -> list[str]:
        """Check if user drawings align with the pattern."""
        factors = []

        # Get pattern price levels
        pattern_high = pattern.get("gap_high", pattern.get("high", 0))
        pattern_low = pattern.get("gap_low", pattern.get("low", 0))

        if not pattern_high or not pattern_low:
            return factors

        # Check each drawing
        for drawing in drawings:
            drawing_type = drawing.get("type", "")
            drawing_price = drawing.get("price", 0)

            # Horizontal lines (support/resistance)
            if drawing_type == "horizontal_line" and drawing_price:
                # Check if drawing aligns with pattern (within 0.5%)
                tolerance = abs(pattern_high - pattern_low) * 0.5

                if abs(drawing_price - pattern_high) <= tolerance:
                    label = drawing.get("label", "S/R line")
                    factors.append(f"Aligns with {label} at {drawing_price:.2f}")
                elif abs(drawing_price - pattern_low) <= tolerance:
                    label = drawing.get("label", "S/R line")
                    factors.append(f"Aligns with {label} at {drawing_price:.2f}")

            # Fibonacci levels
            elif drawing_type == "fibonacci":
                levels = drawing.get("levels", [])
                for level in levels:
                    level_price = level.get("price", 0)
                    level_name = level.get("name", "Fib")

                    tolerance = abs(pattern_high - pattern_low) * 0.3
                    if abs(level_price - pattern_high) <= tolerance:
                        factors.append(f"Aligns with {level_name} level")
                        break

        return factors

    def get_best_setups(
        self,
        patterns: list[dict[str, Any]],
        indicators: dict[str, Any],
        drawings: list[dict[str, Any]],
        max_setups: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Get the best trading setups based on confluence.

        Args:
            patterns: List of ICT patterns
            indicators: Indicator values
            drawings: User drawings
            max_setups: Maximum number of setups to return

        Returns:
            Top setups sorted by confluence score
        """
        analyzed = self.analyze(patterns, indicators, drawings)
        valid_setups = [p for p in analyzed if p["meets_minimum"]]
        return valid_setups[:max_setups]
