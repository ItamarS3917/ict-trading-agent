"""
ICT Trading Agent - Core Implementation

This module contains the main ICT Trading Agent class that implements
Inner Circle Trader concepts for algorithmic trading analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from data_handler import DataHandler
from pattern_detector import PatternDetector


class ICTTradingAgent:
    """
    Main ICT Trading Agent implementing Inner Circle Trader concepts
    for automated trading analysis and signal generation.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the ICT Trading Agent.
        
        Args:
            config: Configuration dictionary with trading parameters
        """
        self.config = config or self._default_config()
        self.data_handler = DataHandler()
        self.pattern_detector = PatternDetector(self.config)
        
    def _default_config(self) -> Dict:
        """Default configuration for the trading agent."""
        return {
            "lookback_period": 100,
            "fvg_min_size": 0.001,  # Minimum FVG size as percentage
            "orderblock_strength": 3,
            "liquidity_threshold": 0.05,
            "timeframe": "1h",
            "risk_per_trade": 0.02
        }
    
    def analyze_market_structure(self, symbol: str) -> Dict:
        """
        Analyze market structure for Break of Structure (BOS) and 
        Change of Character (CHoCH) patterns.
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            Dictionary containing market structure analysis
        """
        # Get price data
        df = self.data_handler.get_price_data(
            symbol, 
            period=f"{self.config['lookback_period']}d"
        )
        
        if df.empty:
            return {"error": "No data available"}
        
        # Identify swing highs and lows
        swing_points = self._identify_swing_points(df)
        
        # Determine trend direction
        trend = self._determine_trend(df, swing_points)
        
        # Check for structure breaks
        bos_points = self._detect_break_of_structure(df, swing_points)
        choch_points = self._detect_change_of_character(df, swing_points)
        
        return {
            "symbol": symbol,
            "trend_direction": trend,
            "swing_points": swing_points,
            "break_of_structure": bos_points,
            "change_of_character": choch_points,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def detect_fair_value_gaps(self, symbol: str) -> List[Dict]:
        """
        Detect Fair Value Gaps (FVGs) in the price data.
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            List of detected FVG patterns
        """
        df = self.data_handler.get_price_data(
            symbol, 
            period=f"{self.config['lookback_period']}d"
        )
        
        return self.pattern_detector.detect_fair_value_gaps(df)
    
    def detect_order_blocks(self, symbol: str) -> List[Dict]:
        """
        Detect Order Block patterns in the price data.
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            List of detected Order Block patterns
        """
        df = self.data_handler.get_price_data(
            symbol, 
            period=f"{self.config['lookback_period']}d"
        )
        
        return self.pattern_detector.detect_order_blocks(df)
    
    def detect_liquidity_pools(self, symbol: str) -> List[Dict]:
        """
        Detect liquidity pools and accumulation zones.
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            List of detected liquidity pools
        """
        df = self.data_handler.get_price_data(
            symbol, 
            period=f"{self.config['lookback_period']}d"
        )
        
        return self.pattern_detector.detect_liquidity_pools(df)
    
    def generate_signals(self, symbol: str) -> List[Dict]:
        """
        Generate trading signals based on ICT concepts.
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            List of trading signals
        """
        signals = []
        
        # Get various pattern detections
        fvgs = self.detect_fair_value_gaps(symbol)
        order_blocks = self.detect_order_blocks(symbol)
        market_structure = self.analyze_market_structure(symbol)
        
        # Generate signals based on pattern confluence
        for fvg in fvgs:
            if self._is_valid_fvg_signal(fvg, market_structure):
                signal = {
                    "type": "FVG_ENTRY",
                    "direction": fvg["direction"],
                    "price": fvg["entry_price"],
                    "stop_loss": fvg["stop_loss"],
                    "take_profit": fvg["take_profit"],
                    "strength": self._calculate_signal_strength(fvg, market_structure),
                    "timestamp": datetime.now().isoformat(),
                    "pattern": "Fair Value Gap"
                }
                signals.append(signal)
        
        for ob in order_blocks:
            if self._is_valid_orderblock_signal(ob, market_structure):
                signal = {
                    "type": "ORDERBLOCK_ENTRY",
                    "direction": ob["direction"], 
                    "price": ob["entry_price"],
                    "stop_loss": ob["stop_loss"],
                    "take_profit": ob["take_profit"],
                    "strength": self._calculate_signal_strength(ob, market_structure),
                    "timestamp": datetime.now().isoformat(),
                    "pattern": "Order Block"
                }
                signals.append(signal)
        
        return sorted(signals, key=lambda x: x["strength"], reverse=True)
    
    def _identify_swing_points(self, df: pd.DataFrame, window: int = 5) -> Dict:
        """Identify swing highs and lows in price data."""
        highs = []
        lows = []
        
        for i in range(window, len(df) - window):
            # Check for swing high
            if all(df.iloc[i]['High'] > df.iloc[j]['High'] for j in range(i-window, i+window+1) if j != i):
                highs.append({
                    "index": i,
                    "price": df.iloc[i]['High'],
                    "timestamp": df.index[i]
                })
            
            # Check for swing low
            if all(df.iloc[i]['Low'] < df.iloc[j]['Low'] for j in range(i-window, i+window+1) if j != i):
                lows.append({
                    "index": i,
                    "price": df.iloc[i]['Low'],
                    "timestamp": df.index[i]
                })
        
        return {"highs": highs, "lows": lows}
    
    def _determine_trend(self, df: pd.DataFrame, swing_points: Dict) -> str:
        """Determine overall trend direction based on swing points."""
        highs = swing_points["highs"][-5:]  # Last 5 highs
        lows = swing_points["lows"][-5:]    # Last 5 lows
        
        if len(highs) < 2 or len(lows) < 2:
            return "SIDEWAYS"
        
        # Check for higher highs and higher lows (uptrend)
        higher_highs = all(highs[i]["price"] > highs[i-1]["price"] for i in range(1, len(highs)))
        higher_lows = all(lows[i]["price"] > lows[i-1]["price"] for i in range(1, len(lows)))
        
        if higher_highs and higher_lows:
            return "UPTREND"
        
        # Check for lower highs and lower lows (downtrend)
        lower_highs = all(highs[i]["price"] < highs[i-1]["price"] for i in range(1, len(highs)))
        lower_lows = all(lows[i]["price"] < lows[i-1]["price"] for i in range(1, len(lows)))
        
        if lower_highs and lower_lows:
            return "DOWNTREND"
        
        return "SIDEWAYS"
    
    def _detect_break_of_structure(self, df: pd.DataFrame, swing_points: Dict) -> List[Dict]:
        """Detect Break of Structure (BOS) points."""
        bos_points = []
        highs = swing_points["highs"]
        lows = swing_points["lows"]
        
        # Implementation of BOS detection logic
        # This is a simplified version - real implementation would be more complex
        
        return bos_points
    
    def _detect_change_of_character(self, df: pd.DataFrame, swing_points: Dict) -> List[Dict]:
        """Detect Change of Character (CHoCH) points."""
        choch_points = []
        
        # Implementation of CHoCH detection logic
        # This is a simplified version - real implementation would be more complex
        
        return choch_points
    
    def _is_valid_fvg_signal(self, fvg: Dict, market_structure: Dict) -> bool:
        """Validate if FVG signal aligns with market structure."""
        trend = market_structure.get("trend_direction", "SIDEWAYS")
        
        if trend == "UPTREND" and fvg["direction"] == "BULLISH":
            return True
        elif trend == "DOWNTREND" and fvg["direction"] == "BEARISH":
            return True
        
        return False
    
    def _is_valid_orderblock_signal(self, orderblock: Dict, market_structure: Dict) -> bool:
        """Validate if Order Block signal aligns with market structure."""
        trend = market_structure.get("trend_direction", "SIDEWAYS")
        
        if trend == "UPTREND" and orderblock["direction"] == "BULLISH":
            return True
        elif trend == "DOWNTREND" and orderblock["direction"] == "BEARISH":
            return True
        
        return False
    
    def _calculate_signal_strength(self, pattern: Dict, market_structure: Dict) -> float:
        """Calculate signal strength based on pattern quality and confluence."""
        base_strength = pattern.get("strength", 0.5)
        
        # Add bonus for trend alignment
        trend = market_structure.get("trend_direction", "SIDEWAYS")
        if trend != "SIDEWAYS" and pattern["direction"].upper() in trend:
            base_strength += 0.2
        
        # Add bonus for pattern quality metrics
        if pattern.get("volume_confirmation", False):
            base_strength += 0.1
        
        return min(base_strength, 1.0)  # Cap at 1.0