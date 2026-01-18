"""
analyze-ict-patterns skill for Claude.

Detects Fair Value Gaps, Order Blocks, and Liquidity Pools
from TradingView chart data using the MCP server.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pattern_detector import PatternDetector
from utils.mcp_client import MCPClient
from utils.confluence_analyzer import ConfluenceAnalyzer
from utils.data_freshness import DataFreshnessValidator, DataFreshnessError
from utils.agent_logger import get_agent_logger


class AnalyzeICTPatterns:
    """
    Claude skill for analyzing ICT patterns in TradingView charts.

    This skill:
    1. Fetches chart data from TradingView MCP server
    2. Detects FVGs, Order Blocks, and Liquidity Pools
    3. Analyzes confluence with TradingView indicators/drawings
    4. Returns structured pattern data with recommendations
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize the skill.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Initialize components
        self.pattern_detector = PatternDetector(
            self.config.get(
                "patterns",
                {"fvg_min_size": 0.001, "orderblock_strength": 3, "liquidity_threshold": 0.05},
            )
        )
        self.confluence_analyzer = ConfluenceAnalyzer(
            min_confluence_score=self.config.get("min_confluence_score", 2)
        )
        self.freshness_validator = DataFreshnessValidator(
            max_age_minutes=self.config.get("max_data_age_minutes", 5)
        )
        self.logger = get_agent_logger("claude")

    async def execute(
        self,
        chart_data_json: str,
        indicators_json: str | None = None,
        drawings_json: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute the skill to analyze ICT patterns.

        Args:
            chart_data_json: JSON from MCP get_active_chart tool
            indicators_json: Optional JSON from MCP get_indicators tool
            drawings_json: Optional JSON from MCP get_drawings tool

        Returns:
            Analysis results with patterns and recommendations
        """
        start_time = datetime.now()
        self.logger.log_request("analyze_ict_patterns", {"has_indicators": bool(indicators_json)})

        try:
            # Parse chart data
            chart_data = json.loads(chart_data_json)

            # Validate data freshness
            try:
                self.freshness_validator.validate(chart_data)
            except DataFreshnessError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "recommendation": "Please refresh the chart and try again",
                }

            # Convert to DataFrame
            df = MCPClient.parse_chart_data(chart_data_json)

            if df.empty:
                return {
                    "success": False,
                    "error": "No chart data available",
                    "recommendation": "Ensure you have a chart open in TradingView",
                }

            # Get metadata
            metadata = MCPClient.get_chart_metadata(chart_data_json)

            # Detect patterns
            fvgs = self.pattern_detector.detect_fair_value_gaps(df)
            order_blocks = self.pattern_detector.detect_order_blocks(df)
            liquidity_pools = self.pattern_detector.detect_liquidity_pools(df)

            all_patterns = fvgs + order_blocks + liquidity_pools

            # Analyze confluence if indicators/drawings available
            indicators = {}
            drawings = []

            if indicators_json:
                indicators = MCPClient.parse_indicators(indicators_json)
            if drawings_json:
                drawings = MCPClient.parse_drawings(drawings_json)

            analyzed_patterns = self.confluence_analyzer.analyze(
                all_patterns, indicators, drawings
            )

            # Separate by type
            result = {
                "success": True,
                "symbol": metadata["symbol"],
                "timeframe": metadata["timeframe"],
                "analyzed_at": datetime.now().isoformat(),
                "data_age_seconds": self.freshness_validator.get_age_seconds(chart_data),
                "patterns": {
                    "fair_value_gaps": [p for p in analyzed_patterns if p.get("type") == "Fair Value Gap"],
                    "order_blocks": [p for p in analyzed_patterns if p.get("type") == "Order Block"],
                    "liquidity_pools": [p for p in analyzed_patterns if p.get("type") == "Liquidity Pool"],
                },
                "summary": self._generate_summary(analyzed_patterns, metadata),
                "best_setups": self.confluence_analyzer.get_best_setups(
                    all_patterns, indicators, drawings, max_setups=3
                ),
            }

            # Log results
            self.logger.log_analysis(
                "analyze_ict_patterns",
                {
                    "fvg_count": len(fvgs),
                    "ob_count": len(order_blocks),
                    "lp_count": len(liquidity_pools),
                    "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                },
            )

            return result

        except Exception as e:
            self.logger.log_error("analyze_ict_patterns", e)
            return {
                "success": False,
                "error": str(e),
                "recommendation": "An error occurred during analysis. Please check your data and try again.",
            }

    def _generate_summary(
        self, patterns: list[dict[str, Any]], metadata: dict[str, Any]
    ) -> str:
        """Generate a natural language summary of the analysis."""
        fvg_count = len([p for p in patterns if p.get("type") == "Fair Value Gap"])
        ob_count = len([p for p in patterns if p.get("type") == "Order Block"])
        lp_count = len([p for p in patterns if p.get("type") == "Liquidity Pool"])

        bullish = len([p for p in patterns if p.get("direction") == "BULLISH"])
        bearish = len([p for p in patterns if p.get("direction") == "BEARISH"])

        high_confluence = len([p for p in patterns if p.get("confluence_score", 0) >= 3])

        summary = f"Analysis of {metadata['symbol']} ({metadata['timeframe']}): "
        summary += f"Found {fvg_count} FVGs, {ob_count} Order Blocks, {lp_count} Liquidity Pools. "

        if bullish > bearish:
            summary += f"Bias: BULLISH ({bullish} bullish vs {bearish} bearish patterns). "
        elif bearish > bullish:
            summary += f"Bias: BEARISH ({bearish} bearish vs {bullish} bullish patterns). "
        else:
            summary += "Bias: NEUTRAL (equal bullish and bearish patterns). "

        if high_confluence > 0:
            summary += f"{high_confluence} high-confluence setups identified."

        return summary


# Entry point for skill execution
skill = AnalyzeICTPatterns()
