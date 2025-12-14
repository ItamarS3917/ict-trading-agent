"""
Performance Reporting Module

Generates comprehensive performance reports and analytics for trading strategies.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json


class PerformanceReporter:
    """
    Generates performance reports and analytics.
    """
    
    def __init__(self):
        """Initialize the performance reporter."""
        self.reports = []
    
    def generate_trade_report(self, trades: List[Dict]) -> Dict:
        """
        Generate comprehensive trade performance report.
        
        Args:
            trades: List of completed trades
            
        Returns:
            Performance report dictionary
        """
        if not trades:
            return self._empty_report()
        
        df = pd.DataFrame(trades)
        
        # Basic statistics
        total_trades = len(trades)
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] <= 0]
        
        # Profitability metrics
        total_pnl = df['pnl'].sum()
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Average metrics
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        avg_trade = df['pnl'].mean()
        
        # Win/loss streaks
        win_streak, loss_streak = self._calculate_streaks(df['pnl'])
        
        # Trade duration analysis
        if 'entry_date' in df.columns and 'exit_date' in df.columns:
            df['entry_date'] = pd.to_datetime(df['entry_date'])
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['duration'] = (df['exit_date'] - df['entry_date']).dt.total_seconds() / 3600
            avg_duration = df['duration'].mean()
        else:
            avg_duration = 0
        
        # Pattern analysis
        pattern_performance = self._analyze_patterns(df) if 'pattern' in df.columns else {}
        
        # Direction analysis
        direction_performance = self._analyze_directions(df) if 'direction' in df.columns else {}
        
        # Time-based analysis
        time_analysis = self._analyze_time_performance(df)
        
        return {
            'summary': {
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
                'profit_factor': profit_factor,
            },
            'averages': {
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'avg_trade': avg_trade,
                'avg_duration_hours': avg_duration,
            },
            'streaks': {
                'max_win_streak': win_streak,
                'max_loss_streak': loss_streak,
            },
            'pattern_performance': pattern_performance,
            'direction_performance': direction_performance,
            'time_analysis': time_analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_monthly_report(self, trades: List[Dict], 
                               equity_curve: List[Dict]) -> Dict:
        """
        Generate monthly performance report.
        
        Args:
            trades: List of completed trades
            equity_curve: Equity curve data
            
        Returns:
            Monthly performance report
        """
        if not trades:
            return {'error': 'No trades available'}
        
        df = pd.DataFrame(trades)
        df['exit_date'] = pd.to_datetime(df['exit_date'])
        df['month'] = df['exit_date'].dt.to_period('M')
        
        monthly_stats = []
        
        for month, month_trades in df.groupby('month'):
            stats = {
                'month': str(month),
                'trades': len(month_trades),
                'winning_trades': len(month_trades[month_trades['pnl'] > 0]),
                'losing_trades': len(month_trades[month_trades['pnl'] <= 0]),
                'total_pnl': month_trades['pnl'].sum(),
                'win_rate': len(month_trades[month_trades['pnl'] > 0]) / len(month_trades),
                'avg_pnl': month_trades['pnl'].mean(),
                'best_trade': month_trades['pnl'].max(),
                'worst_trade': month_trades['pnl'].min(),
            }
            monthly_stats.append(stats)
        
        return {
            'monthly_performance': monthly_stats,
            'best_month': max(monthly_stats, key=lambda x: x['total_pnl']) if monthly_stats else None,
            'worst_month': min(monthly_stats, key=lambda x: x['total_pnl']) if monthly_stats else None,
        }
    
    def generate_drawdown_report(self, equity_curve: List[Dict]) -> Dict:
        """
        Generate drawdown analysis report.
        
        Args:
            equity_curve: Equity curve data
            
        Returns:
            Drawdown report
        """
        if not equity_curve:
            return {'error': 'No equity curve data'}
        
        df = pd.DataFrame(equity_curve)
        equity = df['equity'].values
        
        # Calculate drawdowns
        peak = equity[0]
        drawdowns = []
        current_dd = {'start': 0, 'peak_value': peak, 'trough': 0, 'trough_value': peak}
        
        for i, value in enumerate(equity):
            if value > peak:
                # New peak, save previous drawdown if exists
                if current_dd['trough'] > 0 and current_dd['trough_value'] < current_dd['peak_value']:
                    dd_pct = (current_dd['peak_value'] - current_dd['trough_value']) / current_dd['peak_value']
                    drawdowns.append({
                        'start_idx': current_dd['start'],
                        'trough_idx': current_dd['trough'],
                        'peak_value': current_dd['peak_value'],
                        'trough_value': current_dd['trough_value'],
                        'drawdown_pct': dd_pct,
                        'duration': current_dd['trough'] - current_dd['start']
                    })
                
                peak = value
                current_dd = {'start': i, 'peak_value': peak, 'trough': i, 'trough_value': peak}
            elif value < current_dd['trough_value']:
                current_dd['trough'] = i
                current_dd['trough_value'] = value
        
        # Add final drawdown if exists
        if current_dd['trough_value'] < current_dd['peak_value']:
            dd_pct = (current_dd['peak_value'] - current_dd['trough_value']) / current_dd['peak_value']
            drawdowns.append({
                'start_idx': current_dd['start'],
                'trough_idx': current_dd['trough'],
                'peak_value': current_dd['peak_value'],
                'trough_value': current_dd['trough_value'],
                'drawdown_pct': dd_pct,
                'duration': current_dd['trough'] - current_dd['start']
            })
        
        if not drawdowns:
            max_dd = 0
            max_dd_duration = 0
            avg_dd = 0
        else:
            max_dd = max(dd['drawdown_pct'] for dd in drawdowns)
            max_dd_duration = max(dd['duration'] for dd in drawdowns)
            avg_dd = np.mean([dd['drawdown_pct'] for dd in drawdowns])
        
        return {
            'max_drawdown': max_dd,
            'max_drawdown_duration': max_dd_duration,
            'average_drawdown': avg_dd,
            'total_drawdowns': len(drawdowns),
            'drawdown_periods': drawdowns[:5]  # Return top 5 worst drawdowns
        }
    
    def generate_risk_metrics(self, trades: List[Dict], 
                             equity_curve: List[Dict],
                             initial_capital: float) -> Dict:
        """
        Generate risk-adjusted performance metrics.
        
        Args:
            trades: List of completed trades
            equity_curve: Equity curve data
            initial_capital: Starting capital
            
        Returns:
            Risk metrics report
        """
        if not trades or not equity_curve:
            return {'error': 'Insufficient data'}
        
        # Calculate returns
        df_equity = pd.DataFrame(equity_curve)
        returns = df_equity['equity'].pct_change().dropna()
        
        # Sharpe Ratio
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = returns - risk_free_rate
        sharpe = np.sqrt(252) * excess_returns.mean() / returns.std() if returns.std() > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        sortino = (np.sqrt(252) * excess_returns.mean() / downside_returns.std() 
                  if len(downside_returns) > 0 and downside_returns.std() > 0 else 0)
        
        # Calmar Ratio
        max_dd = self._calculate_max_drawdown(df_equity['equity'].values)
        annual_return = (df_equity['equity'].iloc[-1] / initial_capital) ** (252 / len(df_equity)) - 1
        calmar = annual_return / max_dd if max_dd > 0 else 0
        
        # Value at Risk (95%)
        var_95 = np.percentile(returns, 5)
        
        # Conditional VaR (Expected Shortfall)
        cvar_95 = returns[returns <= var_95].mean()
        
        # Win/Loss ratio
        df_trades = pd.DataFrame(trades)
        winning_trades = df_trades[df_trades['pnl'] > 0]['pnl']
        losing_trades = df_trades[df_trades['pnl'] < 0]['pnl']
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades.mean()) if len(losing_trades) > 0 else 0
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # Expectancy
        win_rate = len(winning_trades) / len(df_trades) if len(df_trades) > 0 else 0
        expectancy = (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
        
        return {
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'value_at_risk_95': var_95,
            'conditional_var_95': cvar_95,
            'win_loss_ratio': win_loss_ratio,
            'expectancy': expectancy,
            'volatility': returns.std() * np.sqrt(252),
            'max_drawdown': max_dd
        }
    
    def _empty_report(self) -> Dict:
        """Return empty report structure."""
        return {
            'summary': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
            },
            'message': 'No trades available for reporting'
        }
    
    def _calculate_streaks(self, pnl_series: pd.Series) -> Tuple[int, int]:
        """Calculate maximum winning and losing streaks."""
        win_streak = 0
        loss_streak = 0
        current_win = 0
        current_loss = 0
        
        for pnl in pnl_series:
            if pnl > 0:
                current_win += 1
                current_loss = 0
                win_streak = max(win_streak, current_win)
            elif pnl < 0:
                current_loss += 1
                current_win = 0
                loss_streak = max(loss_streak, current_loss)
        
        return win_streak, loss_streak
    
    def _analyze_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by pattern type."""
        pattern_stats = {}
        
        for pattern, group in df.groupby('pattern'):
            pattern_stats[pattern] = {
                'trades': len(group),
                'win_rate': len(group[group['pnl'] > 0]) / len(group),
                'total_pnl': group['pnl'].sum(),
                'avg_pnl': group['pnl'].mean(),
            }
        
        return pattern_stats
    
    def _analyze_directions(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by trade direction."""
        direction_stats = {}
        
        for direction, group in df.groupby('direction'):
            direction_stats[direction] = {
                'trades': len(group),
                'win_rate': len(group[group['pnl'] > 0]) / len(group),
                'total_pnl': group['pnl'].sum(),
                'avg_pnl': group['pnl'].mean(),
            }
        
        return direction_stats
    
    def _analyze_time_performance(self, df: pd.DataFrame) -> Dict:
        """Analyze performance by time periods."""
        if 'exit_date' not in df.columns:
            return {}
        
        df['exit_date'] = pd.to_datetime(df['exit_date'])
        df['hour'] = df['exit_date'].dt.hour
        df['day_of_week'] = df['exit_date'].dt.dayofweek
        
        # Best/worst hours
        hourly = df.groupby('hour')['pnl'].agg(['sum', 'mean', 'count']).to_dict('index')
        
        # Best/worst days of week
        daily = df.groupby('day_of_week')['pnl'].agg(['sum', 'mean', 'count']).to_dict('index')
        
        return {
            'hourly_performance': hourly,
            'daily_performance': daily
        }
    
    def _calculate_max_drawdown(self, equity: np.ndarray) -> float:
        """Calculate maximum drawdown."""
        peak = equity[0]
        max_dd = 0.0
        
        for value in equity:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd
    
    def export_report(self, report: Dict, format: str = 'json',
                     filepath: Optional[str] = None) -> str:
        """
        Export report to file.
        
        Args:
            report: Report dictionary
            format: Export format ('json', 'txt')
            filepath: Optional file path
            
        Returns:
            Filepath where report was saved
        """
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"reports/performance_report_{timestamp}.{format}"
        
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format == 'txt':
            with open(filepath, 'w') as f:
                f.write(self._format_report_text(report))
        
        return filepath
    
    def _format_report_text(self, report: Dict) -> str:
        """Format report as readable text."""
        lines = [
            "=" * 70,
            "PERFORMANCE REPORT",
            "=" * 70,
            f"\nGenerated: {report.get('timestamp', datetime.now().isoformat())}",
            "\n" + "-" * 70,
            "SUMMARY",
            "-" * 70,
        ]
        
        if 'summary' in report:
            for key, value in report['summary'].items():
                if isinstance(value, float):
                    lines.append(f"{key}: {value:.4f}")
                else:
                    lines.append(f"{key}: {value}")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
