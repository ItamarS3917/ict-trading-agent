"""
Risk Management Module

Provides comprehensive risk management functionality including
position sizing, portfolio risk, and risk metrics calculation.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging


@dataclass
class Position:
    """Represents a trading position."""
    symbol: str
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    quantity: int
    stop_loss: float
    take_profit: float
    entry_date: str
    

class RiskManager:
    """
    Manages risk for trading operations.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the Risk Manager.
        
        Args:
            config: Configuration dictionary with risk parameters
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
        self.positions: List[Position] = []
    
    def _default_config(self) -> Dict:
        """Default risk management configuration."""
        return {
            'risk_per_trade': 0.02,  # 2% risk per trade
            'max_positions': 3,
            'max_portfolio_risk': 0.06,  # 6% max total risk
            'max_position_size': 0.3,  # 30% max position size
            'stop_loss_atr_multiplier': 2,
            'take_profit_ratio': 2,  # 1:2 risk/reward
            'max_daily_loss': 0.05,  # 5% max daily loss
            'max_drawdown': 0.20  # 20% max drawdown
        }
    
    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss: float,
        risk_per_trade: Optional[float] = None
    ) -> int:
        """
        Calculate position size based on risk management rules.
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade: Risk per trade as percentage (optional)
            
        Returns:
            Position size in units
        """
        risk_pct = risk_per_trade or self.config['risk_per_trade']
        risk_amount = capital * risk_pct
        
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            self.logger.warning("Invalid stop loss - price risk is zero or negative")
            return 0
        
        # Calculate position size based on risk
        position_size = int(risk_amount / price_risk)
        
        # Ensure position doesn't exceed max position size
        max_position = int((capital * self.config['max_position_size']) / entry_price)
        position_size = min(position_size, max_position)
        
        # Ensure position is affordable
        total_cost = position_size * entry_price
        if total_cost > capital:
            position_size = int(capital / entry_price)
        
        return position_size
    
    def validate_trade(
        self,
        signal: Dict,
        capital: float,
        current_positions: Optional[List[Position]] = None
    ) -> Tuple[bool, str]:
        """
        Validate if a trade meets risk management criteria.
        
        Args:
            signal: Trading signal dictionary
            capital: Available capital
            current_positions: List of current positions
            
        Returns:
            Tuple of (is_valid, reason)
        """
        positions = current_positions or self.positions
        
        # Check max positions
        if len(positions) >= self.config['max_positions']:
            return False, "Maximum number of positions reached"
        
        # Check if capital is sufficient
        entry_price = signal.get('price', 0)
        stop_loss = signal.get('stop_loss', 0)
        
        position_size = self.calculate_position_size(capital, entry_price, stop_loss)
        
        if position_size <= 0:
            return False, "Insufficient capital for position"
        
        # Check portfolio risk
        current_risk = self._calculate_portfolio_risk(positions, capital)
        new_risk = self.config['risk_per_trade']
        
        if current_risk + new_risk > self.config['max_portfolio_risk']:
            return False, "Would exceed maximum portfolio risk"
        
        # Check risk/reward ratio
        risk = abs(entry_price - stop_loss)
        reward = abs(signal.get('take_profit', 0) - entry_price)
        
        if risk > 0:
            rr_ratio = reward / risk
            min_rr = self.config['take_profit_ratio']
            
            if rr_ratio < min_rr:
                return False, f"Risk/reward ratio {rr_ratio:.2f} below minimum {min_rr}"
        
        return True, "Trade validated"
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        direction: str,
        atr: float,
        support_resistance: Optional[float] = None
    ) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            direction: Trade direction ('LONG' or 'SHORT')
            atr: Average True Range
            support_resistance: Optional support/resistance level
            
        Returns:
            Stop loss price
        """
        atr_multiplier = self.config['stop_loss_atr_multiplier']
        
        if direction.upper() in ['LONG', 'BULLISH']:
            # For long positions, stop loss below entry
            atr_stop = entry_price - (atr * atr_multiplier)
            
            # Use support level if provided and it's closer
            if support_resistance and support_resistance < entry_price:
                return max(atr_stop, support_resistance)
            
            return atr_stop
        
        else:  # SHORT or BEARISH
            # For short positions, stop loss above entry
            atr_stop = entry_price + (atr * atr_multiplier)
            
            # Use resistance level if provided and it's closer
            if support_resistance and support_resistance > entry_price:
                return min(atr_stop, support_resistance)
            
            return atr_stop
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        direction: str,
        rr_ratio: Optional[float] = None
    ) -> float:
        """
        Calculate take profit price based on risk/reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            direction: Trade direction
            rr_ratio: Risk/reward ratio (optional)
            
        Returns:
            Take profit price
        """
        ratio = rr_ratio or self.config['take_profit_ratio']
        risk = abs(entry_price - stop_loss)
        reward = risk * ratio
        
        if direction.upper() in ['LONG', 'BULLISH']:
            return entry_price + reward
        else:
            return entry_price - reward
    
    def check_daily_loss_limit(
        self,
        starting_capital: float,
        current_capital: float
    ) -> Tuple[bool, float]:
        """
        Check if daily loss limit has been reached.
        
        Args:
            starting_capital: Capital at start of day
            current_capital: Current capital
            
        Returns:
            Tuple of (limit_reached, current_loss_pct)
        """
        loss = starting_capital - current_capital
        loss_pct = loss / starting_capital if starting_capital > 0 else 0
        
        limit_reached = loss_pct >= self.config['max_daily_loss']
        
        if limit_reached:
            self.logger.warning(
                f"Daily loss limit reached: {loss_pct:.2%} "
                f"(limit: {self.config['max_daily_loss']:.2%})"
            )
        
        return limit_reached, loss_pct
    
    def check_drawdown_limit(
        self,
        peak_capital: float,
        current_capital: float
    ) -> Tuple[bool, float]:
        """
        Check if maximum drawdown limit has been reached.
        
        Args:
            peak_capital: Peak capital value
            current_capital: Current capital
            
        Returns:
            Tuple of (limit_reached, current_drawdown)
        """
        drawdown = (peak_capital - current_capital) / peak_capital if peak_capital > 0 else 0
        
        limit_reached = drawdown >= self.config['max_drawdown']
        
        if limit_reached:
            self.logger.warning(
                f"Maximum drawdown limit reached: {drawdown:.2%} "
                f"(limit: {self.config['max_drawdown']:.2%})"
            )
        
        return limit_reached, drawdown
    
    def _calculate_portfolio_risk(
        self,
        positions: List[Position],
        capital: float
    ) -> float:
        """
        Calculate total portfolio risk from all positions.
        
        Args:
            positions: List of current positions
            capital: Total capital
            
        Returns:
            Total risk as percentage
        """
        total_risk = 0.0
        
        for position in positions:
            risk = abs(position.entry_price - position.stop_loss) * position.quantity
            risk_pct = risk / capital if capital > 0 else 0
            total_risk += risk_pct
        
        return total_risk
    
    def calculate_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion.
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade
            avg_loss: Average losing trade
            
        Returns:
            Optimal position size as percentage
        """
        if avg_loss <= 0:
            return 0.0
        
        win_loss_ratio = avg_win / abs(avg_loss)
        
        kelly_pct = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use fractional Kelly (25%) for more conservative sizing
        fractional_kelly = kelly_pct * 0.25
        
        # Cap at max position size
        return max(0.0, min(fractional_kelly, self.config['max_position_size']))
    
    def calculate_var(
        self,
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk (VaR).
        
        Args:
            returns: Series of returns
            confidence_level: Confidence level (default 95%)
            
        Returns:
            VaR value
        """
        if len(returns) == 0:
            return 0.0
        
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def calculate_sharpe_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sharpe Ratio.
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / returns.std()
    
    def calculate_sortino_ratio(
        self,
        returns: pd.Series,
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate Sortino Ratio (focuses on downside deviation).
        
        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = returns[returns < 0]
        
        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0
        
        return np.sqrt(252) * excess_returns.mean() / downside_returns.std()
