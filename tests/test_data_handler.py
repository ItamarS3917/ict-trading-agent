"""
Unit tests for DataHandler
"""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_handler import DataHandler


class TestDataHandler:
    """Test cases for DataHandler class."""
    
    @pytest.fixture
    def handler(self):
        """Fixture for DataHandler instance."""
        return DataHandler()
    
    def test_handler_initialization(self, handler):
        """Test DataHandler initialization."""
        assert handler.cache_dir == "data/cache"
        assert os.path.exists(handler.cache_dir)
    
    def test_clean_data_empty(self, handler):
        """Test cleaning empty DataFrame."""
        df = pd.DataFrame()
        cleaned = handler._clean_data(df)
        assert cleaned.empty
    
    def test_clean_data_with_nan(self, handler):
        """Test cleaning DataFrame with NaN values."""
        df = pd.DataFrame({
            'Open': [100, None, 102],
            'High': [105, 106, None],
            'Low': [95, 96, 97],
            'Close': [102, 103, 104],
            'Volume': [1000, 2000, 3000]
        })
        
        cleaned = handler._clean_data(df)
        assert len(cleaned) < len(df)  # Some rows should be removed
        assert not cleaned.isnull().any().any()  # No NaN values
    
    def test_calculate_atr(self, handler):
        """Test ATR calculation."""
        dates = pd.date_range(start='2023-01-01', periods=50, freq='1H')
        df = pd.DataFrame({
            'High': [100 + i for i in range(50)],
            'Low': [95 + i for i in range(50)],
            'Close': [98 + i for i in range(50)]
        }, index=dates)
        
        atr = handler.calculate_atr(df, period=14)
        
        assert isinstance(atr, pd.Series)
        assert len(atr) == len(df)
        # ATR should have valid values after the period
        assert not atr.iloc[20:].isnull().all()
    
    def test_calculate_rsi(self, handler):
        """Test RSI calculation."""
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 
                           111, 110, 112, 114, 113, 115, 117, 116, 118, 120])
        
        rsi = handler._calculate_rsi(prices, period=14)
        
        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(prices)
        # RSI should be between 0 and 100
        valid_rsi = rsi.dropna()
        assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()
    
    def test_add_technical_indicators(self, handler):
        """Test adding technical indicators."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1H')
        df = pd.DataFrame({
            'Open': range(100, 200),
            'High': range(105, 205),
            'Low': range(95, 195),
            'Close': range(100, 200),
            'Volume': [1000 + i * 10 for i in range(100)]
        }, index=dates)
        
        df_with_indicators = handler.add_technical_indicators(df)
        
        # Check that indicators were added
        assert 'SMA_20' in df_with_indicators.columns
        assert 'SMA_50' in df_with_indicators.columns
        assert 'EMA_20' in df_with_indicators.columns
        assert 'ATR' in df_with_indicators.columns
        assert 'RSI' in df_with_indicators.columns
        
        # Check that original columns are preserved
        assert 'Close' in df_with_indicators.columns
        assert 'Volume' in df_with_indicators.columns


class TestDataValidation:
    """Test cases for data validation."""
    
    @pytest.fixture
    def handler(self):
        """Fixture for DataHandler instance."""
        return DataHandler()
    
    def test_required_columns(self, handler):
        """Test that required columns are checked."""
        df = pd.DataFrame({
            'Open': [100],
            'High': [105],
            'Low': [95],
            'Close': [102]
            # Missing Volume
        })
        
        cleaned = handler._clean_data(df)
        # Should still work but warn about missing columns
        assert not cleaned.empty
    
    def test_sorted_index(self, handler):
        """Test that data is sorted by date."""
        dates = pd.date_range(start='2023-01-01', periods=10, freq='1H')
        # Create unsorted data
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(105, 115),
            'Low': range(95, 105),
            'Close': range(100, 110),
            'Volume': [1000] * 10
        }, index=dates[::-1])  # Reverse order
        
        cleaned = handler._clean_data(df)
        
        # Check that index is sorted
        assert cleaned.index.is_monotonic_increasing


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
