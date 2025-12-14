"""
Backtesting Example for ICT Trading Agent

This example demonstrates how to run comprehensive backtests
and analyze strategy performance.
"""

import sys
sys.path.insert(0, '../src')

from datetime import datetime, timedelta
from backtester import Backtester
from utils.config_loader import ConfigLoader
from utils.logger import LoggerSetup

# Setup logging
logger = LoggerSetup.setup_logger(
    name="example_backtest",
    log_file="logs/example_backtest.log",
    level="INFO"
)

def main():
    """Run backtesting example."""
    
    print("=" * 70)
    print("ICT Trading Agent - Backtesting Example")
    print("=" * 70)
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load()
    
    # Backtest parameters
    symbol = "NQ=F"
    initial_capital = 10000
    
    # Date range (last 1 year)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    print(f"\n📊 Backtesting Configuration:")
    print(f"  Symbol: {symbol}")
    print(f"  Initial Capital: ${initial_capital:,.2f}")
    print(f"  Start Date: {start_date.strftime('%Y-%m-%d')}")
    print(f"  End Date: {end_date.strftime('%Y-%m-%d')}")
    
    # Initialize backtester
    backtester = Backtester(
        initial_capital=initial_capital,
        commission=config.get('backtesting.commission', 2.0),
        slippage=config.get('backtesting.slippage', 0.001)
    )
    
    print("\n🧪 Running backtest... (this may take a few minutes)")
    print("-" * 70)
    
    # Run backtest
    results = backtester.run_backtest(
        symbol=symbol,
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        interval='1h'
    )
    
    if 'error' in results:
        print(f"\n❌ Error: {results['error']}")
        return
    
    # Display results
    print("\n✅ Backtest Complete!")
    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    
    print(f"\n💰 CAPITAL:")
    print(f"  Initial Capital:     ${results['initial_capital']:,.2f}")
    print(f"  Final Capital:       ${results['final_capital']:,.2f}")
    profit = results['final_capital'] - results['initial_capital']
    print(f"  Total Profit/Loss:   ${profit:,.2f}")
    print(f"  Total Return:        {results['total_return']:.2%}")
    
    print(f"\n📊 TRADE STATISTICS:")
    print(f"  Total Trades:        {results['total_trades']}")
    print(f"  Winning Trades:      {results['winning_trades']}")
    print(f"  Losing Trades:       {results['losing_trades']}")
    print(f"  Win Rate:            {results['win_rate']:.2%}")
    
    print(f"\n💵 PROFIT METRICS:")
    print(f"  Average Win:         ${results['average_win']:,.2f}")
    print(f"  Average Loss:        ${results['average_loss']:,.2f}")
    if results['average_loss'] > 0:
        print(f"  Win/Loss Ratio:      {results['average_win']/results['average_loss']:.2f}")
    print(f"  Profit Factor:       {results['profit_factor']:.2f}")
    
    print(f"\n📉 RISK METRICS:")
    print(f"  Sharpe Ratio:        {results['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown:        {results['max_drawdown']:.2%}")
    
    # Show some trade examples
    if results.get('trades'):
        print("\n📝 SAMPLE TRADES:")
        print("-" * 70)
        
        trades = results['trades']
        
        # Show first 3 trades
        print("\nFirst 3 Trades:")
        for i, trade in enumerate(trades[:3], 1):
            pnl_emoji = "✅" if trade['pnl'] > 0 else "❌"
            print(f"\n  Trade #{i} {pnl_emoji}")
            print(f"    Direction:   {trade['direction']}")
            print(f"    Entry:       ${trade['entry_price']:.2f} @ {trade['entry_date']}")
            print(f"    Exit:        ${trade['exit_price']:.2f} @ {trade['exit_date']}")
            print(f"    P&L:         ${trade['pnl']:.2f}")
            print(f"    Exit Reason: {trade['exit_reason']}")
        
        # Show best and worst trades
        best_trade = max(trades, key=lambda x: x['pnl'])
        worst_trade = min(trades, key=lambda x: x['pnl'])
        
        print("\n🏆 Best Trade:")
        print(f"    P&L: ${best_trade['pnl']:.2f}")
        print(f"    Entry: ${best_trade['entry_price']:.2f} @ {best_trade['entry_date']}")
        
        print("\n💔 Worst Trade:")
        print(f"    P&L: ${worst_trade['pnl']:.2f}")
        print(f"    Entry: ${worst_trade['entry_price']:.2f} @ {worst_trade['entry_date']}")
    
    # Generate and display full report
    print("\n" + "=" * 70)
    print("FULL REPORT")
    print("=" * 70)
    
    report = backtester.generate_report(results)
    print(report)
    
    print("\n💡 TIP: Use the Streamlit dashboard for visual analysis!")
    print("   Run: streamlit run ../src/dashboard.py")


if __name__ == "__main__":
    main()
