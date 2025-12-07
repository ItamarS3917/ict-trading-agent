"""
Data Handler Module for ICT Trading Agent

Handles data fetching, processing, and caching for market data.
"""

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import os


class DataHandler:
    """
    Handles market data fetching and processing for the ICT Trading Agent.
    """
    
    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize the DataHandler.
        
        Args:
            cache_dir: Directory for data caching
        """
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_price_data(self, symbol: str, period: str = "1mo", 
                      interval: str = "1h") -> pd.DataFrame:
        """
        Fetch price data for a given symbol.
        
        Args:
            symbol: Trading symbol (e.g., "NQ=F")
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                print(f"Warning: No data found for symbol {symbol}")
                return pd.DataFrame()
            
            # Clean and prepare data
            df = self._clean_data(df)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_historical_data(self, symbol: str, start_date: str, 
                           end_date: str, interval: str = "1h") -> pd.DataFrame:
        """
        Fetch historical data for a specific date range.
        
        Args:
            symbol: Trading symbol
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            interval: Data interval
        
        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                print(f"Warning: No historical data found for {symbol}")
                return pd.DataFrame()
            
            return self._clean_data(df)
            
        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare market data.
        
        Args:
            df: Raw market data DataFrame
        
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        # Ensure we have the required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Warning: Missing columns in data: {missing_columns}")
        
        # Sort by date
        df = df.sort_index()
        
        return df
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            df: OHLC DataFrame
            period: ATR calculation period
        
        Returns:
            Series with ATR values
        """
        high = df['High']
        low = df['Low']
        close = df['Close'].shift(1)
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        return true_range.rolling(window=period).mean()
    
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
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_20'] = df['Close'].ewm(span=20).mean()
        
        # ATR
        df['ATR'] = self.calculate_atr(df)
        
        # RSI
        df['RSI'] = self._calculate_rsi(df['Close'])
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
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