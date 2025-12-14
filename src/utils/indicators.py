"""
Technical Indicators Module

Provides a comprehensive set of technical indicators for trading analysis,
including trend, momentum, volatility, and volume indicators.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


class TechnicalIndicators:
    """
    Collection of technical indicators for market analysis.
    """
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Simple Moving Average.
        
        Args:
            data: Price series
            period: SMA period
            
        Returns:
            SMA series
        """
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Exponential Moving Average.
        
        Args:
            data: Price series
            period: EMA period
            
        Returns:
            EMA series
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index.
        
        Args:
            data: Price series
            period: RSI period
            
        Returns:
            RSI series
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, 
             signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Moving Average Convergence Divergence.
        
        Args:
            data: Price series
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, 
                       std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands.
        
        Args:
            data: Price series
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (Upper band, Middle band, Lower band)
        """
        middle_band = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> pd.Series:
        """
        Average True Range.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period
            
        Returns:
            ATR series
        """
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return true_range.rolling(window=period).mean()
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, 
                   period: int = 14, smooth_k: int = 3, 
                   smooth_d: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: Stochastic period
            smooth_k: %K smoothing period
            smooth_d: %D smoothing period
            
        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()
        
        k_fast = 100 * (close - lowest_low) / (highest_high - lowest_low)
        k = k_fast.rolling(window=smooth_k).mean()
        d = k.rolling(window=smooth_d).mean()
        
        return k, d
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, 
            period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Average Directional Index (ADX) with +DI and -DI.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ADX period
            
        Returns:
            Tuple of (ADX, +DI, -DI)
        """
        # Calculate directional movement
        high_diff = high.diff()
        low_diff = -low.diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        # Calculate ATR
        atr = TechnicalIndicators.atr(high, low, close, period)
        
        # Calculate directional indicators
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def vwap(high: pd.Series, low: pd.Series, close: pd.Series, 
             volume: pd.Series) -> pd.Series:
        """
        Volume Weighted Average Price.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            volume: Volume series
            
        Returns:
            VWAP series
        """
        typical_price = (high + low + close) / 3
        return (typical_price * volume).cumsum() / volume.cumsum()
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On-Balance Volume.
        
        Args:
            close: Close price series
            volume: Volume series
            
        Returns:
            OBV series
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def fibonacci_retracements(high: float, low: float) -> dict:
        """
        Calculate Fibonacci retracement levels.
        
        Args:
            high: Swing high price
            low: Swing low price
            
        Returns:
            Dictionary of Fibonacci levels
        """
        diff = high - low
        
        return {
            '0.0': high,
            '0.236': high - (diff * 0.236),
            '0.382': high - (diff * 0.382),
            '0.500': high - (diff * 0.500),
            '0.618': high - (diff * 0.618),
            '0.786': high - (diff * 0.786),
            '1.0': low
        }
    
    @staticmethod
    def pivot_points(high: float, low: float, close: float) -> dict:
        """
        Calculate pivot points and support/resistance levels.
        
        Args:
            high: Previous period high
            low: Previous period low
            close: Previous period close
            
        Returns:
            Dictionary of pivot levels
        """
        pivot = (high + low + close) / 3
        
        return {
            'pivot': pivot,
            'r1': (2 * pivot) - low,
            'r2': pivot + (high - low),
            'r3': high + 2 * (pivot - low),
            's1': (2 * pivot) - high,
            's2': pivot - (high - low),
            's3': low - 2 * (high - pivot)
        }
    
    @staticmethod
    def ichimoku_cloud(high: pd.Series, low: pd.Series, close: pd.Series,
                      tenkan: int = 9, kijun: int = 26, senkou_b: int = 52,
                      displacement: int = 26) -> dict:
        """
        Ichimoku Cloud indicator.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            tenkan: Tenkan-sen period
            kijun: Kijun-sen period
            senkou_b: Senkou Span B period
            displacement: Displacement period
            
        Returns:
            Dictionary with Ichimoku components
        """
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (high.rolling(window=tenkan).max() + 
                     low.rolling(window=tenkan).min()) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (high.rolling(window=kijun).max() + 
                    low.rolling(window=kijun).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(displacement)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((high.rolling(window=senkou_b).max() + 
                         low.rolling(window=senkou_b).min()) / 2).shift(displacement)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-displacement)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    @staticmethod
    def supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
                   period: int = 10, multiplier: float = 3.0) -> Tuple[pd.Series, pd.Series]:
        """
        SuperTrend indicator.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            period: ATR period
            multiplier: ATR multiplier
            
        Returns:
            Tuple of (SuperTrend, Trend direction)
        """
        atr = TechnicalIndicators.atr(high, low, close, period)
        hl_avg = (high + low) / 2
        
        upper_band = hl_avg + (multiplier * atr)
        lower_band = hl_avg - (multiplier * atr)
        
        supertrend = pd.Series(index=close.index, dtype=float)
        direction = pd.Series(index=close.index, dtype=int)
        
        supertrend.iloc[0] = upper_band.iloc[0]
        direction.iloc[0] = 1
        
        for i in range(1, len(close)):
            if close.iloc[i] <= upper_band.iloc[i]:
                supertrend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = lower_band.iloc[i]
                direction.iloc[i] = 1
        
        return supertrend, direction
