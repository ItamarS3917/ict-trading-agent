# 📊 ICT Trading Agent - Algorithmic Trading Analysis Tool

**Automated trading strategy implementation with real-time market analysis using Inner Circle Trader concepts**

## ✨ What's New in v1.0

**Major Features Added:**
- 🧪 **Complete Backtesting Engine** - Historical simulation with comprehensive metrics
- 📊 **15+ Technical Indicators** - RSI, MACD, Bollinger Bands, ATR, Ichimoku, and more
- 🔔 **Advanced Notification System** - Webhook and email alerts for trading signals
- 📈 **Interactive Streamlit Dashboard** - Real-time visualization and analysis
- 🛡️ **Risk Management Module** - Position sizing, stop loss/TP calculation, portfolio risk
- 📈 **Performance Reporting** - Detailed analytics, drawdown analysis, monthly reports
- ⚙️ **Configuration System** - YAML-based settings with validation
- 📝 **Comprehensive Documentation** - User guide, examples, and API reference
- ✅ **Unit Tests** - Test coverage for core functionality

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🎯 Overview

The ICT Trading Agent is an intelligent algorithmic trading analysis tool that implements Inner Circle Trader (ICT) concepts for NASDAQ futures analysis. It provides automated pattern detection, market structure analysis, and trading opportunity alerts with professional-grade risk management and backtesting capabilities.

## 🚀 Features

### Core Trading Features
- 📈 **ICT Pattern Detection**: Fair Value Gaps (FVGs), Order Blocks, Liquidity Pools
- 🔍 **Market Structure Analysis**: Break of Structure (BOS), Change of Character (CHoCH)
- 📊 **Signal Generation**: Automated trading signals with strength scoring
- 💧 **Liquidity Zone Detection**: Advanced algorithms for identifying accumulation zones

### Analysis & Backtesting
- 🧪 **Backtesting Engine**: Historical data simulation with realistic execution
- 📈 **Performance Metrics**: Win rate, Sharpe ratio, profit factor, max drawdown
- 📊 **Equity Curve**: Visual tracking of strategy performance
- 🎯 **Trade Analytics**: Detailed trade-by-trade analysis

### Risk Management
- 🛡️ **Position Sizing**: Kelly Criterion and percentage-based sizing
- 🎯 **Stop Loss/Take Profit**: ATR-based and custom calculations
- 📊 **Portfolio Risk**: Total risk tracking and limits
- ⚠️ **Risk Limits**: Daily loss limits and drawdown controls

### Technical Indicators (15+)
- 📉 Trend: SMA, EMA, SuperTrend, Ichimoku Cloud
- 📊 Momentum: RSI, MACD, Stochastic, ADX
- 📈 Volatility: ATR, Bollinger Bands
- 📊 Volume: OBV, VWAP
- 🎯 Support/Resistance: Fibonacci, Pivot Points

### User Interface & Notifications
- 📱 **Interactive Dashboard**: Streamlit-based web interface
- 🔔 **Multi-Channel Alerts**: Webhook (Discord/Slack), email, console
- 🖥️ **CLI Interface**: Command-line tools for automation
- 📊 **Visual Charts**: Candlestick charts with pattern overlays

### Configuration & Logging
- ⚙️ **YAML Configuration**: Easy customization of all parameters
- 📝 **Comprehensive Logging**: Rotating logs with multiple levels
- 🔧 **Flexible Setup**: Configurable for any instrument or timeframe

## 🛠️ Tech Stack

- **Python 3.9+**
- **Streamlit** - Interactive web dashboard
- **TradingView** - Market data integration
- **NumPy** - Numerical computations
- **Pandas** - Data manipulation and analysis
- **Scikit-learn** - Machine learning algorithms
- **Plotly** - Interactive charting
- **yfinance** - Financial data retrieval

## 📋 Requirements

```
python>=3.9
streamlit>=1.25.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
yfinance>=0.2.0
scikit-learn>=1.3.0
requests>=2.31.0
```

## 🚀 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ItamarS3917/ict-trading-agent.git
cd ict-trading-agent
```

2. **Create virtual environment:**
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

## 🎮 Quick Start

### Option 1: Interactive Dashboard (Recommended)
```bash
streamlit run src/dashboard.py
```
Open your browser to `http://localhost:8501` for the interactive web interface.

### Option 2: Python API
```python
from src.ict_agent import ICTTradingAgent

# Initialize agent
agent = ICTTradingAgent()

# Analyze market
market_structure = agent.analyze_market_structure("NQ=F")
print(f"Trend: {market_structure['trend_direction']}")

# Detect patterns
fvgs = agent.detect_fair_value_gaps("NQ=F")
print(f"Found {len(fvgs)} Fair Value Gaps")

# Generate signals
signals = agent.generate_signals("NQ=F")
for signal in signals:
    print(f"{signal['direction']} @ ${signal['price']:.2f}")
```

### Option 3: Command Line Interface
```bash
# Analyze current market
python src/main.py --analyze --symbol NQ=F

# Run backtest
python src/main.py --backtest --symbol NQ=F --start-date 2023-01-01 --end-date 2023-12-31

# Generate signals
python src/main.py --signals --symbol NQ=F
```

### Option 4: Run Examples
```bash
cd examples
python basic_usage.py           # Basic market analysis
python backtest_example.py      # Backtesting demo
python risk_management_example.py  # Risk management demo
```

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive guide with API reference
- **[Changelog](CHANGELOG.md)** - Version history and improvements
- **[Examples](examples/)** - Practical usage examples
- **Inline Documentation** - Detailed docstrings in all modules

## 🎮 Advanced Usage

