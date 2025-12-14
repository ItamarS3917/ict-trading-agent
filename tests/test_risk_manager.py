"""
Unit tests for RiskManager
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from risk_manager import RiskManager, Position


class TestRiskManager:
    """Test cases for RiskManager class."""
    
    @pytest.fixture
    def config(self):
        """Fixture for configuration."""
        return {
            'risk_per_trade': 0.02,
            'max_positions': 3,
            'max_portfolio_risk': 0.06,
            'max_position_size': 0.3,
            'stop_loss_atr_multiplier': 2,
            'take_profit_ratio': 2,
            'max_daily_loss': 0.05,
            'max_drawdown': 0.20
        }
    
    @pytest.fixture
    def risk_manager(self, config):
        """Fixture for RiskManager instance."""
        return RiskManager(config)
    
    def test_risk_manager_initialization(self, risk_manager, config):
        """Test RiskManager initialization."""
        assert risk_manager.config == config
        assert risk_manager.config['risk_per_trade'] == 0.02
        assert len(risk_manager.positions) == 0
    
    def test_calculate_position_size_basic(self, risk_manager):
        """Test basic position size calculation."""
        capital = 10000
        entry_price = 100
        stop_loss = 95  # 5% stop loss
        
        position_size = risk_manager.calculate_position_size(
            capital, entry_price, stop_loss
        )
        
        assert position_size > 0
        assert isinstance(position_size, int)
        
        # Risk should be approximately 2% of capital
        risk = position_size * (entry_price - stop_loss)
        risk_pct = risk / capital
        assert 0.01 <= risk_pct <= 0.03  # Allow some tolerance
    
    def test_calculate_position_size_zero_risk(self, risk_manager):
        """Test position sizing with zero price risk."""
        capital = 10000
        entry_price = 100
        stop_loss = 100  # Same as entry = no risk
        
        position_size = risk_manager.calculate_position_size(
            capital, entry_price, stop_loss
        )
        
        assert position_size == 0
    
    def test_calculate_position_size_max_limit(self, risk_manager):
        """Test position sizing respects max position size."""
        capital = 10000
        entry_price = 10  # Low price
        stop_loss = 9.9  # Small stop loss
        
        position_size = risk_manager.calculate_position_size(
            capital, entry_price, stop_loss
        )
        
        # Should not exceed 30% of capital
        max_position = int((capital * 0.3) / entry_price)
        assert position_size <= max_position
    
    def test_validate_trade_success(self, risk_manager):
        """Test successful trade validation."""
        signal = {
            'price': 100,
            'stop_loss': 95,
            'take_profit': 110,
            'direction': 'LONG'
        }
        capital = 10000
        
        is_valid, reason = risk_manager.validate_trade(signal, capital, [])
        
        assert is_valid
        assert reason == "Trade validated"
    
    def test_validate_trade_max_positions(self, risk_manager):
        """Test trade validation with max positions reached."""
        signal = {
            'price': 100,
            'stop_loss': 95,
            'take_profit': 110
        }
        capital = 10000
        
        # Create max positions
        positions = [
            Position('SYM1', 'LONG', 100, 10, 95, 110, '2023-01-01'),
            Position('SYM2', 'LONG', 100, 10, 95, 110, '2023-01-01'),
            Position('SYM3', 'LONG', 100, 10, 95, 110, '2023-01-01')
        ]
        
        is_valid, reason = risk_manager.validate_trade(signal, capital, positions)
        
        assert not is_valid
        assert "Maximum number of positions" in reason
    
    def test_validate_trade_poor_risk_reward(self, risk_manager):
        """Test trade validation with poor risk/reward ratio."""
        signal = {
            'price': 100,
            'stop_loss': 95,
            'take_profit': 102,  # Only 1:0.4 R:R
            'direction': 'LONG'
        }
        capital = 10000
        
        is_valid, reason = risk_manager.validate_trade(signal, capital, [])
        
        assert not is_valid
        assert "Risk/reward ratio" in reason
    
    def test_calculate_stop_loss_long(self, risk_manager):
        """Test stop loss calculation for long position."""
        entry_price = 100
        atr = 2
        
        stop_loss = risk_manager.calculate_stop_loss(
            entry_price, 'LONG', atr
        )
        
        assert stop_loss < entry_price
        expected = entry_price - (atr * 2)
        assert abs(stop_loss - expected) < 0.01
    
    def test_calculate_stop_loss_short(self, risk_manager):
        """Test stop loss calculation for short position."""
        entry_price = 100
        atr = 2
        
        stop_loss = risk_manager.calculate_stop_loss(
            entry_price, 'SHORT', atr
        )
        
        assert stop_loss > entry_price
        expected = entry_price + (atr * 2)
        assert abs(stop_loss - expected) < 0.01
    
    def test_calculate_take_profit_long(self, risk_manager):
        """Test take profit calculation for long position."""
        entry_price = 100
        stop_loss = 95
        
        take_profit = risk_manager.calculate_take_profit(
            entry_price, stop_loss, 'LONG'
        )
        
        assert take_profit > entry_price
        # Should be 2x the risk
        risk = entry_price - stop_loss
        expected_reward = risk * 2
        assert abs((take_profit - entry_price) - expected_reward) < 0.01
    
    def test_calculate_take_profit_short(self, risk_manager):
        """Test take profit calculation for short position."""
        entry_price = 100
        stop_loss = 105
        
        take_profit = risk_manager.calculate_take_profit(
            entry_price, stop_loss, 'SHORT'
        )
        
        assert take_profit < entry_price
        # Should be 2x the risk
        risk = stop_loss - entry_price
        expected_reward = risk * 2
        assert abs((entry_price - take_profit) - expected_reward) < 0.01
    
    def test_check_daily_loss_limit_not_reached(self, risk_manager):
        """Test daily loss limit check when not reached."""
        starting_capital = 10000
        current_capital = 9600  # 4% loss
        
        limit_reached, loss_pct = risk_manager.check_daily_loss_limit(
            starting_capital, current_capital
        )
        
        assert not limit_reached
        assert abs(loss_pct - 0.04) < 0.001
    
    def test_check_daily_loss_limit_reached(self, risk_manager):
        """Test daily loss limit check when reached."""
        starting_capital = 10000
        current_capital = 9400  # 6% loss
        
        limit_reached, loss_pct = risk_manager.check_daily_loss_limit(
            starting_capital, current_capital
        )
        
        assert limit_reached
        assert loss_pct > 0.05
    
    def test_check_drawdown_limit_not_reached(self, risk_manager):
        """Test drawdown limit check when not reached."""
        peak_capital = 10000
        current_capital = 8500  # 15% drawdown
        
        limit_reached, drawdown = risk_manager.check_drawdown_limit(
            peak_capital, current_capital
        )
        
        assert not limit_reached
        assert abs(drawdown - 0.15) < 0.001
    
    def test_check_drawdown_limit_reached(self, risk_manager):
        """Test drawdown limit check when reached."""
        peak_capital = 10000
        current_capital = 7500  # 25% drawdown
        
        limit_reached, drawdown = risk_manager.check_drawdown_limit(
            peak_capital, current_capital
        )
        
        assert limit_reached
        assert drawdown > 0.20
    
    def test_calculate_kelly_criterion(self, risk_manager):
        """Test Kelly Criterion calculation."""
        win_rate = 0.6
        avg_win = 100
        avg_loss = 50
        
        kelly = risk_manager.calculate_kelly_criterion(
            win_rate, avg_win, avg_loss
        )
        
        assert 0 <= kelly <= risk_manager.config['max_position_size']
        assert kelly > 0  # Should be positive with these stats


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
