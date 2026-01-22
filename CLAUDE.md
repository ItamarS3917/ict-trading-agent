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

### MCP Server
```bash
# The MCP server is designed to be run by Claude via MCP protocol
# It provides tools for accessing TradingView chart data

# Test MCP server locally (runs in stub mode without authentication)
python -m pytest tests/test_mcp_server.py -v

# For production use with Claude:
# Add to your Claude Desktop MCP settings or use via Claude API
# The server will authenticate with TradingView when configured
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
- Accepts raw DataFrames with optional TradingView drawings for confluence analysis

**DataHandler** (`src/data_handler.py`)
- **DEPRECATED**: Now a backwards-compatible wrapper for `DataUtils`
- Data fetching moved to MCP server integration
- Use `DataUtils` from `src/utils/data_utils.py` for new code

**DataUtils** (`src/utils/data_utils.py`)
- Data cleaning, validation, and caching utilities
- Processes OHLCV data from MCP server or other sources
- ATR and RSI calculation helpers
- Data validation and quality checks

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
- Accepts config dict OR config_file path via ConfigLoader

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

**AgentLogger** (`src/utils/agent_logger.py`)
- Agent-specific logging for Claude, Gemini, Cursor
- Request/response tracking with timing
- Context-aware logging with agent identification

**ConfluenceAnalyzer** (`src/utils/confluence_analyzer.py`)
- Multi-factor confluence scoring for trade setups
- Aligns ICT patterns with TradingView indicators and drawings
- Prioritizes high-probability setups based on confluence score

**DataFreshnessValidator** (`src/utils/data_freshness.py`)
- Validates data is recent (default: < 5 minutes old)
- Prevents stale data from being used in analysis
- Configurable maximum data age

**MCPClient** (`src/utils/mcp_client.py`)
- Parses MCP server responses to pandas DataFrames
- Handles chart data, indicators, and drawings from TradingView

### MCP Integration

**TradingView MCP Server** (`mcp_server/server.py`)
- Provides MCP tools for Claude to access TradingView chart data
- Tools: `get_active_chart`, `get_indicators`, `get_drawings`, `get_watchlist`, `get_alerts`
- Runs in stub mode when TradingView not authenticated (for testing)
- Uses `tradingview-scraper` package for real data

**TradingViewClient** (`mcp_server/tradingview_client.py`)
- Client wrapper for TradingView data access
- Supports both authenticated and stub modes
- Returns structured data for MCP server

**Claude Skills** (`skills/`)
- `analyze-ict-patterns`: Detects FVGs, Order Blocks, and Liquidity Pools from TradingView charts
  - Integrates PatternDetector, ConfluenceAnalyzer, DataFreshnessValidator
  - Returns structured pattern data with confluence scoring and recommendations

### Data Flow

1. **TradingView → Claude Analysis** (MCP-based):
   - TradingView MCP server fetches chart data/indicators/drawings → MCPClient parses to DataFrames → DataFreshnessValidator checks age → PatternDetector identifies patterns → ConfluenceAnalyzer scores setups → Structured recommendations returned

2. **Traditional Market Analysis** (yfinance-based, legacy):
   - DataHandler fetches OHLCV data → ICTTradingAgent analyzes structure → PatternDetector identifies patterns → Signals generated with strength scores

3. **Backtesting**:
   - Backtester requests historical data → Simulates trades using ICTTradingAgent signals → RiskManager calculates position sizes → PerformanceReporter generates metrics

4. **Configuration**:
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
from data_handler import DataHandler  # Legacy - prefer DataUtils
from utils.data_utils import DataUtils  # New approach
from ict_agent import ICTTradingAgent
from pattern_detector import PatternDetector
from utils.confluence_analyzer import ConfluenceAnalyzer
from utils.mcp_client import MCPClient
```

The package is installed in editable mode (`pip install -e .`) which makes the src directory importable.

**Important**: Skills and MCP server add `src/` to `sys.path` for imports since they run outside the package context.

## Testing Strategy

Tests are organized by module:
- `test_patterns.py`: Pattern detection (FVGs, Order Blocks, Liquidity Pools)
- `test_data_handler.py`: Data utilities and validation
- `test_risk_manager.py`: Risk calculations, position sizing, stop loss/take profit
- `test_mcp_server.py`: MCP server tools and TradingView client (9 async tests)
- `test_config_loader.py`: YAML configuration loading and validation

All tests use pytest. MCP server tests are async and use `pytest.mark.asyncio`. Coverage focuses on core trading logic. Excluded from coverage: `*/__init__.py` and test files.

## Code Style

- **Linter**: Ruff with pycodestyle, Pyflakes, isort, flake8-bugbear, flake8-comprehensions, pyupgrade
- **Formatter**: Ruff (double quotes, space indentation)
- **Line length**: 100 characters
- **Type hints**: Used throughout with Python 3.9+ syntax (e.g., `list[dict]` not `List[Dict]`)
- **Docstrings**: Google style with Args/Returns sections

## Known Patterns

1. **Config Normalization**: ICTTradingAgent flattens nested config sections. When adding new config sections, update the `sections` list in `_normalize_config()` (src/ict_agent.py:47).

2. **Pattern Strength Calculation**: All patterns have strength scores (1-10) used for signal prioritization. Lower threshold = more signals but lower quality.

3. **Data Caching**: DataUtils caches in `data/cache/`. Manual cache clearing may be needed for stale data.

4. **Signal Generation**: Signals include entry_price, stop_loss, take_profit, strength, and pattern metadata. They're time-stamped for tracking.

5. **Backtest Lookback**: Backtester starts simulation at index 100 to ensure sufficient data for indicator calculations (src/backtester.py:72).

6. **MCP Stub Mode**: TradingView MCP server runs in stub mode when not authenticated, returning sample data for testing. Check `tradingview-scraper` authentication for real data.

7. **Backwards Compatibility**: DataHandler still exists as a wrapper for legacy code. New code should use DataUtils directly.

8. **Data Freshness**: PatternDetector can validate data age via DataFreshnessValidator. Default max age is 5 minutes for real-time analysis.

9. **Confluence Scoring**: Patterns with confluence score ≥ 2 are considered high-probability setups. Score increases with aligned indicators/drawings.
