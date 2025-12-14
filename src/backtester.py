"""
Backtesting Engine for ICT Trading Agent

Provides comprehensive backtesting capabilities with performance metrics,
risk analysis, and detailed trade logging.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

from data_handler import DataHandler
from ict_agent import ICTTradingAgent


class Backtester:
    """
    Backtesting engine for evaluating ICT trading strategies.
    """
    
    def __init__(self, initial_capital: float = 10000, 
                 commission: float = 2.0, slippage: float = 0.001):
        """
        Initialize the Backtester.
        
        Args:
            initial_capital: Starting capital for backtesting
            commission: Commission per trade in dollars
            slippage: Slippage as percentage (0.001 = 0.1%)
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.data_handler = DataHandler()
        self.agent = ICTTradingAgent()
        self.logger = logging.getLogger(__name__)
        
    def run_backtest(self, symbol: str, start_date: str, 
                     end_date: str, interval: str = "1h") -> Dict:
        """
        Run backtesting for a given symbol and date range.
        
        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            
        Returns:
            Dictionary containing backtest results and metrics
        """
        self.logger.info(f"Starting backtest for {symbol} from {start_date} to {end_date}")
        
        # Fetch historical data
        df = self.data_handler.get_historical_data(symbol, start_date, end_date, interval)
        
        if df.empty:
            self.logger.error("No data available for backtesting")
            return {"error": "No data available"}
        
        # Initialize tracking variables
        capital = self.initial_capital
        positions = []
        trades = []
        equity_curve = []
        
        # Simulate trading
        for i in range(100, len(df)):  # Start after lookback period
            current_date = df.index[i]
            current_price = df.iloc[i]['Close']
            
            # Update equity curve
            position_value = sum(pos['quantity'] * current_price for pos in positions)
            total_equity = capital + position_value
            equity_curve.append({
                'date': current_date,
                'equity': total_equity,
                'cash': capital,
                'positions_value': position_value
            })
            
            # Check for exit signals on existing positions
            for position in positions[:]:  # Use slice to avoid modification during iteration
                exit_signal = self._check_exit_signal(df.iloc[:i+1], position, current_price)
                
                if exit_signal:
                    # Close position
                    exit_price = current_price * (1 - self.slippage if position['direction'] == 'LONG' else 1 + self.slippage)
                    pnl = self._calculate_pnl(position, exit_price)
                    capital += pnl - self.commission
                    
                    trade = {
                        'entry_date': position['entry_date'],
                        'exit_date': current_date,
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'direction': position['direction'],
                        'quantity': position['quantity'],
                        'pnl': pnl,
                        'exit_reason': exit_signal
                    }
                    trades.append(trade)
                    positions.remove(position)
            
            # Generate new signals if we have capacity
            if len(positions) < 3:  # Max 3 concurrent positions
                signals = self.agent.generate_signals(symbol)
                
                for signal in signals[:1]:  # Take only the strongest signal
                    if signal['strength'] >= 0.6:  # Minimum strength threshold
                        # Calculate position size based on risk
                        position_size = self._calculate_position_size(
                            capital, 
                            signal['price'], 
                            signal['stop_loss']
                        )
                        
                        if position_size > 0:
                            entry_price = signal['price'] * (1 + self.slippage)
                            cost = position_size * entry_price + self.commission
                            
                            if cost <= capital:
                                capital -= cost
                                position = {
                                    'entry_date': current_date,
                                    'entry_price': entry_price,
                                    'direction': signal['direction'],
                                    'quantity': position_size,
                                    'stop_loss': signal['stop_loss'],
                                    'take_profit': signal['take_profit'],
                                    'pattern': signal['pattern']
                                }
                                positions.append(position)
        
        # Close any remaining positions at the end
        final_price = df.iloc[-1]['Close']
        for position in positions:
            exit_price = final_price * (1 - self.slippage if position['direction'] == 'LONG' else 1 + self.slippage)
            pnl = self._calculate_pnl(position, exit_price)
            capital += pnl - self.commission
            
            trade = {
                'entry_date': position['entry_date'],
                'exit_date': df.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'direction': position['direction'],
                'quantity': position['quantity'],
                'pnl': pnl,
                'exit_reason': 'End of backtest'
            }
            trades.append(trade)
        
        # Calculate performance metrics
        metrics = self._calculate_metrics(trades, equity_curve)
        
        self.logger.info(f"Backtest complete. Total trades: {len(trades)}")
        
        return {
            'symbol': symbol,
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_capital': capital,
            'trades': trades,
            'equity_curve': equity_curve,
            **metrics
        }
    
    def _check_exit_signal(self, df: pd.DataFrame, position: Dict, 
                          current_price: float) -> Optional[str]:
        """
        Check if an exit signal is triggered for a position.
        
        Args:
            df: Price data up to current point
            position: Current position
            current_price: Current market price
            
        Returns:
            Exit reason if signal triggered, None otherwise
        """
        # Check stop loss
        if position['direction'] == 'LONG':
            if current_price <= position['stop_loss']:
                return 'Stop Loss'
            if current_price >= position['take_profit']:
                return 'Take Profit'
        else:  # SHORT
            if current_price >= position['stop_loss']:
                return 'Stop Loss'
            if current_price <= position['take_profit']:
                return 'Take Profit'
        
        return None
    
    def _calculate_position_size(self, capital: float, entry_price: float, 
                                stop_loss: float, risk_per_trade: float = 0.02) -> int:
        """
        Calculate position size based on risk management rules.
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss: Stop loss price
            risk_per_trade: Risk per trade as percentage
            
        Returns:
            Position size in units
        """
        risk_amount = capital * risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            return 0
        
        position_size = int(risk_amount / price_risk)
        
        # Ensure position doesn't exceed available capital
        max_position = int((capital * 0.3) / entry_price)  # Max 30% of capital per position
        
        return min(position_size, max_position)
    
    def _calculate_pnl(self, position: Dict, exit_price: float) -> float:
        """
        Calculate profit/loss for a position.
        
        Args:
            position: Position dictionary
            exit_price: Exit price
            
        Returns:
            Profit or loss amount
        """
        if position['direction'] == 'LONG':
            pnl = (exit_price - position['entry_price']) * position['quantity']
        else:  # SHORT
            pnl = (position['entry_price'] - exit_price) * position['quantity']
        
        return pnl
    
    def _calculate_metrics(self, trades: List[Dict], 
                          equity_curve: List[Dict]) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            trades: List of completed trades
            equity_curve: Equity curve data
            
        Returns:
            Dictionary of performance metrics
        """
        if not trades:
            return {
                'total_return': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'average_win': 0.0,
                'average_loss': 0.0,
                'total_trades': 0
            }
        
        # Basic metrics
        total_pnl = sum(trade['pnl'] for trade in trades)
        total_return = (total_pnl / self.initial_capital)
        
        # Win rate
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winning_trades)
        gross_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Average win/loss
        avg_win = gross_profit / len(winning_trades) if winning_trades else 0
        avg_loss = gross_loss / len(losing_trades) if losing_trades else 0
        
        # Maximum drawdown
        equity_values = [e['equity'] for e in equity_curve]
        max_drawdown = self._calculate_max_drawdown(equity_values)
        
        # Sharpe ratio
        sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)
        
        return {
            'total_return': total_return,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades)
        }
    
    def _calculate_max_drawdown(self, equity_values: List[float]) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Args:
            equity_values: List of equity values
            
        Returns:
            Maximum drawdown as percentage
        """
        if not equity_values:
            return 0.0
        
        peak = equity_values[0]
        max_dd = 0.0
        
        for value in equity_values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, equity_curve: List[Dict], 
                               risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio from equity curve.
        
        Args:
            equity_curve: Equity curve data
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if len(equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i]['equity'] - equity_curve[i-1]['equity']) / equity_curve[i-1]['equity']
            returns.append(ret)
        
        if not returns:
            return 0.0
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualized Sharpe ratio (assuming hourly data)
        sharpe = (avg_return - risk_free_rate/8760) / std_return * np.sqrt(8760)
        
        return sharpe
    
    def generate_report(self, results: Dict) -> str:
        """
        Generate a formatted backtest report.
        
        Args:
            results: Backtest results dictionary
            
        Returns:
            Formatted report string
        """
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║           ICT TRADING AGENT - BACKTEST REPORT                    ║
╚══════════════════════════════════════════════════════════════════╝

Symbol: {results['symbol']}
Period: {results['start_date']} to {results['end_date']}

CAPITAL:
  Initial Capital:     ${results['initial_capital']:,.2f}
  Final Capital:       ${results['final_capital']:,.2f}
  Total Return:        {results['total_return']:.2%}

PERFORMANCE METRICS:
  Total Trades:        {results['total_trades']}
  Winning Trades:      {results['winning_trades']}
  Losing Trades:       {results['losing_trades']}
  Win Rate:            {results['win_rate']:.2%}
  Profit Factor:       {results['profit_factor']:.2f}
  
RISK METRICS:
  Sharpe Ratio:        {results['sharpe_ratio']:.2f}
  Max Drawdown:        {results['max_drawdown']:.2%}
  
TRADE STATISTICS:
  Average Win:         ${results['average_win']:,.2f}
  Average Loss:        ${results['average_loss']:,.2f}
  Avg Win/Loss Ratio:  {results['average_win']/results['average_loss']:.2f if results['average_loss'] > 0 else 0:.2f}

═══════════════════════════════════════════════════════════════════
"""
        return report