### Backtesting with Risk Management
```python
from src.backtester import Backtester
from src.risk_manager import RiskManager

# Setup backtester
backtester = Backtester(initial_capital=10000, commission=2.0)

# Run backtest
results = backtester.run_backtest(
    symbol="NQ=F",
    start_date="2023-01-01",
    end_date="2023-12-31"
)

# Display results
print(f"Total Return: {results['total_return']:.2%}")
print(f"Win Rate: {results['win_rate']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")

# Generate report
report = backtester.generate_report(results)
print(report)
```

### Using Technical Indicators
```python
from src.utils.indicators import TechnicalIndicators
from src.data_handler import DataHandler

# Get market data
handler = DataHandler()
df = handler.get_price_data("NQ=F", period="1mo")

# Calculate indicators
rsi = TechnicalIndicators.rsi(df['Close'], period=14)
macd, signal, histogram = TechnicalIndicators.macd(df['Close'])
upper, middle, lower = TechnicalIndicators.bollinger_bands(df['Close'])

print(f"Current RSI: {rsi.iloc[-1]:.2f}")
print(f"MACD: {macd.iloc[-1]:.2f}")
```

### Setting Up Notifications
```python
from src.utils.notifications import NotificationSystem

# Configure notifications
notifier = NotificationSystem({
    'enabled': True,
    'webhook_url': 'YOUR_DISCORD_WEBHOOK_URL',
    'email_enabled': True,
    'email_smtp_server': 'smtp.gmail.com',
    'email_from': 'your-email@gmail.com',
    'email_to': 'recipient@gmail.com'
})

# Send alert for trading signal
notifier.send_signal_alert(signal)

# Send trade execution alert
notifier.send_trade_alert(trade, alert_type="ENTRY")
```

## 📊 Key Concepts

### Inner Circle Trader (ICT) Concepts
- **Fair Value Gaps (FVGs)**: Price imbalances in the market
- **Order Blocks**: Institutional order zones
- **Market Structure**: Break of Structure (BOS) and Change of Character (CHoCH)
- **Liquidity Pools**: Areas of accumulated orders
- **Premium/Discount**: Market position relative to equilibrium

### Trading Features
- **Pattern Recognition**: Automated detection of ICT patterns
- **Risk Management**: Position sizing and stop-loss calculations
- **Backtesting**: Historical performance analysis
- **Real-time Alerts**: Notification system for trading opportunities

## 📁 Project Structure

```
ict-trading-agent/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main CLI application
│   ├── dashboard.py         # Streamlit dashboard
│   ├── ict_agent.py         # Core ICT trading agent
│   ├── data_handler.py      # Data fetching and processing
│   ├── pattern_detector.py  # ICT pattern detection
│   ├── backtester.py        # Backtesting engine
│   └── utils/
│       ├── __init__.py
│       ├── indicators.py    # Technical indicators
│       └── notifications.py # Alert system
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_patterns.py
│   └── test_backtester.py
├── config/
│   ├── config.yaml          # Configuration file
│   └── config.example.yaml  # Example configuration
├── data/                    # Historical data storage
├── docs/                    # Documentation
├── requirements.txt
├── setup.py
└── README.md
```

## ⚙️ Configuration

Edit `config/config.yaml` to customize:

```yaml
trading:
  symbol: "NQ=F"  # NASDAQ Futures
  timeframe: "1h"
  lookback_period: 100

patterns:
  fvg_min_size: 0.1
  orderblock_strength: 3
  liquidity_threshold: 0.05

alerts:
  enabled: true
  webhook_url: ""
  email_enabled: false

backtesting:
  initial_capital: 10000
  risk_per_trade: 0.02
  commission: 2.0
```

## 🧪 Testing

The project includes comprehensive unit tests for all core functionality.

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_patterns.py -v

# Run with coverage report
python -m pytest --cov=src tests/

# Run tests for specific module
python -m pytest tests/test_risk_manager.py -v
```

**Test Coverage:**
- Pattern detection (FVGs, Order Blocks, Liquidity Pools)
- Data handling and validation
- Risk management calculations
- Position sizing algorithms
- Stop loss and take profit calculations

## 📈 Performance & Metrics

The ICT Trading Agent provides comprehensive performance analysis:

### Profitability Metrics
- **Total Return** - Overall strategy performance
- **Win Rate** - Percentage of winning trades
- **Profit Factor** - Ratio of gross profit to gross loss
- **Average Win/Loss** - Mean profit/loss per trade
- **Win/Loss Ratio** - Average win vs average loss

### Risk Metrics
- **Sharpe Ratio** - Risk-adjusted return
- **Sortino Ratio** - Downside risk-adjusted return
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Value at Risk (VaR)** - Potential loss at confidence level
- **Calmar Ratio** - Return vs maximum drawdown

### Trade Analytics
- **Trade Duration** - Average time in trades
- **Best/Worst Trades** - Top performers and losers
- **Monthly Performance** - Period-by-period breakdown
- **Pattern Performance** - Success rate by pattern type
- **Time-based Analysis** - Performance by hour/day

## 🚨 Disclaimer

This tool is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Always conduct your own research and consider seeking advice from financial professionals.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

**Itamar Shealtiel**
- GitHub: [@ItamarS3917](https://github.com/ItamarS3917)
- Email: itamarshealtiel1@gmail.com
- LinkedIn: [Itamar Shealtiel](https://linkedin.com/in/itamar-shealtiel)

## 🙏 Acknowledgments

- Inner Circle Trader concepts and methodology
- TradingView for market data
- The Python trading community

---

*Built with ❤️ for algorithmic trading enthusiasts*