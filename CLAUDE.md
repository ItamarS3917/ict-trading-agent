# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ICT Trading Agent is an algorithmic trading analysis tool implementing Inner Circle Trader (ICT) concepts for NASDAQ futures analysis. The system provides pattern detection, market structure analysis, backtesting, and risk management for trading strategies.

**Key Concepts:**
- **Fair Value Gaps (FVGs)**: Price imbalances where gaps between candle highs/lows haven't been filled
- **Order Blocks**: Institutional order zones with specific strength thresholds
- **Market Structure**: Break of Structure (BOS) and Change of Character (CHoCH) patterns
- **Liquidity Pools**: Areas of accumulated orders identified through volume/price analysis

## Development Commands

### Installation
```bash
# Install production dependencies
make install
# OR manually
pip install -r requirements.txt && pip install -e .

# Install development dependencies
make dev
# OR manually
pip install -r requirements-dev.txt && pip install -e .
```

### Testing
```bash
# Run all tests
make test
# OR
pytest tests/ -v

# Run specific test file
pytest tests/test_patterns.py -v
pytest tests/test_risk_manager.py -v
pytest tests/test_data_handler.py -v

# Run with coverage
make coverage
# OR
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html
```

### Code Quality
```bash
# Run linter (check only)
make lint
# OR
ruff check .
ruff format --check .

# Format code (auto-fix)
make format
# OR
ruff check --fix .
ruff format .
```

### Running the Application
```bash
# Interactive Streamlit dashboard (primary interface)
streamlit run src/dashboard.py
# Opens browser at http://localhost:8501

# CLI commands
python src/main.py --analyze --symbol NQ=F
python src/main.py --backtest --symbol NQ=F --start-date 2023-01-01 --end-date 2023-12-31
python src/main.py --signals --symbol NQ=F

# Run examples
python examples/basic_usage.py
python examples/backtest_example.py
python examples/risk_management_example.py
```

### Cleanup
```bash
make clean  # Removes cache files, coverage reports, pytest cache
```

## Architecture

### Core Components

**ICTTradingAgent** (`src/ict_agent.py`)
- Central orchestrator for trading analysis
- Coordinates between DataHandler and PatternDetector
- Implements market structure analysis (BOS, CHoCH detection)
- Generates trading signals based on detected patterns
- Configuration handling with nested section flattening (trading, patterns, risk, data, alerts, backtesting)

**PatternDetector** (`src/pattern_detector.py`)
- Detects Fair Value Gaps (bullish/bearish)
- Identifies Order Blocks with strength scoring
- Locates Liquidity Pools through volume analysis
- Pattern validation and strength calculation

**DataHandler** (`src/data_handler.py`)
- Fetches market data via yfinance API
- Handles data caching in `data/cache/` directory
- Provides both period-based and date-range data retrieval
- Data cleaning and preparation for analysis

**Backtester** (`src/backtester.py`)
- Historical strategy simulation with realistic execution
- Tracks equity curves, positions, and trade-by-trade results
- Calculates performance metrics: Sharpe ratio, win rate, profit factor, max drawdown
- Includes commission and slippage in calculations

**RiskManager** (`src/risk_manager.py`)
- Position sizing calculations (Kelly Criterion, percentage-based)
- Stop loss/take profit calculations (ATR-based and custom)
- Portfolio risk tracking with limits
- Uses dataclass `Position` for trade representation

**PerformanceReporter** (`src/performance_reporter.py`)
- Generates comprehensive performance analytics
- Monthly breakdowns and drawdown analysis
- Trade statistics and pattern performance tracking

### Utilities

**TechnicalIndicators** (`src/utils/indicators.py`)
- 15+ indicators: RSI, MACD, Bollinger Bands, ATR, Ichimoku, SMA, EMA, SuperTrend, Stochastic, ADX, OBV, VWAP, Fibonacci, Pivot Points
- All methods are static and operate on pandas Series/DataFrame

**NotificationSystem** (`src/utils/notifications.py`)
- Multi-channel alerts: webhook (Discord/Slack), email, console
- Signal alerts and trade execution notifications

**ConfigLoader** (`src/utils/config_loader.py`)
- YAML-based configuration management
- Validation and default value handling

**Logger** (`src/utils/logger.py`)
- Rotating file logs with configurable levels
- Logs stored in `logs/` directory

### Data Flow

1. **Market Analysis**:
   - DataHandler fetches OHLCV data → ICTTradingAgent analyzes structure → PatternDetector identifies patterns → Signals generated with strength scores

2. **Backtesting**:
   - Backtester requests historical data → Simulates trades using ICTTradingAgent signals → RiskManager calculates position sizes → PerformanceReporter generates metrics

3. **Configuration**:
   - YAML config loaded → ICTTradingAgent normalizes nested sections → Components receive flattened config

## Configuration System

Configuration lives in `config/config.yaml` (copy from `config/config.example.yaml`). The agent flattens nested sections automatically, so both `config['trading']['symbol']` and `config['symbol']` work.

**Key Configuration Sections:**
- `trading`: symbol, timeframe, lookback_period
- `patterns`: fvg_min_size, orderblock_strength, liquidity_threshold, swing_window
- `risk`: risk_per_trade, max_positions, stop_loss_atr_multiplier, take_profit_ratio
- `data`: primary_source, backup_source, cache_duration
- `alerts`: webhook_url, email settings
- `backtesting`: initial_capital, commission, slippage
- `logging`: level, file path

## Import Conventions

All source modules use relative imports without the `src.` prefix:
```python
from data_handler import DataHandler
from ict_agent import ICTTradingAgent
from pattern_detector import PatternDetector
```

The package is installed in editable mode (`pip install -e .`) which makes the src directory importable.

## Testing Strategy

Tests are organized by module:
- `test_patterns.py`: Pattern detection (FVGs, Order Blocks, Liquidity Pools)
- `test_data_handler.py`: Data fetching and validation
- `test_risk_manager.py`: Risk calculations, position sizing, stop loss/take profit

Coverage focuses on core trading logic. Excluded from coverage: `*/__init__.py` and test files.

## Code Style

- **Linter**: Ruff with pycodestyle, Pyflakes, isort, flake8-bugbear, flake8-comprehensions, pyupgrade
- **Formatter**: Ruff (double quotes, space indentation)
- **Line length**: 100 characters
- **Type hints**: Used throughout with Python 3.9+ syntax (e.g., `list[dict]` not `List[Dict]`)
- **Docstrings**: Google style with Args/Returns sections

## Known Patterns

1. **Config Normalization**: ICTTradingAgent flattens nested config sections. When adding new config sections, update the `sections` list in `_normalize_config()`.

2. **Pattern Strength Calculation**: All patterns have strength scores (1-10) used for signal prioritization. Lower threshold = more signals but lower quality.

3. **Data Caching**: DataHandler caches in `data/cache/`. Manual cache clearing may be needed for stale data.

4. **Signal Generation**: Signals include entry_price, stop_loss, take_profit, strength, and pattern metadata. They're time-stamped for tracking.

5. **Backtest Lookback**: Backtester starts simulation at index 100 to ensure sufficient data for indicator calculations.
