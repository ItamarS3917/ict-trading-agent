# 📊 ICT Trading Agent - Algorithmic Trading Analysis Tool

**Automated trading strategy implementation with real-time market analysis using Inner Circle Trader concepts**

## 🎯 Overview

The ICT Trading Agent is an intelligent algorithmic trading analysis tool that implements Inner Circle Trader (ICT) concepts for NASDAQ futures analysis. It provides automated pattern detection, market structure analysis, and trading opportunity alerts.

## 🚀 Features

- 📈 **Trading Algorithm**: Inner Circle Trader (ICT) concept implementation
- 🔍 **Pattern Detection**: Fair Value Gaps (FVGs), Order Blocks, Market Structure analysis
- 📊 **Data Processing**: Real-time NASDAQ futures data processing with NumPy/Pandas
- 🔔 **Notification System**: Automated alerts for trading opportunities
- 🧪 **Backtesting Engine**: Historical data analysis with performance metrics
- 💧 **Liquidity Pool Detection**: Advanced algorithms for identifying liquidity zones
- ⚙️ **Configurable Rule Engine**: Customizable strategy parameters
- 📱 **Interactive Dashboard**: Streamlit-based visualization interface
- 🖥️ **CLI Interface**: Command-line interface for automated analysis

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

## 🎮 Usage

### Interactive Dashboard
```bash
streamlit run src/dashboard.py
```

### Command Line Interface
```bash
# Analyze current market conditions
python src/main.py --analyze

# Run backtesting
python src/main.py --backtest --start-date 2023-01-01 --end-date 2023-12-31

# Generate signals
python src/main.py --signals --symbol NQ=F
```

### Python API
```python
from src.ict_agent import ICTTradingAgent

# Initialize agent
agent = ICTTradingAgent()

# Analyze market structure
analysis = agent.analyze_market_structure("NQ=F")

# Detect Fair Value Gaps
fvgs = agent.detect_fair_value_gaps("NQ=F")

# Get trading signals
signals = agent.generate_signals("NQ=F")
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

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_patterns.py

# Run with coverage
python -m pytest --cov=src tests/
```

## 📈 Performance

The ICT Trading Agent includes comprehensive backtesting capabilities to evaluate strategy performance:

- **Win Rate Analysis**
- **Risk/Reward Ratios**
- **Maximum Drawdown**
- **Sharpe Ratio**
- **Monthly/Yearly Returns**

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