"""
Risk Management Example for ICT Trading Agent

This example demonstrates how to use the risk management features
for position sizing and risk control.
"""

import sys
sys.path.insert(0, '../src')

from risk_manager import RiskManager, Position
from utils.config_loader import ConfigLoader
import pandas as pd

def main():
    """Run risk management example."""
    
    print("=" * 70)
    print("ICT Trading Agent - Risk Management Example")
    print("=" * 70)
    
    # Load configuration
    config_loader = ConfigLoader()
    config = config_loader.load()
    
    # Initialize risk manager
    risk_config = config.get('risk', {})
    risk_manager = RiskManager(risk_config)
    
    # Trading parameters
    capital = 10000
    
    print(f"\n💰 Account Information:")
    print(f"  Capital: ${capital:,.2f}")
    print(f"  Risk per Trade: {risk_config.get('risk_per_trade', 0.02):.1%}")
    print(f"  Max Positions: {risk_config.get('max_positions', 3)}")
    print(f"  Max Portfolio Risk: {risk_config.get('max_portfolio_risk', 0.06):.1%}")
    
    # Example 1: Calculate Position Size
    print("\n" + "=" * 70)
    print("1️⃣ Position Sizing Example")
    print("=" * 70)
    
    entry_price = 15000
    stop_loss = 14900
    atr = 50
    
    print(f"\nTrade Setup:")
    print(f"  Entry Price: ${entry_price}")
    print(f"  Stop Loss: ${stop_loss}")
    print(f"  Price Risk: ${entry_price - stop_loss}")
    print(f"  ATR: ${atr}")
    
    position_size = risk_manager.calculate_position_size(
        capital=capital,
        entry_price=entry_price,
        stop_loss=stop_loss
    )
    
    total_cost = position_size * entry_price
    risk_amount = position_size * (entry_price - stop_loss)
    
    print(f"\n✅ Calculated Position Size: {position_size} units")
    print(f"  Total Cost: ${total_cost:,.2f}")
    print(f"  Risk Amount: ${risk_amount:,.2f} ({risk_amount/capital:.2%} of capital)")
    
    # Example 2: Calculate Stop Loss and Take Profit
    print("\n" + "=" * 70)
    print("2️⃣ Stop Loss & Take Profit Calculation")
    print("=" * 70)
    
    # Long position
    print("\nLong Position:")
    sl_long = risk_manager.calculate_stop_loss(
        entry_price=entry_price,
        direction='LONG',
        atr=atr
    )
    tp_long = risk_manager.calculate_take_profit(
        entry_price=entry_price,
        stop_loss=sl_long,
        direction='LONG'
    )
    
    print(f"  Entry: ${entry_price}")
    print(f"  Stop Loss: ${sl_long:.2f}")
    print(f"  Take Profit: ${tp_long:.2f}")
    print(f"  Risk: ${entry_price - sl_long:.2f}")
    print(f"  Reward: ${tp_long - entry_price:.2f}")
    print(f"  R:R Ratio: 1:{(tp_long - entry_price)/(entry_price - sl_long):.2f}")
    
    # Short position
    print("\nShort Position:")
    sl_short = risk_manager.calculate_stop_loss(
        entry_price=entry_price,
        direction='SHORT',
        atr=atr
    )
    tp_short = risk_manager.calculate_take_profit(
        entry_price=entry_price,
        stop_loss=sl_short,
        direction='SHORT'
    )
    
    print(f"  Entry: ${entry_price}")
    print(f"  Stop Loss: ${sl_short:.2f}")
    print(f"  Take Profit: ${tp_short:.2f}")
    print(f"  Risk: ${sl_short - entry_price:.2f}")
    print(f"  Reward: ${entry_price - tp_short:.2f}")
    print(f"  R:R Ratio: 1:{(entry_price - tp_short)/(sl_short - entry_price):.2f}")
    
    # Example 3: Validate Trade
    print("\n" + "=" * 70)
    print("3️⃣ Trade Validation Example")
    print("=" * 70)
    
    signal = {
        'price': entry_price,
        'stop_loss': sl_long,
        'take_profit': tp_long,
        'direction': 'LONG'
    }
    
    is_valid, reason = risk_manager.validate_trade(signal, capital, [])
    
    print(f"\nSignal Details:")
    print(f"  Direction: {signal['direction']}")
    print(f"  Entry: ${signal['price']}")
    print(f"  Stop Loss: ${signal['stop_loss']:.2f}")
    print(f"  Take Profit: ${signal['take_profit']:.2f}")
    
    print(f"\nValidation Result:")
    if is_valid:
        print(f"  ✅ Trade is VALID")
        print(f"  Reason: {reason}")
    else:
        print(f"  ❌ Trade is INVALID")
        print(f"  Reason: {reason}")
    
    # Example 4: Daily Loss Limit Check
    print("\n" + "=" * 70)
    print("4️⃣ Daily Loss Limit Check")
    print("=" * 70)
    
    starting_capital = 10000
    
    scenarios = [
        ("Normal trading day", 9700),   # 3% loss
        ("Bad day", 9400),              # 6% loss
        ("Profitable day", 10500)       # 5% gain
    ]
    
    for scenario, current_capital in scenarios:
        limit_reached, loss_pct = risk_manager.check_daily_loss_limit(
            starting_capital, current_capital
        )
        
        status = "🛑 LIMIT REACHED" if limit_reached else "✅ OK"
        pnl = current_capital - starting_capital
        
        print(f"\n{scenario}:")
        print(f"  Current Capital: ${current_capital:,.2f}")
        print(f"  P&L: ${pnl:+,.2f} ({(pnl/starting_capital)*100:+.2f}%)")
        print(f"  Status: {status}")
    
    # Example 5: Portfolio Risk
    print("\n" + "=" * 70)
    print("5️⃣ Portfolio Risk Management")
    print("=" * 70)
    
    # Simulate some positions
    positions = [
        Position('NQ=F', 'LONG', 15000, 1, 14900, 15200, '2023-12-01'),
        Position('ES=F', 'LONG', 4800, 2, 4750, 4900, '2023-12-01'),
    ]
    
    print(f"\nCurrent Positions: {len(positions)}")
    for i, pos in enumerate(positions, 1):
        print(f"\n  Position {i}:")
        print(f"    Symbol: {pos.symbol}")
        print(f"    Direction: {pos.direction}")
        print(f"    Quantity: {pos.quantity}")
        print(f"    Entry: ${pos.entry_price}")
        print(f"    Stop Loss: ${pos.stop_loss}")
        
        risk = abs(pos.entry_price - pos.stop_loss) * pos.quantity
        print(f"    Risk: ${risk:.2f}")
    
    # Check if new trade is acceptable
    new_signal = {
        'price': 15000,
        'stop_loss': 14900,
        'take_profit': 15200,
        'direction': 'LONG'
    }
    
    print(f"\n📊 New Trade Evaluation:")
    is_valid, reason = risk_manager.validate_trade(new_signal, capital, positions)
    
    if is_valid:
        print(f"  ✅ Can accept new position")
    else:
        print(f"  ❌ Cannot accept new position")
    print(f"  Reason: {reason}")
    
    # Example 6: Kelly Criterion
    print("\n" + "=" * 70)
    print("6️⃣ Kelly Criterion for Position Sizing")
    print("=" * 70)
    
    # Historical performance
    win_rate = 0.60
    avg_win = 150
    avg_loss = 75
    
    kelly = risk_manager.calculate_kelly_criterion(win_rate, avg_win, avg_loss)
    
    print(f"\nHistorical Performance:")
    print(f"  Win Rate: {win_rate:.1%}")
    print(f"  Average Win: ${avg_win}")
    print(f"  Average Loss: ${avg_loss}")
    
    print(f"\n📈 Kelly Criterion Recommendation:")
    print(f"  Optimal Position Size: {kelly:.2%} of capital")
    print(f"  For ${capital:,.2f} capital: ${capital * kelly:,.2f} per position")
    
    print("\n" + "=" * 70)
    print("✅ Risk Management Examples Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
