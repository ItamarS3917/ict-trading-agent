# ICT Trading Agent - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Core Features](#core-features)
5. [Configuration](#configuration)
6. [API Reference](#api-reference)
7. [Examples](#examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Introduction

The ICT Trading Agent is a comprehensive algorithmic trading tool that implements Inner Circle Trader (ICT) concepts for automated market analysis. It provides pattern detection, backtesting, risk management, and real-time signal generation for NASDAQ futures and other instruments.

### Key Capabilities

- **Pattern Detection**: Fair Value Gaps (FVGs), Order Blocks, Liquidity Pools
- **Market Structure Analysis**: Break of Structure (BOS), Change of Character (CHoCH)
- **Backtesting Engine**: Historical performance analysis with comprehensive metrics
- **Risk Management**: Position sizing, stop loss/take profit calculation, portfolio risk control
- **Real-time Alerts**: Webhook and email notifications for trading opportunities
- **Interactive Dashboard**: Streamlit-based web interface for visualization

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ItamarS3917/ict-trading-agent.git
   cd ict-trading-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure settings:**
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml with your preferences
   ```

---

## Quick Start

### Basic Market Analysis

```python
from ict_agent import ICTTradingAgent

# Initialize agent
agent = ICTTradingAgent()

# Analyze market structure
market_structure = agent.analyze_market_structure("NQ=F")
print(f"Trend: {market_structure['trend_direction']}")

# Detect patterns
fvgs = agent.detect_fair_value_gaps("NQ=F")
print(f"Found {len(fvgs)} Fair Value Gaps")

# Generate signals
signals = agent.generate_signals("NQ=F")
for signal in signals:
    print(f"{signal['direction']} @ ${signal['price']}")
```

### Running the Dashboard

```bash
streamlit run src/dashboard.py
```

### Command Line Interface

```bash
# Analyze current market
python src/main.py --analyze --symbol NQ=F

# Run backtest
python src/main.py --backtest --symbol NQ=F --start-date 2023-01-01 --end-date 2023-12-31

# Generate signals
python src/main.py --signals --symbol NQ=F
```

---

## Core Features

### 1. Pattern Detection

#### Fair Value Gaps (FVGs)

Fair Value Gaps are price imbalances where there's a gap between consecutive candles.

```python
fvgs = agent.detect_fair_value_gaps("NQ=F")

for fvg in fvgs:
    print(f"Direction: {fvg['direction']}")
    print(f"Gap Size: {fvg['gap_size']:.4%}")
    print(f"Entry: ${fvg['entry_price']:.2f}")
    print(f"Strength: {fvg['strength']:.2%}")
```

#### Order Blocks

Order Blocks identify institutional order zones marked by strong price movements.

```python
order_blocks = agent.detect_order_blocks("NQ=F")

for ob in order_blocks:
    print(f"Direction: {ob['direction']}")
    print(f"Range: ${ob['block_low']:.2f} - ${ob['block_high']:.2f}")
    print(f"Strength: {ob['strength']:.2%}")
```

#### Liquidity Pools

Liquidity pools identify areas where stop losses accumulate.

```python
pools = agent.detect_liquidity_pools("NQ=F")

for pool in pools:
    print(f"Type: {pool['level_type']}")
    print(f"Price: ${pool['price_level']:.2f}")
    print(f"Touches: {pool['touches']}")
```

### 2. Backtesting

Run historical simulations to evaluate strategy performance:

```python
from backtester import Backtester

backtester = Backtester(initial_capital=10000)

results = backtester.run_backtest(
    symbol="NQ=F",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

print(f"Total Return: {results['total_return']:.2%}")
print(f"Win Rate: {results['win_rate']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

### 3. Risk Management

#### Position Sizing

```python
from risk_manager import RiskManager

risk_manager = RiskManager()

position_size = risk_manager.calculate_position_size(
    capital=10000,
    entry_price=15000,
    stop_loss=14900
)

print(f"Position Size: {position_size} units")
```

#### Stop Loss & Take Profit

```python
# Calculate stop loss based on ATR
stop_loss = risk_manager.calculate_stop_loss(
    entry_price=15000,
    direction='LONG',
    atr=50
)

# Calculate take profit based on R:R ratio
take_profit = risk_manager.calculate_take_profit(
    entry_price=15000,
    stop_loss=stop_loss,
    direction='LONG',
    rr_ratio=2.0
)
```

#### Trade Validation

```python
signal = {
    'price': 15000,
    'stop_loss': 14900,
    'take_profit': 15200,
    'direction': 'LONG'
}

is_valid, reason = risk_manager.validate_trade(signal, capital=10000, current_positions=[])

if is_valid:
    print("Trade validated!")
else:
    print(f"Trade rejected: {reason}")
```

### 4. Notifications

Set up alerts for trading opportunities:

```python
from utils.notifications import NotificationSystem

notifier = NotificationSystem({
    'enabled': True,
    'webhook_url': 'your_webhook_url',
    'email_enabled': True
})

# Send signal alert
notifier.send_signal_alert(signal)

# Send trade alert
notifier.send_trade_alert(trade, alert_type="ENTRY")
```

### 5. Technical Indicators

Access a comprehensive set of technical indicators:

```python
from utils.indicators import TechnicalIndicators

# RSI
rsi = TechnicalIndicators.rsi(df['Close'], period=14)

# MACD
macd, signal, histogram = TechnicalIndicators.macd(df['Close'])

# Bollinger Bands
upper, middle, lower = TechnicalIndicators.bollinger_bands(df['Close'])

# ATR
atr = TechnicalIndicators.atr(df['High'], df['Low'], df['Close'])
```

---

## Configuration

Edit `config/config.yaml` to customize the agent:

```yaml
# Trading Parameters
trading:
  symbol: "NQ=F"
  timeframe: "1h"
  lookback_period: 100

# Pattern Detection
patterns:
  fvg_min_size: 0.001
  orderblock_strength: 3
  liquidity_threshold: 0.05

# Risk Management
risk:
  risk_per_trade: 0.02
  max_positions: 3
  stop_loss_atr_multiplier: 2
  take_profit_ratio: 2

# Backtesting
backtesting:
  initial_capital: 10000
  commission: 2.0
  slippage: 0.001

# Alerts
alerts:
  enabled: true
  webhook_url: ""
  email_enabled: false
```

---

## API Reference

### ICTTradingAgent

Main trading agent class.

**Methods:**
- `analyze_market_structure(symbol)` - Analyze market structure
- `detect_fair_value_gaps(symbol)` - Detect FVG patterns
- `detect_order_blocks(symbol)` - Detect order block patterns
- `detect_liquidity_pools(symbol)` - Detect liquidity pools
- `generate_signals(symbol)` - Generate trading signals

### Backtester

Backtesting engine.

**Methods:**
- `run_backtest(symbol, start_date, end_date)` - Run backtest
- `generate_report(results)` - Generate formatted report

### RiskManager

Risk management system.

**Methods:**
- `calculate_position_size(capital, entry_price, stop_loss)` - Calculate position size
- `validate_trade(signal, capital, positions)` - Validate trade
- `calculate_stop_loss(entry_price, direction, atr)` - Calculate stop loss
- `calculate_take_profit(entry_price, stop_loss, direction)` - Calculate take profit

---

## Examples

See the `examples/` directory for detailed examples:

- `basic_usage.py` - Basic market analysis
- `backtest_example.py` - Comprehensive backtesting
- `risk_management_example.py` - Risk management features

Run examples:
```bash
cd examples
python basic_usage.py
python backtest_example.py
python risk_management_example.py
```

---

## Best Practices

### 1. Risk Management

- **Never risk more than 1-2% per trade**
- **Use stop losses on every trade**
- **Diversify across multiple instruments**
- **Monitor daily loss limits**

### 2. Pattern Validation

- **Wait for confluence** - Multiple patterns confirming the same direction
- **Consider market structure** - Trade with the trend
- **Check volume** - Higher volume increases pattern reliability
- **Use higher timeframes** - More reliable signals on 1H+ charts

### 3. Backtesting

- **Use sufficient data** - At least 1 year of historical data
- **Include slippage and commissions** - For realistic results
- **Test multiple market conditions** - Bull, bear, and sideways markets
- **Walk-forward validation** - Test on unseen data

### 4. Live Trading

- **Start small** - Begin with minimum position sizes
- **Paper trade first** - Test strategies without real money
- **Keep a trading journal** - Record all trades and lessons learned
- **Review regularly** - Analyze performance weekly/monthly

---

## Troubleshooting

### Common Issues

**Issue: "No data available for symbol"**
- Check internet connection
- Verify symbol format (e.g., "NQ=F" for NASDAQ futures)
- Try a different data period

**Issue: "Module not found" errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**Issue: Dashboard not loading**
- Check if port 8501 is available
- Try: `streamlit run src/dashboard.py --server.port 8502`

**Issue: Slow backtesting**
- Reduce data range or use larger intervals
- Consider using daily data instead of hourly

### Getting Help

- **GitHub Issues**: Report bugs or request features
- **Email**: itamarshealtiel1@gmail.com
- **Documentation**: Check this guide and inline code comments

---

## Disclaimer

This tool is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Always conduct your own research and consider seeking advice from financial professionals.

---

**Last Updated**: December 2024  
**Version**: 1.0.0
