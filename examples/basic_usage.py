"""
Basic Usage Example for ICT Trading Agent

This example demonstrates how to use the ICT Trading Agent
for basic market analysis and signal generation.
"""

import sys
sys.path.insert(0, '../src')

from ict_agent import ICTTradingAgent
from data_handler import DataHandler
from utils.config_loader import ConfigLoader
from utils.logger import LoggerSetup

# Setup logging
logger = LoggerSetup.setup_logger(
    name="example_basic",
    log_file="logs/example_basic.log",
    level="INFO"
)

def main():
    """Run basic ICT analysis example."""
    
    print("=" * 70)
    print("ICT Trading Agent - Basic Usage Example")
    print("=" * 70)
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load()
    
    # Initialize the agent
    agent = ICTTradingAgent(config)
    
    # Choose symbol to analyze
    symbol = "NQ=F"  # NASDAQ Futures
    print(f"\n📊 Analyzing {symbol}...")
    
    # 1. Analyze Market Structure
    print("\n1️⃣ Market Structure Analysis")
    print("-" * 70)
    
    market_structure = agent.analyze_market_structure(symbol)
    
    print(f"Trend Direction: {market_structure.get('trend_direction', 'N/A')}")
    print(f"Swing Highs: {len(market_structure.get('swing_points', {}).get('highs', []))}")
    print(f"Swing Lows: {len(market_structure.get('swing_points', {}).get('lows', []))}")
    
    # 2. Detect Fair Value Gaps
    print("\n2️⃣ Fair Value Gap Detection")
    print("-" * 70)
    
    fvgs = agent.detect_fair_value_gaps(symbol)
    print(f"Total FVGs Detected: {len(fvgs)}")
    
    if fvgs:
        print("\nTop 3 Fair Value Gaps:")
        for i, fvg in enumerate(fvgs[:3], 1):
            print(f"  {i}. {fvg['direction']} FVG")
            print(f"     Gap Size: {fvg['gap_size']:.4%}")
            print(f"     Entry: ${fvg['entry_price']:.2f}")
            print(f"     Strength: {fvg['strength']:.2%}")
            print()
    
    # 3. Detect Order Blocks
    print("3️⃣ Order Block Detection")
    print("-" * 70)
    
    order_blocks = agent.detect_order_blocks(symbol)
    print(f"Total Order Blocks Detected: {len(order_blocks)}")
    
    if order_blocks:
        print("\nTop 3 Order Blocks:")
        for i, ob in enumerate(order_blocks[:3], 1):
            print(f"  {i}. {ob['direction']} Order Block")
            print(f"     Range: ${ob['block_low']:.2f} - ${ob['block_high']:.2f}")
            print(f"     Entry: ${ob['entry_price']:.2f}")
            print(f"     Strength: {ob['strength']:.2%}")
            print()
    
    # 4. Generate Trading Signals
    print("4️⃣ Trading Signal Generation")
    print("-" * 70)
    
    signals = agent.generate_signals(symbol)
    print(f"Total Signals Generated: {len(signals)}")
    
    if signals:
        print("\n🚨 Trading Signals:")
        for i, signal in enumerate(signals[:5], 1):
            emoji = "🟢" if signal['direction'] in ['LONG', 'BULLISH'] else "🔴"
            print(f"\n  {emoji} Signal #{i}: {signal['pattern']}")
            print(f"     Direction: {signal['direction']}")
            print(f"     Entry Price: ${signal['price']:.2f}")
            print(f"     Stop Loss: ${signal['stop_loss']:.2f}")
            print(f"     Take Profit: ${signal['take_profit']:.2f}")
            print(f"     Strength: {signal['strength']:.2%}")
            
            # Calculate R:R
            risk = abs(signal['price'] - signal['stop_loss'])
            reward = abs(signal['take_profit'] - signal['price'])
            rr_ratio = reward / risk if risk > 0 else 0
            print(f"     Risk/Reward: 1:{rr_ratio:.2f}")
    else:
        print("\n📭 No trading signals detected at this time.")
    
    print("\n" + "=" * 70)
    print("✅ Analysis Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
