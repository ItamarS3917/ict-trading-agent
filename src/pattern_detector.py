"""
Pattern Detector Module for ICT Trading Agent

Implements detection algorithms for ICT trading patterns including
Fair Value Gaps, Order Blocks, and Liquidity Pools.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class PatternDetector:
    """
    Detects ICT trading patterns in market data.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the PatternDetector.
        
        Args:
            config: Configuration dictionary with pattern parameters
        """
        self.config = config
        
    def detect_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect Fair Value Gaps (FVGs) in price data.
        
        A Fair Value Gap occurs when there's a gap between the high of one candle
        and the low of another candle that hasn't been filled.
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            List of detected FVG patterns
        """
        fvgs = []
        
        if len(df) < 3:
            return fvgs
        
        min_gap_size = self.config.get('fvg_min_size', 0.001)
        
        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i-1]
            current_candle = df.iloc[i]
            next_candle = df.iloc[i+1]
            
            # Bullish FVG: Gap between previous low and next high
            if (prev_candle['Low'] > next_candle['High'] and 
                current_candle['Close'] > current_candle['Open']):
                
                gap_size = (prev_candle['Low'] - next_candle['High']) / next_candle['High']
                
                if gap_size >= min_gap_size:
                    fvg = {
                        'type': 'Fair Value Gap',
                        'direction': 'BULLISH',
                        'timestamp': df.index[i],
                        'gap_high': prev_candle['Low'],
                        'gap_low': next_candle['High'],
                        'gap_size': gap_size,
                        'entry_price': next_candle['High'],
                        'stop_loss': prev_candle['Low'] - (prev_candle['Low'] * 0.001),
                        'take_profit': prev_candle['Low'] + (gap_size * prev_candle['Low'] * 2),
                        'strength': self._calculate_fvg_strength(df, i, gap_size),
                        'filled': False
                    }
                    fvgs.append(fvg)
            
            # Bearish FVG: Gap between previous high and next low
            elif (prev_candle['High'] < next_candle['Low'] and 
                  current_candle['Close'] < current_candle['Open']):
                
                gap_size = (next_candle['Low'] - prev_candle['High']) / prev_candle['High']
                
                if gap_size >= min_gap_size:
                    fvg = {
                        'type': 'Fair Value Gap',
                        'direction': 'BEARISH',
                        'timestamp': df.index[i],
                        'gap_high': next_candle['Low'],
                        'gap_low': prev_candle['High'],
                        'gap_size': gap_size,
                        'entry_price': prev_candle['High'],
                        'stop_loss': next_candle['Low'] + (next_candle['Low'] * 0.001),
                        'take_profit': next_candle['Low'] - (gap_size * next_candle['Low'] * 2),
                        'strength': self._calculate_fvg_strength(df, i, gap_size),
                        'filled': False
                    }
                    fvgs.append(fvg)
        
        return fvgs
    
    def detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect Order Block patterns in price data.
        
        Order Blocks are areas where large institutional orders were placed,
        often identified by strong moves away from consolidation zones.
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            List of detected Order Block patterns
        """
        order_blocks = []
        
        if len(df) < 20:
            return order_blocks
        
        min_strength = self.config.get('orderblock_strength', 3)
        
        for i in range(10, len(df) - 10):
            # Look for strong bullish moves
            if self._is_strong_bullish_move(df, i, min_strength):
                ob_low = min(df.iloc[i-5:i+1]['Low'])
                ob_high = max(df.iloc[i-5:i+1]['High'])
                
                order_block = {
                    'type': 'Order Block',
                    'direction': 'BULLISH',
                    'timestamp': df.index[i],
                    'block_high': ob_high,
                    'block_low': ob_low,
                    'entry_price': ob_low,
                    'stop_loss': ob_low - ((ob_high - ob_low) * 0.5),
                    'take_profit': ob_high + ((ob_high - ob_low) * 2),
                    'strength': self._calculate_orderblock_strength(df, i),
                    'tested': False
                }
                order_blocks.append(order_block)
            
            # Look for strong bearish moves
            elif self._is_strong_bearish_move(df, i, min_strength):
                ob_low = min(df.iloc[i-5:i+1]['Low'])
                ob_high = max(df.iloc[i-5:i+1]['High'])
                
                order_block = {
                    'type': 'Order Block',
                    'direction': 'BEARISH',
                    'timestamp': df.index[i],
                    'block_high': ob_high,
                    'block_low': ob_low,
                    'entry_price': ob_high,
                    'stop_loss': ob_high + ((ob_high - ob_low) * 0.5),
                    'take_profit': ob_low - ((ob_high - ob_low) * 2),
                    'strength': self._calculate_orderblock_strength(df, i),
                    'tested': False
                }
                order_blocks.append(order_block)
        
        return order_blocks
    
    def detect_liquidity_pools(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect liquidity pools - areas where stop losses might be accumulated.
        
        Args:
            df: OHLC DataFrame
        
        Returns:
            List of detected liquidity pools
        """
        liquidity_pools = []
        
        if len(df) < 50:
            return liquidity_pools
        
        # Look for equal highs and lows (potential liquidity zones)
        tolerance = self.config.get('liquidity_threshold', 0.05)
        
        # Detect equal highs
        highs = df['High'].values
        for i in range(20, len(highs) - 20):
            equal_highs = []
            base_high = highs[i]
            
            # Look for similar highs within tolerance
            for j in range(i-20, i+21):
                if j != i and abs(highs[j] - base_high) / base_high <= tolerance:
                    equal_highs.append(j)
            
            if len(equal_highs) >= 2:  # At least 3 equal highs (including base)
                liquidity_pool = {
                    'type': 'Liquidity Pool',
                    'level_type': 'RESISTANCE',
                    'price_level': base_high,
                    'timestamp': df.index[i],
                    'touches': len(equal_highs) + 1,
                    'strength': len(equal_highs) / 10.0,  # Normalize strength
                    'direction': 'BEARISH'  # Resistance level
                }
                liquidity_pools.append(liquidity_pool)
        
        # Detect equal lows
        lows = df['Low'].values
        for i in range(20, len(lows) - 20):
            equal_lows = []
            base_low = lows[i]
            
            # Look for similar lows within tolerance
            for j in range(i-20, i+21):
                if j != i and abs(lows[j] - base_low) / base_low <= tolerance:
                    equal_lows.append(j)
            
            if len(equal_lows) >= 2:  # At least 3 equal lows (including base)
                liquidity_pool = {
                    'type': 'Liquidity Pool',
                    'level_type': 'SUPPORT',
                    'price_level': base_low,
                    'timestamp': df.index[i],
                    'touches': len(equal_lows) + 1,
                    'strength': len(equal_lows) / 10.0,  # Normalize strength
                    'direction': 'BULLISH'  # Support level
                }
                liquidity_pools.append(liquidity_pool)
        
        return liquidity_pools
    
    def _calculate_fvg_strength(self, df: pd.DataFrame, index: int, gap_size: float) -> float:
        """Calculate the strength of a Fair Value Gap."""
        # Base strength from gap size
        strength = min(gap_size * 100, 0.5)  # Normalize gap size contribution
        
        # Add volume confirmation if available
        if 'Volume' in df.columns and index < len(df):
            avg_volume = df.iloc[index-10:index]['Volume'].mean()
            current_volume = df.iloc[index]['Volume']
            if current_volume > avg_volume * 1.5:
                strength += 0.2
        
        # Add momentum confirmation
        if index >= 3:
            recent_closes = df.iloc[index-3:index+1]['Close']
            if len(recent_closes) >= 3:
                momentum = (recent_closes.iloc[-1] - recent_closes.iloc[0]) / recent_closes.iloc[0]
                strength += abs(momentum) * 5  # Scale momentum
        
        return min(strength, 1.0)  # Cap at 1.0
    
    def _calculate_orderblock_strength(self, df: pd.DataFrame, index: int) -> float:
        """Calculate the strength of an Order Block."""
        if index < 5 or index >= len(df) - 5:
            return 0.5
        
        # Calculate price movement strength
        pre_move = df.iloc[index-5:index]['Close']
        post_move = df.iloc[index:index+5]['Close']
        
        if len(pre_move) == 0 or len(post_move) == 0:
            return 0.5
        
        price_change = abs(post_move.iloc[-1] - pre_move.iloc[0]) / pre_move.iloc[0]
        strength = min(price_change * 10, 0.8)  # Scale and cap
        
        # Add volume confirmation
        if 'Volume' in df.columns:
            avg_volume = df.iloc[index-20:index]['Volume'].mean()
            peak_volume = df.iloc[index]['Volume']
            if peak_volume > avg_volume * 1.5:
                strength += 0.2
        
        return min(strength, 1.0)
    
    def _is_strong_bullish_move(self, df: pd.DataFrame, index: int, min_strength: int) -> bool:
        """Check if there's a strong bullish move at the given index."""
        if index < min_strength or index >= len(df):
            return False
        
        # Check for consecutive higher closes
        closes = df.iloc[index-min_strength:index+1]['Close']
        return all(closes.iloc[i] > closes.iloc[i-1] for i in range(1, len(closes)))
    
    def _is_strong_bearish_move(self, df: pd.DataFrame, index: int, min_strength: int) -> bool:
        """Check if there's a strong bearish move at the given index."""
        if index < min_strength or index >= len(df):
            return False
        
        # Check for consecutive lower closes
        closes = df.iloc[index-min_strength:index+1]['Close']
        return all(closes.iloc[i] < closes.iloc[i-1] for i in range(1, len(closes)))