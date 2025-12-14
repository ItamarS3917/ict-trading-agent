"""
Unit tests for PatternDetector
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pattern_detector import PatternDetector


class TestPatternDetector:
    """Test cases for PatternDetector class."""
    
    @pytest.fixture
    def config(self):
        """Fixture for configuration."""
        return {
            'fvg_min_size': 0.001,
            'orderblock_strength': 3,
            'liquidity_threshold': 0.05
        }
    
    @pytest.fixture
    def detector(self, config):
        """Fixture for PatternDetector instance."""
        return PatternDetector(config)
    
    @pytest.fixture
    def sample_data(self):
        """Fixture for sample price data."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1H')
        np.random.seed(42)
        
        data = {
            'Open': np.random.uniform(15000, 15100, 100),
            'High': np.random.uniform(15000, 15200, 100),
            'Low': np.random.uniform(14900, 15000, 100),
            'Close': np.random.uniform(15000, 15100, 100),
            'Volume': np.random.uniform(1000, 10000, 100)
        }
        
        df = pd.DataFrame(data, index=dates)
        
        # Ensure High is highest and Low is lowest
        df['High'] = df[['Open', 'High', 'Close']].max(axis=1)
        df['Low'] = df[['Open', 'Low', 'Close']].min(axis=1)
        
        return df
    
    def test_detector_initialization(self, detector, config):
        """Test PatternDetector initialization."""
        assert detector.config == config
        assert detector.config['fvg_min_size'] == 0.001
    
    def test_detect_fair_value_gaps_empty_data(self, detector):
        """Test FVG detection with empty data."""
        df = pd.DataFrame()
        fvgs = detector.detect_fair_value_gaps(df)
        assert fvgs == []
    
    def test_detect_fair_value_gaps_insufficient_data(self, detector):
        """Test FVG detection with insufficient data."""
        df = pd.DataFrame({
            'Open': [15000],
            'High': [15100],
            'Low': [14900],
            'Close': [15050]
        })
        fvgs = detector.detect_fair_value_gaps(df)
        assert fvgs == []
    
    def test_detect_fair_value_gaps_with_data(self, detector, sample_data):
        """Test FVG detection with sample data."""
        fvgs = detector.detect_fair_value_gaps(sample_data)
        assert isinstance(fvgs, list)
        
        # If FVGs found, verify structure
        if fvgs:
            fvg = fvgs[0]
            assert 'type' in fvg
            assert 'direction' in fvg
            assert 'gap_size' in fvg
            assert 'entry_price' in fvg
            assert fvg['type'] == 'Fair Value Gap'
            assert fvg['direction'] in ['BULLISH', 'BEARISH']
    
    def test_detect_order_blocks_empty_data(self, detector):
        """Test Order Block detection with empty data."""
        df = pd.DataFrame()
        order_blocks = detector.detect_order_blocks(df)
        assert order_blocks == []
    
    def test_detect_order_blocks_insufficient_data(self, detector):
        """Test Order Block detection with insufficient data."""
        df = pd.DataFrame({
            'Open': [15000] * 10,
            'High': [15100] * 10,
            'Low': [14900] * 10,
            'Close': [15050] * 10
        })
        order_blocks = detector.detect_order_blocks(df)
        assert order_blocks == []
    
    def test_detect_order_blocks_with_data(self, detector, sample_data):
        """Test Order Block detection with sample data."""
        order_blocks = detector.detect_order_blocks(sample_data)
        assert isinstance(order_blocks, list)
        
        # If order blocks found, verify structure
        if order_blocks:
            ob = order_blocks[0]
            assert 'type' in ob
            assert 'direction' in ob
            assert 'block_high' in ob
            assert 'block_low' in ob
            assert ob['type'] == 'Order Block'
            assert ob['direction'] in ['BULLISH', 'BEARISH']
    
    def test_detect_liquidity_pools_empty_data(self, detector):
        """Test liquidity pool detection with empty data."""
        df = pd.DataFrame()
        pools = detector.detect_liquidity_pools(df)
        assert pools == []
    
    def test_detect_liquidity_pools_insufficient_data(self, detector):
        """Test liquidity pool detection with insufficient data."""
        df = pd.DataFrame({
            'High': [15000] * 30,
            'Low': [14900] * 30
        })
        pools = detector.detect_liquidity_pools(df)
        assert isinstance(pools, list)
    
    def test_detect_liquidity_pools_with_data(self, detector, sample_data):
        """Test liquidity pool detection with sample data."""
        pools = detector.detect_liquidity_pools(sample_data)
        assert isinstance(pools, list)
        
        # If pools found, verify structure
        if pools:
            pool = pools[0]
            assert 'type' in pool
            assert 'level_type' in pool
            assert 'price_level' in pool
            assert pool['type'] == 'Liquidity Pool'
            assert pool['level_type'] in ['SUPPORT', 'RESISTANCE']
    
    def test_fvg_strength_calculation(self, detector, sample_data):
        """Test FVG strength calculation."""
        # This tests the internal method indirectly through detect_fair_value_gaps
        fvgs = detector.detect_fair_value_gaps(sample_data)
        
        for fvg in fvgs:
            assert 0 <= fvg['strength'] <= 1.0
    
    def test_orderblock_strength_calculation(self, detector, sample_data):
        """Test Order Block strength calculation."""
        order_blocks = detector.detect_order_blocks(sample_data)
        
        for ob in order_blocks:
            assert 0 <= ob['strength'] <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
