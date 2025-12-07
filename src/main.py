#!/usr/bin/env python3
"""
ICT Trading Agent - Main CLI Application

This module provides the command-line interface for the ICT Trading Agent.
It supports analysis, backtesting, and signal generation for NASDAQ futures.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional

from ict_agent import ICTTradingAgent
from data_handler import DataHandler
from backtester import Backtester


def analyze_market(symbol: str = "NQ=F") -> dict:
    """Analyze current market conditions."""
    print(f"🔍 Analyzing market conditions for {symbol}...")
    
    agent = ICTTradingAgent()
    
    # Get market structure analysis
    market_structure = agent.analyze_market_structure(symbol)
    
    # Detect patterns
    fvgs = agent.detect_fair_value_gaps(symbol)
    order_blocks = agent.detect_order_blocks(symbol)
    
    # Generate signals
    signals = agent.generate_signals(symbol)
    
    analysis = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "market_structure": market_structure,
        "fair_value_gaps": fvgs,
        "order_blocks": order_blocks,
        "signals": signals
    }
    
    print("✅ Analysis complete!")
    return analysis


def run_backtest(symbol: str, start_date: str, end_date: str, initial_capital: float = 10000) -> dict:
    """Run backtesting analysis."""
    print(f"🧪 Running backtest for {symbol} from {start_date} to {end_date}...")
    
    backtester = Backtester(initial_capital=initial_capital)
    results = backtester.run_backtest(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date
    )
    
    print("📊 Backtest Results:")
    print(f"Total Return: {results['total_return']:.2%}")
    print(f"Win Rate: {results['win_rate']:.2%}")
    print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {results['max_drawdown']:.2%}")
    
    return results


def generate_signals(symbol: str = "NQ=F") -> list:
    """Generate trading signals for the specified symbol."""
    print(f"📡 Generating signals for {symbol}...")
    
    agent = ICTTradingAgent()
    signals = agent.generate_signals(symbol)
    
    if signals:
        print(f"🚨 Found {len(signals)} trading signals:")
        for i, signal in enumerate(signals, 1):
            print(f"{i}. {signal['type']} signal at {signal['price']} - {signal['strength']}")
    else:
        print("📭 No signals detected at this time.")
    
    return signals


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ICT Trading Agent - Algorithmic Trading Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--analyze", 
        action="store_true", 
        help="Analyze current market conditions"
    )
    
    parser.add_argument(
        "--backtest", 
        action="store_true", 
        help="Run backtesting analysis"
    )
    
    parser.add_argument(
        "--signals", 
        action="store_true", 
        help="Generate trading signals"
    )
    
    parser.add_argument(
        "--symbol", 
        type=str, 
        default="NQ=F", 
        help="Trading symbol (default: NQ=F)"
    )
    
    parser.add_argument(
        "--start-date", 
        type=str, 
        help="Start date for backtesting (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end-date", 
        type=str, 
        help="End date for backtesting (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--capital", 
        type=float, 
        default=10000, 
        help="Initial capital for backtesting (default: 10000)"
    )
    
    args = parser.parse_args()
    
    if not any([args.analyze, args.backtest, args.signals]):
        parser.print_help()
        return
    
    try:
        if args.analyze:
            analysis = analyze_market(args.symbol)
            # Could save results to file or display more details
            
        elif args.backtest:
            if not args.start_date or not args.end_date:
                print("❌ Error: --start-date and --end-date are required for backtesting")
                return
                
            results = run_backtest(
                symbol=args.symbol,
                start_date=args.start_date,
                end_date=args.end_date,
                initial_capital=args.capital
            )
            
        elif args.signals:
            signals = generate_signals(args.symbol)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()