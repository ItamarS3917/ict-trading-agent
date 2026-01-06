# Claude + TradingView Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restructure ICT Trading Agent from Streamlit GUI to Claude conversational interface with TradingView MCP integration.

**Architecture:** Three-layer system - (1) TradingView MCP server for data access, (2) Claude skills wrapping existing Python logic, (3) Refactored core analysis modules (PatternDetector, RiskManager).

**Tech Stack:** Python 3.9+, MCP SDK, TradingView websockets (tvDatafeed approach), YAML configs, pytest

---

## Phase 1: Setup and Dependencies

### Task 1: Install MCP SDK and Update Dependencies

**Files:**
- Modify: `requirements.txt`
- Modify: `requirements-dev.txt`

**Step 1: Add MCP SDK to requirements**

Add to `requirements.txt`:
```
mcp>=1.0.0
tvDatafeed>=2.0.0
websockets>=12.0
```

**Step 2: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully

**Step 3: Verify installation**

Run: `python -c "import mcp; import tvDatafeed; print('MCP and TradingView imports OK')"`
Expected: "MCP and TradingView imports OK"

**Step 4: Commit**

```bash
git add requirements.txt
git commit -m "deps: add MCP SDK and TradingView libraries"
```

---

### Task 2: Create New Configuration Structure

**Files:**
- Create: `config/trading_config.yaml`
- Create: `config/mcp_server_config.yaml`
- Create: `config/skills_config.yaml`
- Create: `config/trading_config.example.yaml`
- Create: `config/mcp_server_config.example.yaml`

**Step 1: Create trading configuration**

Create `config/trading_config.yaml`:
```yaml
# Trading Configuration
account:
  initial_capital: 10000
  currency: "USD"

risk:
  risk_per_trade: 0.02  # 2%
  max_positions: 3
  max_portfolio_risk: 0.06  # 6%
  stop_loss_atr_multiplier: 2
  take_profit_ratio: 2  # 1:2 R:R

patterns:
  fvg_min_size: 0.001
  orderblock_strength: 3
  liquidity_threshold: 0.05
  swing_window: 5
```

**Step 2: Create MCP server configuration**

Create `config/mcp_server_config.yaml`:
```yaml
# TradingView MCP Server Configuration
tradingview:
  username: ""  # Set via environment variable TV_USERNAME
  password: ""  # Set via environment variable TV_PASSWORD

server:
  host: "localhost"
  port: 8080

data:
  default_bars: 500
  cache_duration: 60  # seconds
```

**Step 3: Create skills configuration**

Create `config/skills_config.yaml`:
```yaml
# Claude Skills Configuration
skills:
  analyze-ict-patterns:
    enabled: true
    min_pattern_strength: 5

  calculate-risk:
    enabled: true

  generate-trade-setup:
    enabled: true
    min_confluence_factors: 2

  monitor-workspace:
    enabled: true
    max_symbols: 10
```

**Step 4: Create example configs**

Run:
```bash
cp config/trading_config.yaml config/trading_config.example.yaml
cp config/mcp_server_config.yaml config/mcp_server_config.example.yaml
```

**Step 5: Update .gitignore**

Add to `.gitignore`:
```
config/trading_config.yaml
config/mcp_server_config.yaml
config/skills_config.yaml
```

**Step 6: Commit**

```bash
git add config/*.example.yaml config/skills_config.yaml .gitignore
git commit -m "config: add new configuration structure for MCP and skills"
```

---

## Phase 2: Refactor Existing Code

### Task 3: Refactor PatternDetector to Accept Raw DataFrames

**Files:**
- Modify: `src/pattern_detector.py`
- Modify: `tests/test_patterns.py`

**Step 1: Update test to use raw DataFrame**

Modify `tests/test_patterns.py`:
```python
import pandas as pd
import pytest
from src.pattern_detector import PatternDetector

@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV DataFrame for testing."""
    data = {
        'Open': [100, 102, 101, 103, 105],
        'High': [103, 104, 102, 106, 107],
        'Low': [99, 101, 100, 102, 104],
        'Close': [102, 101, 103, 105, 106],
        'Volume': [1000, 1100, 900, 1200, 1300]
    }
    return pd.DataFrame(data)

def test_pattern_detector_accepts_dataframe(sample_ohlcv_data):
    """Test that PatternDetector can work with raw DataFrame."""
    config = {'fvg_min_size': 0.001}
    detector = PatternDetector(config)

    # Should not raise an error
    fvgs = detector.detect_fair_value_gaps(sample_ohlcv_data)
    assert isinstance(fvgs, list)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_patterns.py::test_pattern_detector_accepts_dataframe -v`
Expected: May pass or fail depending on current implementation

**Step 3: Remove DataHandler dependency from PatternDetector**

Modify `src/pattern_detector.py`:
```python
"""
Pattern Detector Module for ICT Trading Agent

Implements detection algorithms for ICT trading patterns including
Fair Value Gaps, Order Blocks, and Liquidity Pools.
"""

import pandas as pd
from typing import Optional


class PatternDetector:
    """
    Detects ICT trading patterns in market data.
    """

    def __init__(self, config: dict):
        """
        Initialize the PatternDetector.

        Args:
            config: Configuration dictionary with pattern parameters
        """
        self.config = config

    def detect_fair_value_gaps(
        self,
        df: pd.DataFrame,
        drawings: Optional[list] = None
    ) -> list[dict]:
        """
        Detect Fair Value Gaps (FVGs) in price data.

        A Fair Value Gap occurs when there's a gap between the high of one candle
        and the low of another candle that hasn't been filled.

        Args:
            df: OHLCV DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
            drawings: Optional TradingView drawings for confluence analysis

        Returns:
            List of detected FVG patterns
        """
        fvgs = []

        if len(df) < 3:
            return fvgs

        min_gap_size = self.config.get("fvg_min_size", 0.001)

        for i in range(1, len(df) - 1):
            prev_candle = df.iloc[i - 1]
            current_candle = df.iloc[i]
            next_candle = df.iloc[i + 1]

            # Bullish FVG: Gap between previous low and next high
            if (
                prev_candle["Low"] > next_candle["High"]
                and current_candle["Close"] > current_candle["Open"]
            ):
                gap_size = (prev_candle["Low"] - next_candle["High"]) / next_candle["High"]

                if gap_size >= min_gap_size:
                    confluence = self._check_drawing_confluence(
                        prev_candle["Low"], next_candle["High"], drawings
                    ) if drawings else False

                    fvg = {
                        "type": "Fair Value Gap",
                        "direction": "BULLISH",
                        "timestamp": df.index[i] if hasattr(df.index[i], 'isoformat') else str(i),
                        "gap_high": prev_candle["Low"],
                        "gap_low": next_candle["High"],
                        "gap_size": gap_size,
                        "entry_price": next_candle["High"],
                        "stop_loss": prev_candle["Low"] - (prev_candle["Low"] * 0.001),
                        "take_profit": prev_candle["Low"] + (gap_size * prev_candle["Low"] * 2),
                        "strength": self._calculate_fvg_strength(df, i, gap_size),
                        "filled": False,
                        "confluence": confluence,
                    }
                    fvgs.append(fvg)

            # Bearish FVG: Gap between previous high and next low
            elif (
                prev_candle["High"] < next_candle["Low"]
                and current_candle["Close"] < current_candle["Open"]
            ):
                gap_size = (next_candle["Low"] - prev_candle["High"]) / prev_candle["High"]

                if gap_size >= min_gap_size:
                    confluence = self._check_drawing_confluence(
                        next_candle["Low"], prev_candle["High"], drawings
                    ) if drawings else False

                    fvg = {
                        "type": "Fair Value Gap",
                        "direction": "BEARISH",
                        "timestamp": df.index[i] if hasattr(df.index[i], 'isoformat') else str(i),
                        "gap_high": next_candle["Low"],
                        "gap_low": prev_candle["High"],
                        "gap_size": gap_size,
                        "entry_price": next_candle["Low"],
                        "stop_loss": next_candle["Low"] + (next_candle["Low"] * 0.001),
                        "take_profit": next_candle["Low"] - (gap_size * next_candle["Low"] * 2),
                        "strength": self._calculate_fvg_strength(df, i, gap_size),
                        "filled": False,
                        "confluence": confluence,
                    }
                    fvgs.append(fvg)

        return fvgs

    def _check_drawing_confluence(
        self,
        level_high: float,
        level_low: float,
        drawings: Optional[list]
    ) -> bool:
        """
        Check if any TradingView drawings align with the price level.

        Args:
            level_high: Upper price level
            level_low: Lower price level
            drawings: List of TradingView drawing objects

        Returns:
            True if confluence found, False otherwise
        """
        if not drawings:
            return False

        # Check if any trendline, support/resistance intersects with the level
        for drawing in drawings:
            if drawing.get('type') in ['trendline', 'horizontal_line', 'rectangle']:
                # Simplified check - actual implementation would need geometry
                drawing_price = drawing.get('price', 0)
                if level_low <= drawing_price <= level_high:
                    return True

        return False

    # Keep existing _calculate_fvg_strength, detect_order_blocks, detect_liquidity_pools methods...
```

**Step 4: Run tests**

Run: `pytest tests/test_patterns.py -v`
Expected: Tests pass

**Step 5: Commit**

```bash
git add src/pattern_detector.py tests/test_patterns.py
git commit -m "refactor: PatternDetector accepts raw DataFrames with optional drawings"
```

---

### Task 4: Refactor RiskManager for Simplified Configuration

**Files:**
- Modify: `src/risk_manager.py`
- Modify: `tests/test_risk_manager.py`
- Create: `src/utils/config_loader.py`

**Step 1: Create configuration loader utility**

Create `src/utils/config_loader.py`:
```python
"""Configuration loader utility."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict


class ConfigLoader:
    """Loads and manages YAML configuration files."""

    def __init__(self, config_dir: str = "config"):
        """
        Initialize config loader.

        Args:
            config_dir: Directory containing config files
        """
        self.config_dir = Path(config_dir)

    def load(self, filename: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.

        Args:
            filename: Name of config file (e.g., 'trading_config.yaml')

        Returns:
            Configuration dictionary
        """
        config_path = self.config_dir / filename

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Replace environment variables
        config = self._replace_env_vars(config)

        return config

    def _replace_env_vars(self, config: Dict) -> Dict:
        """Replace ${ENV_VAR} patterns with environment variables."""
        if isinstance(config, dict):
            return {k: self._replace_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._replace_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        return config
```

**Step 2: Write test for config loader**

Create `tests/test_config_loader.py`:
```python
"""Tests for configuration loader."""

import pytest
import yaml
from pathlib import Path
from src.utils.config_loader import ConfigLoader


def test_config_loader_loads_yaml(tmp_path):
    """Test that ConfigLoader can load YAML files."""
    # Create temp config file
    config_file = tmp_path / "test_config.yaml"
    config_data = {
        'account': {'capital': 10000},
        'risk': {'risk_per_trade': 0.02}
    }

    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)

    loader = ConfigLoader(config_dir=str(tmp_path))
    loaded_config = loader.load('test_config.yaml')

    assert loaded_config['account']['capital'] == 10000
    assert loaded_config['risk']['risk_per_trade'] == 0.02
```

**Step 3: Run test**

Run: `pytest tests/test_config_loader.py -v`
Expected: PASS

**Step 4: Update RiskManager to use config loader**

Modify `src/risk_manager.py` (keep existing logic, update __init__):
```python
"""
Risk Management Module

Provides comprehensive risk management functionality including
position sizing, portfolio risk, and risk metrics calculation.
"""

import logging
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from utils.config_loader import ConfigLoader


@dataclass
class Position:
    """Represents a trading position."""

    symbol: str
    direction: str  # 'LONG' or 'SHORT'
    entry_price: float
    quantity: int
    stop_loss: float
    take_profit: float
    entry_date: str


class RiskManager:
    """
    Manages risk for trading operations.
    """

    def __init__(self, config: Optional[dict] = None, config_file: Optional[str] = None):
        """
        Initialize the Risk Manager.

        Args:
            config: Configuration dictionary with risk parameters (takes priority)
            config_file: Path to configuration file (e.g., 'trading_config.yaml')
        """
        if config:
            self.config = config
        elif config_file:
            loader = ConfigLoader()
            full_config = loader.load(config_file)
            # Extract risk and account sections
            self.config = {
                **full_config.get('risk', {}),
                **full_config.get('account', {})
            }
        else:
            self.config = self._default_config()

        self.logger = logging.getLogger(__name__)
        self.positions: list[Position] = []

    def _default_config(self) -> dict:
        """Default risk management configuration."""
        return {
            "risk_per_trade": 0.02,  # 2% risk per trade
            "max_positions": 3,
            "max_portfolio_risk": 0.06,  # 6% max total risk
            "max_position_size": 0.3,  # 30% max position size
            "stop_loss_atr_multiplier": 2,
            "take_profit_ratio": 2,  # 1:2 risk/reward
            "max_daily_loss": 0.05,  # 5% max daily loss
            "max_drawdown": 0.20,  # 20% max drawdown
            "initial_capital": 10000,
        }

    # Keep all existing methods: calculate_position_size, calculate_stop_loss, etc.
```

**Step 5: Run tests**

Run: `pytest tests/test_risk_manager.py -v`
Expected: Tests pass

**Step 6: Commit**

```bash
git add src/utils/config_loader.py src/risk_manager.py tests/test_config_loader.py tests/test_risk_manager.py
git commit -m "refactor: RiskManager uses ConfigLoader for YAML configs"
```

---

### Task 5: Convert DataHandler to Data Utils

**Files:**
- Rename: `src/data_handler.py` → `src/utils/data_utils.py`
- Modify: `src/utils/data_utils.py`
- Modify: `tests/test_data_handler.py`

**Step 1: Move and rename file**

Run:
```bash
git mv src/data_handler.py src/utils/data_utils.py
```

**Step 2: Update data_utils to remove yfinance, keep utilities**

Modify `src/utils/data_utils.py`:
```python
"""
Data utilities for ICT Trading Agent.

Provides data cleaning, validation, and caching utilities.
No longer fetches data - data comes from MCP server.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional
import json
from datetime import datetime, timedelta


class DataUtils:
    """
    Data cleaning, validation, and caching utilities.
    """

    def __init__(self, cache_dir: str = "data/cache"):
        """
        Initialize DataUtils.

        Args:
            cache_dir: Directory for data caching
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def clean_ohlcv_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate OHLCV data.

        Args:
            df: DataFrame with OHLCV columns

        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df

        # Ensure required columns exist
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Remove rows with NaN values
        df = df.dropna()

        # Ensure High >= Low
        if (df['High'] < df['Low']).any():
            df = df[df['High'] >= df['Low']]

        # Ensure High >= Open, Close and Low <= Open, Close
        df = df[
            (df['High'] >= df['Open']) &
            (df['High'] >= df['Close']) &
            (df['Low'] <= df['Open']) &
            (df['Low'] <= df['Close'])
        ]

        # Remove duplicate timestamps
        if isinstance(df.index, pd.DatetimeIndex):
            df = df[~df.index.duplicated(keep='first')]

        return df

    def validate_ohlcv_data(self, df: pd.DataFrame) -> bool:
        """
        Validate OHLCV data structure and quality.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        if df.empty:
            return False

        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            return False

        # Check for negative prices or volumes
        if (df[['Open', 'High', 'Low', 'Close', 'Volume']] < 0).any().any():
            return False

        # Check price relationships
        if (df['High'] < df['Low']).any():
            return False

        return True

    def cache_analysis(self, symbol: str, analysis_type: str, data: dict) -> None:
        """
        Cache analysis results.

        Args:
            symbol: Trading symbol
            analysis_type: Type of analysis (e.g., 'patterns', 'signals')
            data: Analysis data to cache
        """
        cache_file = self.cache_dir / f"{symbol}_{analysis_type}_{datetime.now().strftime('%Y%m%d')}.json"

        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'analysis_type': analysis_type,
                'data': data
            }, f, indent=2)

    def load_cached_analysis(
        self,
        symbol: str,
        analysis_type: str,
        max_age_minutes: int = 60
    ) -> Optional[dict]:
        """
        Load cached analysis if not expired.

        Args:
            symbol: Trading symbol
            analysis_type: Type of analysis
            max_age_minutes: Maximum age of cache in minutes

        Returns:
            Cached data or None if not found/expired
        """
        cache_file = self.cache_dir / f"{symbol}_{analysis_type}_{datetime.now().strftime('%Y%m%d')}.json"

        if not cache_file.exists():
            return None

        with open(cache_file, 'r') as f:
            cached = json.load(f)

        # Check if expired
        cached_time = datetime.fromisoformat(cached['timestamp'])
        if datetime.now() - cached_time > timedelta(minutes=max_age_minutes):
            return None

        return cached['data']
```

**Step 3: Update tests**

Modify `tests/test_data_handler.py`:
```python
"""Tests for data utilities."""

import pytest
import pandas as pd
import numpy as np
from src.utils.data_utils import DataUtils


def test_clean_ohlcv_data():
    """Test OHLCV data cleaning."""
    utils = DataUtils()

    # Create sample data with some issues
    data = {
        'Open': [100, 102, np.nan, 103],
        'High': [103, 104, 105, 106],
        'Low': [99, 101, 100, 102],
        'Close': [102, 101, 103, 105],
        'Volume': [1000, 1100, 900, 1200]
    }
    df = pd.DataFrame(data)

    cleaned = utils.clean_ohlcv_data(df)

    # Should remove NaN row
    assert len(cleaned) == 3
    # Should have all required columns
    assert all(col in cleaned.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])


def test_validate_ohlcv_data():
    """Test OHLCV data validation."""
    utils = DataUtils()

    # Valid data
    valid_data = {
        'Open': [100, 102],
        'High': [103, 104],
        'Low': [99, 101],
        'Close': [102, 101],
        'Volume': [1000, 1100]
    }
    assert utils.validate_ohlcv_data(pd.DataFrame(valid_data)) is True

    # Invalid data - High < Low
    invalid_data = {
        'Open': [100, 102],
        'High': [99, 104],  # First High < Low
        'Low': [100, 101],
        'Close': [102, 101],
        'Volume': [1000, 1100]
    }
    assert utils.validate_ohlcv_data(pd.DataFrame(invalid_data)) is False
```

**Step 4: Run tests**

Run: `pytest tests/test_data_handler.py -v`
Expected: Tests pass

**Step 5: Commit**

```bash
git add src/utils/data_utils.py tests/test_data_handler.py
git commit -m "refactor: convert DataHandler to DataUtils, remove yfinance dependency"
```

---

## Phase 3: Build MCP Server

### Task 6: Create Basic MCP Server Structure

**Files:**
- Create: `mcp_server/__init__.py`
- Create: `mcp_server/server.py`
- Create: `mcp_server/tradingview_client.py`
- Create: `tests/test_mcp_server.py`

**Step 1: Create MCP server directory structure**

Run:
```bash
mkdir -p mcp_server
touch mcp_server/__init__.py
```

**Step 2: Create basic MCP server**

Create `mcp_server/server.py`:
```python
"""TradingView MCP Server."""

import asyncio
import logging
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from .tradingview_client import TradingViewClient
from ..src.utils.config_loader import ConfigLoader


logger = logging.getLogger(__name__)


class TradingViewMCPServer:
    """MCP Server for TradingView integration."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("tradingview-mcp-server")
        self.tv_client: Optional[TradingViewClient] = None
        self.config: Dict[str, Any] = {}

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="get_active_chart",
                    description="Get data from the currently active TradingView chart",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bars": {
                                "type": "integer",
                                "description": "Number of bars to fetch (default: 500)",
                                "default": 500
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_indicators",
                    description="Get indicator values from the active chart",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_drawings",
                    description="Get user drawings from the active chart",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_watchlist",
                    description="Get symbols from user's watchlist",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_alerts",
                    description="Get user's active alerts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            if not self.tv_client:
                return [types.TextContent(
                    type="text",
                    text="Error: TradingView client not initialized"
                )]

            try:
                if name == "get_active_chart":
                    result = await self.tv_client.get_active_chart(
                        bars=arguments.get("bars", 500)
                    )
                elif name == "get_indicators":
                    result = await self.tv_client.get_indicators()
                elif name == "get_drawings":
                    result = await self.tv_client.get_drawings()
                elif name == "get_watchlist":
                    result = await self.tv_client.get_watchlist()
                elif name == "get_alerts":
                    result = await self.tv_client.get_alerts()
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: Unknown tool '{name}'"
                    )]

                import json
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]

    async def start(self):
        """Start the MCP server."""
        # Load configuration
        loader = ConfigLoader()
        self.config = loader.load('mcp_server_config.yaml')

        # Initialize TradingView client
        self.tv_client = TradingViewClient(self.config['tradingview'])
        await self.tv_client.connect()

        logger.info("TradingView MCP Server started")

    async def run(self):
        """Run the server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    server = TradingViewMCPServer()
    await server.start()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
```

**Step 3: Create TradingView client stub**

Create `mcp_server/tradingview_client.py`:
```python
"""TradingView client for fetching chart data."""

import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class TradingViewClient:
    """Client for interacting with TradingView."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TradingView client.

        Args:
            config: TradingView configuration (username, password, etc.)
        """
        self.config = config
        self.connected = False

    async def connect(self):
        """Connect to TradingView."""
        # TODO: Implement actual TradingView connection
        # This will use tvDatafeed or websockets
        logger.info("Connecting to TradingView...")
        self.connected = True
        logger.info("Connected to TradingView")

    async def get_active_chart(self, bars: int = 500) -> Dict[str, Any]:
        """
        Get data from the active chart.

        Args:
            bars: Number of bars to fetch

        Returns:
            Chart data with OHLCV, symbol, timeframe
        """
        # TODO: Implement actual chart data fetching
        return {
            "symbol": "NQ=F",
            "timeframe": "1h",
            "bars": [],
            "visible_range": {"start": 0, "end": bars}
        }

    async def get_indicators(self) -> Dict[str, Any]:
        """Get indicator values from the active chart."""
        # TODO: Implement indicator fetching
        return {
            "indicators": {}
        }

    async def get_drawings(self) -> List[Dict[str, Any]]:
        """Get user drawings from the active chart."""
        # TODO: Implement drawings fetching
        return []

    async def get_watchlist(self) -> List[Dict[str, Any]]:
        """Get symbols from user's watchlist."""
        # TODO: Implement watchlist fetching
        return []

    async def get_alerts(self) -> List[Dict[str, Any]]:
        """Get user's active alerts."""
        # TODO: Implement alerts fetching
        return []
```

**Step 4: Write basic test**

Create `tests/test_mcp_server.py`:
```python
"""Tests for MCP server."""

import pytest
from mcp_server.tradingview_client import TradingViewClient


@pytest.mark.asyncio
async def test_tradingview_client_connects():
    """Test that TradingView client can be initialized."""
    config = {'username': 'test', 'password': 'test'}
    client = TradingViewClient(config)

    await client.connect()

    assert client.connected is True
```

**Step 5: Run test**

Run: `pytest tests/test_mcp_server.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add mcp_server/ tests/test_mcp_server.py
git commit -m "feat: create basic MCP server structure with TradingView client stub"
```

---

### Task 7: Implement get_active_chart Tool

**Files:**
- Modify: `mcp_server/tradingview_client.py`
- Modify: `tests/test_mcp_server.py`

**Step 1: Write test for get_active_chart**

Add to `tests/test_mcp_server.py`:
```python
@pytest.mark.asyncio
async def test_get_active_chart_returns_ohlcv():
    """Test that get_active_chart returns OHLCV data."""
    config = {'username': 'test', 'password': 'test'}
    client = TradingViewClient(config)
    await client.connect()

    chart_data = await client.get_active_chart(bars=100)

    assert 'symbol' in chart_data
    assert 'timeframe' in chart_data
    assert 'bars' in chart_data
    assert isinstance(chart_data['bars'], list)
```

**Step 2: Run test to verify it passes with stub**

Run: `pytest tests/test_mcp_server.py::test_get_active_chart_returns_ohlcv -v`
Expected: PASS (stub returns empty structure)

**Step 3: Implement get_active_chart using tvDatafeed**

Modify `mcp_server/tradingview_client.py`:
```python
"""TradingView client for fetching chart data."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import pandas as pd

try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    TvDatafeed = None
    Interval = None


logger = logging.getLogger(__name__)


class TradingViewClient:
    """Client for interacting with TradingView."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize TradingView client.

        Args:
            config: TradingView configuration (username, password, etc.)
        """
        self.config = config
        self.connected = False
        self.tv = None
        self.current_symbol = config.get('default_symbol', 'NASDAQ:NQ1!')
        self.current_interval = Interval.in_1_hour if Interval else None

    async def connect(self):
        """Connect to TradingView."""
        if TvDatafeed is None:
            logger.warning("tvDatafeed not installed, using stub mode")
            self.connected = True
            return

        try:
            username = self.config.get('username')
            password = self.config.get('password')

            logger.info("Connecting to TradingView...")
            self.tv = TvDatafeed(username, password)
            self.connected = True
            logger.info("Connected to TradingView")

        except Exception as e:
            logger.error(f"Failed to connect to TradingView: {e}")
            raise

    async def get_active_chart(self, bars: int = 500) -> Dict[str, Any]:
        """
        Get data from the active chart.

        Args:
            bars: Number of bars to fetch

        Returns:
            Chart data with OHLCV, symbol, timeframe
        """
        if not self.connected:
            raise RuntimeError("Not connected to TradingView")

        # If using stub mode (no tvDatafeed)
        if self.tv is None:
            return self._get_stub_chart_data(bars)

        try:
            # Parse symbol format: exchange:symbol
            parts = self.current_symbol.split(':')
            exchange = parts[0] if len(parts) > 1 else 'NASDAQ'
            symbol = parts[1] if len(parts) > 1 else parts[0]

            # Fetch data
            df = self.tv.get_hist(
                symbol=symbol,
                exchange=exchange,
                interval=self.current_interval,
                n_bars=bars
            )

            if df is None or df.empty:
                logger.warning(f"No data received for {self.current_symbol}")
                return self._get_stub_chart_data(bars)

            # Convert to list of dicts
            bars_data = []
            for idx, row in df.iterrows():
                bars_data.append({
                    'timestamp': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume'])
                })

            return {
                "symbol": self.current_symbol,
                "timeframe": self._interval_to_string(self.current_interval),
                "bars": bars_data,
                "visible_range": {
                    "start": 0,
                    "end": len(bars_data)
                }
            }

        except Exception as e:
            logger.error(f"Error fetching chart data: {e}")
            return self._get_stub_chart_data(bars)

    def _get_stub_chart_data(self, bars: int) -> Dict[str, Any]:
        """Return stub data for testing."""
        return {
            "symbol": self.current_symbol,
            "timeframe": "1h",
            "bars": [],
            "visible_range": {"start": 0, "end": bars}
        }

    def _interval_to_string(self, interval) -> str:
        """Convert Interval enum to string."""
        if interval == Interval.in_1_minute:
            return "1m"
        elif interval == Interval.in_5_minute:
            return "5m"
        elif interval == Interval.in_15_minute:
            return "15m"
        elif interval == Interval.in_1_hour:
            return "1h"
        elif interval == Interval.in_daily:
            return "1d"
        else:
            return "1h"

    # Keep other methods as stubs for now...
```

**Step 4: Run tests**

Run: `pytest tests/test_mcp_server.py -v`
Expected: Tests pass

**Step 5: Commit**

```bash
git add mcp_server/tradingview_client.py tests/test_mcp_server.py
git commit -m "feat: implement get_active_chart with tvDatafeed integration"
```

---

## Phase 4: Create Utility Modules

### Task 8: Create MCP Client Helper

**Files:**
- Create: `src/utils/mcp_client.py`
- Create: `tests/test_mcp_client.py`

**Step 1: Create MCP client helper**

Create `src/utils/mcp_client.py`:
```python
"""MCP client helper for Claude skills."""

import json
from typing import Any, Dict, List, Optional
import pandas as pd


class MCPClient:
    """Helper for calling MCP tools from Claude skills."""

    @staticmethod
    def parse_chart_data(chart_json: str) -> pd.DataFrame:
        """
        Parse chart data from MCP response to DataFrame.

        Args:
            chart_json: JSON string from get_active_chart tool

        Returns:
            DataFrame with OHLCV data
        """
        data = json.loads(chart_json)

        if not data.get('bars'):
            return pd.DataFrame()

        # Convert bars to DataFrame
        df = pd.DataFrame(data['bars'])

        # Set timestamp as index
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')

        # Rename columns to match expected format
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })

        return df

    @staticmethod
    def parse_indicators(indicators_json: str) -> Dict[str, Any]:
        """
        Parse indicators from MCP response.

        Args:
            indicators_json: JSON string from get_indicators tool

        Returns:
            Dictionary of indicator values
        """
        data = json.loads(indicators_json)
        return data.get('indicators', {})

    @staticmethod
    def parse_drawings(drawings_json: str) -> List[Dict[str, Any]]:
        """
        Parse drawings from MCP response.

        Args:
            drawings_json: JSON string from get_drawings tool

        Returns:
            List of drawing objects
        """
        return json.loads(drawings_json)

    @staticmethod
    def parse_watchlist(watchlist_json: str) -> List[str]:
        """
        Parse watchlist from MCP response.

        Args:
            watchlist_json: JSON string from get_watchlist tool

        Returns:
            List of symbols
        """
        data = json.loads(watchlist_json)
        return [item['symbol'] for item in data if 'symbol' in item]
```

**Step 2: Write tests**

Create `tests/test_mcp_client.py`:
```python
"""Tests for MCP client helper."""

import json
import pytest
import pandas as pd
from src.utils.mcp_client import MCPClient


def test_parse_chart_data():
    """Test parsing chart data from MCP response."""
    chart_json = json.dumps({
        'symbol': 'NQ=F',
        'timeframe': '1h',
        'bars': [
            {'timestamp': '2024-01-01T10:00:00', 'open': 100, 'high': 102, 'low': 99, 'close': 101, 'volume': 1000},
            {'timestamp': '2024-01-01T11:00:00', 'open': 101, 'high': 103, 'low': 100, 'close': 102, 'volume': 1100}
        ]
    })

    df = MCPClient.parse_chart_data(chart_json)

    assert len(df) == 2
    assert 'Open' in df.columns
    assert 'High' in df.columns
    assert df.iloc[0]['Open'] == 100
    assert df.iloc[1]['Close'] == 102


def test_parse_indicators():
    """Test parsing indicators from MCP response."""
    indicators_json = json.dumps({
        'indicators': {
            'RSI_14': 67.3,
            'MACD': {'value': 1.5, 'signal': 1.2}
        }
    })

    indicators = MCPClient.parse_indicators(indicators_json)

    assert indicators['RSI_14'] == 67.3
    assert indicators['MACD']['value'] == 1.5
```

**Step 3: Run tests**

Run: `pytest tests/test_mcp_client.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add src/utils/mcp_client.py tests/test_mcp_client.py
git commit -m "feat: create MCP client helper for parsing tool responses"
```

---

### Task 9: Create Agent Logger

**Files:**
- Create: `src/utils/agent_logger.py`
- Create: `config/logging_config.yaml`
- Create: `tests/test_agent_logger.py`

**Step 1: Create logging configuration**

Create `config/logging_config.yaml`:
```yaml
# Agent Logging Configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

  agents:
    claude:
      enabled: true
      log_dir: "logs/claude"
      retention_days: 30

    gemini:
      enabled: true
      log_dir: "logs/gemini"
      retention_days: 30

    cursor:
      enabled: true
      log_dir: "logs/cursor"
      retention_days: 30

  mcp_server:
    enabled: true
    log_dir: "logs/mcp_server"
    retention_days: 30
```

**Step 2: Write test for agent logger**

Create `tests/test_agent_logger.py`:
```python
"""Tests for agent logger."""

import pytest
from pathlib import Path
from src.utils.agent_logger import AgentLogger


def test_agent_logger_creates_log_file(tmp_path):
    """Test that AgentLogger creates agent-specific log files."""
    log_dir = tmp_path / "logs"
    logger = AgentLogger(agent_name="claude", log_dir=str(log_dir))

    logger.log_request("analyze_patterns", {"symbol": "NQ=F"})

    # Check log file exists
    claude_log_dir = log_dir / "claude"
    assert claude_log_dir.exists()

    # Check log file created
    log_files = list(claude_log_dir.glob("*.log"))
    assert len(log_files) > 0


def test_agent_logger_logs_analysis(tmp_path):
    """Test that AgentLogger logs analysis results."""
    log_dir = tmp_path / "logs"
    logger = AgentLogger(agent_name="claude", log_dir=str(log_dir))

    analysis_result = {
        "patterns_found": 3,
        "execution_time": 1.23
    }

    logger.log_analysis("analyze_patterns", analysis_result)

    # Verify log contains entry
    log_file = list((log_dir / "claude").glob("*.log"))[0]
    content = log_file.read_text()
    assert "analyze_patterns" in content
    assert "patterns_found" in content
```

**Step 3: Run test to verify it fails**

Run: `pytest tests/test_agent_logger.py -v`
Expected: FAIL (module doesn't exist)

**Step 4: Implement agent logger**

Create `src/utils/agent_logger.py`:
```python
"""Agent-specific logging system."""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler


class AgentLogger:
    """
    Logging system for tracking agent interactions.

    Each agent (Claude, Gemini, Cursor) gets its own log directory
    with daily rotating log files.
    """

    def __init__(
        self,
        agent_name: str,
        log_dir: str = "logs",
        retention_days: int = 30,
        level: str = "INFO"
    ):
        """
        Initialize agent logger.

        Args:
            agent_name: Name of the agent (e.g., 'claude', 'gemini', 'cursor')
            log_dir: Base directory for logs
            retention_days: Number of days to retain logs
            level: Logging level
        """
        self.agent_name = agent_name.lower()
        self.log_dir = Path(log_dir) / self.agent_name
        self.retention_days = retention_days

        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = self._setup_logger(level)

        # Clean old logs
        self._cleanup_old_logs()

    def _setup_logger(self, level: str) -> logging.Logger:
        """Setup logger with rotating file handler."""
        logger = logging.getLogger(f"agent.{self.agent_name}")
        logger.setLevel(getattr(logging, level.upper()))

        # Remove existing handlers
        logger.handlers = []

        # Create log file with date
        log_file = self.log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

        # File handler with rotation (10MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    def log_request(self, skill_name: str, parameters: Dict[str, Any]) -> None:
        """
        Log an agent request.

        Args:
            skill_name: Name of the skill being called
            parameters: Request parameters
        """
        self.logger.info(
            f"REQUEST | Skill: {skill_name} | Params: {json.dumps(parameters)}"
        )

    def log_analysis(
        self,
        skill_name: str,
        result: Dict[str, Any],
        execution_time: Optional[float] = None
    ) -> None:
        """
        Log analysis results.

        Args:
            skill_name: Name of the skill
            result: Analysis result dictionary
            execution_time: Execution time in seconds
        """
        log_data = {
            "skill": skill_name,
            "result_summary": self._summarize_result(result),
            "execution_time": execution_time
        }

        self.logger.info(
            f"ANALYSIS | {json.dumps(log_data)}"
        )

    def log_error(
        self,
        skill_name: str,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error.

        Args:
            skill_name: Name of the skill where error occurred
            error: Exception object
            context: Additional context
        """
        error_data = {
            "skill": skill_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }

        self.logger.error(
            f"ERROR | {json.dumps(error_data)}",
            exc_info=True
        )

    def log_data_fetch(
        self,
        source: str,
        symbol: str,
        bars: int,
        timestamp: datetime
    ) -> None:
        """
        Log data fetch operations.

        Args:
            source: Data source (e.g., 'tradingview', 'mcp')
            symbol: Trading symbol
            bars: Number of bars fetched
            timestamp: Data timestamp
        """
        fetch_data = {
            "source": source,
            "symbol": symbol,
            "bars": bars,
            "data_timestamp": timestamp.isoformat(),
            "age_seconds": (datetime.now() - timestamp).total_seconds()
        }

        self.logger.info(
            f"DATA_FETCH | {json.dumps(fetch_data)}"
        )

    def _summarize_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of analysis results for logging."""
        summary = {}

        if "patterns_found" in result:
            summary["patterns_found"] = result["patterns_found"]

        if "fair_value_gaps" in result:
            summary["fvg_count"] = len(result["fair_value_gaps"])

        if "order_blocks" in result:
            summary["ob_count"] = len(result["order_blocks"])

        if "error" in result:
            summary["error"] = result["error"]

        return summary

    def _cleanup_old_logs(self) -> None:
        """Remove log files older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob("*.log*"):
            try:
                # Parse date from filename (YYYY-MM-DD.log)
                date_str = log_file.stem.split('.')[0]
                file_date = datetime.strptime(date_str, '%Y-%m-%d')

                if file_date < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file.name}")
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                continue


def get_agent_logger(agent_name: str) -> AgentLogger:
    """
    Get or create an agent logger.

    Args:
        agent_name: Name of the agent

    Returns:
        AgentLogger instance
    """
    # Load config if available
    try:
        from .config_loader import ConfigLoader
        loader = ConfigLoader()
        config = loader.load('logging_config.yaml')

        agent_config = config.get('logging', {}).get('agents', {}).get(agent_name, {})

        return AgentLogger(
            agent_name=agent_name,
            log_dir=agent_config.get('log_dir', f'logs/{agent_name}'),
            retention_days=agent_config.get('retention_days', 30),
            level=config.get('logging', {}).get('level', 'INFO')
        )
    except Exception:
        # Fallback to defaults if config not available
        return AgentLogger(agent_name=agent_name)
```

**Step 5: Run tests**

Run: `pytest tests/test_agent_logger.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add src/utils/agent_logger.py config/logging_config.yaml tests/test_agent_logger.py
git commit -m "feat: create agent-specific logging system for Claude, Gemini, Cursor"
```

---

### Task 10: Add Data Freshness Validation to MCP Client

**Files:**
- Modify: `src/utils/mcp_client.py`
- Modify: `tests/test_mcp_client.py`

**Step 1: Write test for data freshness validation**

Add to `tests/test_mcp_client.py`:
```python
from datetime import datetime, timedelta


def test_validate_data_freshness_accepts_recent_data():
    """Test that recent data passes freshness validation."""
    chart_json = json.dumps({
        'symbol': 'NQ=F',
        'bars': [
            {
                'timestamp': datetime.now().isoformat(),
                'open': 100, 'high': 102, 'low': 99, 'close': 101, 'volume': 1000
            }
        ]
    })

    is_fresh = MCPClient.validate_data_freshness(chart_json, max_age_minutes=5)
    assert is_fresh is True


def test_validate_data_freshness_rejects_stale_data():
    """Test that old data fails freshness validation."""
    old_time = datetime.now() - timedelta(minutes=10)
    chart_json = json.dumps({
        'symbol': 'NQ=F',
        'bars': [
            {
                'timestamp': old_time.isoformat(),
                'open': 100, 'high': 102, 'low': 99, 'close': 101, 'volume': 1000
            }
        ]
    })

    is_fresh = MCPClient.validate_data_freshness(chart_json, max_age_minutes=5)
    assert is_fresh is False
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_mcp_client.py::test_validate_data_freshness_accepts_recent_data -v`
Expected: FAIL (method doesn't exist)

**Step 3: Add data freshness validation to MCPClient**

Modify `src/utils/mcp_client.py`:
```python
"""MCP client helper for Claude skills."""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd


class MCPClient:
    """Helper for calling MCP tools from Claude skills."""

    @staticmethod
    def parse_chart_data(chart_json: str) -> pd.DataFrame:
        """
        Parse chart data from MCP response to DataFrame.

        Args:
            chart_json: JSON string from get_active_chart tool

        Returns:
            DataFrame with OHLCV data
        """
        data = json.loads(chart_json)

        if not data.get('bars'):
            return pd.DataFrame()

        # Convert bars to DataFrame
        df = pd.DataFrame(data['bars'])

        # Set timestamp as index
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')

        # Rename columns to match expected format
        df = df.rename(columns={
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })

        return df

    @staticmethod
    def validate_data_freshness(
        chart_json: str,
        max_age_minutes: int = 5
    ) -> bool:
        """
        Validate that chart data is recent enough for analysis.

        Args:
            chart_json: JSON string from get_active_chart tool
            max_age_minutes: Maximum acceptable age in minutes

        Returns:
            True if data is fresh, False otherwise
        """
        try:
            data = json.loads(chart_json)
            bars = data.get('bars', [])

            if not bars:
                return False

            # Get the most recent bar timestamp
            last_bar = bars[-1]
            last_timestamp = pd.to_datetime(last_bar['timestamp'])

            # Calculate age
            now = datetime.now()
            if last_timestamp.tzinfo:
                # If timestamp is timezone-aware, make now timezone-aware too
                import pytz
                now = now.replace(tzinfo=pytz.UTC)

            age = now - last_timestamp
            max_age = timedelta(minutes=max_age_minutes)

            return age <= max_age

        except (KeyError, ValueError, TypeError) as e:
            # If we can't parse timestamp, consider data invalid
            return False

    @staticmethod
    def get_data_age(chart_json: str) -> Optional[timedelta]:
        """
        Get the age of the chart data.

        Args:
            chart_json: JSON string from get_active_chart tool

        Returns:
            Timedelta representing data age, or None if unable to determine
        """
        try:
            data = json.loads(chart_json)
            bars = data.get('bars', [])

            if not bars:
                return None

            last_bar = bars[-1]
            last_timestamp = pd.to_datetime(last_bar['timestamp'])

            now = datetime.now()
            if last_timestamp.tzinfo:
                import pytz
                now = now.replace(tzinfo=pytz.UTC)

            return now - last_timestamp

        except (KeyError, ValueError, TypeError):
            return None

    @staticmethod
    def parse_indicators(indicators_json: str) -> Dict[str, Any]:
        """
        Parse indicators from MCP response.

        Args:
            indicators_json: JSON string from get_indicators tool

        Returns:
            Dictionary of indicator values
        """
        data = json.loads(indicators_json)
        return data.get('indicators', {})

    @staticmethod
    def parse_drawings(drawings_json: str) -> List[Dict[str, Any]]:
        """
        Parse drawings from MCP response.

        Args:
            drawings_json: JSON string from get_drawings tool

        Returns:
            List of drawing objects
        """
        return json.loads(drawings_json)

    @staticmethod
    def parse_watchlist(watchlist_json: str) -> List[str]:
        """
        Parse watchlist from MCP response.

        Args:
            watchlist_json: JSON string from get_watchlist tool

        Returns:
            List of symbols
        """
        data = json.loads(watchlist_json)
        return [item['symbol'] for item in data if 'symbol' in item]
```

**Step 4: Run tests**

Run: `pytest tests/test_mcp_client.py -v`
Expected: PASS

**Step 5: Update skills to validate data freshness**

Modify `skills/analyze-ict-patterns/analyze.py` to add validation:
```python
def analyze_patterns(chart_data_json: str) -> dict:
    """
    Analyze ICT patterns from chart data.

    Args:
        chart_data_json: JSON string from get_active_chart MCP tool

    Returns:
        Dictionary with detected patterns
    """
    # Validate data freshness FIRST
    if not MCPClient.validate_data_freshness(chart_data_json, max_age_minutes=5):
        data_age = MCPClient.get_data_age(chart_data_json)
        age_str = f"{data_age.total_seconds() / 60:.1f} minutes" if data_age else "unknown"
        return {
            "error": f"Data is stale (age: {age_str}). Please refresh your chart.",
            "stale_data": True
        }

    # Parse chart data
    df = MCPClient.parse_chart_data(chart_data_json)

    if df.empty:
        return {"error": "No chart data available"}

    # ... rest of existing code ...
```

**Step 6: Commit**

```bash
git add src/utils/mcp_client.py tests/test_mcp_client.py skills/analyze-ict-patterns/analyze.py
git commit -m "feat: add data freshness validation before analysis"
```

---

### Task 11: Create Confluence Analyzer

**Files:**
- Create: `src/utils/confluence_analyzer.py`
- Create: `tests/test_confluence_analyzer.py`

**Step 1: Write test for confluence analyzer**

Create `tests/test_confluence_analyzer.py`:
```python
"""Tests for confluence analyzer."""

import pytest
from src.utils.confluence_analyzer import ConfluenceAnalyzer


def test_confluence_analyzer_scores_patterns():
    """Test that confluence analyzer scores patterns with multiple factors."""
    analyzer = ConfluenceAnalyzer()

    pattern = {
        'type': 'Fair Value Gap',
        'direction': 'BULLISH',
        'gap_high': 15420,
        'gap_low': 15400,
        'strength': 8
    }

    indicators = {
        'RSI_14': 35,  # Oversold
        'MACD': {'value': -1.5, 'signal': -1.2}  # Bullish crossover
    }

    drawings = [
        {'type': 'trendline', 'price': 15410, 'direction': 'support'},
        {'type': 'horizontal_line', 'price': 15405}
    ]

    score = analyzer.calculate_confluence_score(pattern, indicators, drawings)

    assert score > 0
    assert isinstance(score, (int, float))
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_confluence_analyzer.py -v`
Expected: FAIL (module doesn't exist)

**Step 3: Implement confluence analyzer**

Create `src/utils/confluence_analyzer.py`:
```python
"""Confluence analyzer for ICT patterns."""

from typing import Any, Dict, List, Optional


class ConfluenceAnalyzer:
    """Analyzes confluence between ICT patterns and TradingView context."""

    def calculate_confluence_score(
        self,
        pattern: Dict[str, Any],
        indicators: Dict[str, Any],
        drawings: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confluence score for a pattern.

        Args:
            pattern: Detected ICT pattern
            indicators: TradingView indicator values
            drawings: TradingView user drawings

        Returns:
            Confluence score (0-10)
        """
        score = float(pattern.get('strength', 5))
        confluence_count = 0

        # Check indicator confluence
        indicator_score = self._check_indicator_confluence(pattern, indicators)
        if indicator_score > 0:
            score += indicator_score
            confluence_count += 1

        # Check drawing confluence
        drawing_score = self._check_drawing_confluence(pattern, drawings)
        if drawing_score > 0:
            score += drawing_score
            confluence_count += 1

        # Boost score if multiple factors align
        if confluence_count >= 2:
            score *= 1.2

        return min(score, 10.0)

    def _check_indicator_confluence(
        self,
        pattern: Dict[str, Any],
        indicators: Dict[str, Any]
    ) -> float:
        """Check if indicators support the pattern direction."""
        score = 0.0
        direction = pattern.get('direction', '')

        # RSI confluence
        if 'RSI_14' in indicators:
            rsi = indicators['RSI_14']
            if direction == 'BULLISH' and rsi < 40:
                score += 1.0  # Oversold supports bullish
            elif direction == 'BEARISH' and rsi > 60:
                score += 1.0  # Overbought supports bearish

        # MACD confluence
        if 'MACD' in indicators:
            macd = indicators['MACD']
            if isinstance(macd, dict):
                value = macd.get('value', 0)
                signal = macd.get('signal', 0)

                if direction == 'BULLISH' and value > signal:
                    score += 1.0  # Bullish crossover
                elif direction == 'BEARISH' and value < signal:
                    score += 1.0  # Bearish crossover

        return score

    def _check_drawing_confluence(
        self,
        pattern: Dict[str, Any],
        drawings: List[Dict[str, Any]]
    ) -> float:
        """Check if user drawings align with the pattern."""
        score = 0.0

        # Get pattern price levels
        pattern_high = pattern.get('gap_high', pattern.get('entry_price', 0))
        pattern_low = pattern.get('gap_low', pattern.get('stop_loss', 0))

        if pattern_high == 0 or pattern_low == 0:
            return score

        # Check if any drawing aligns with pattern levels
        for drawing in drawings:
            drawing_price = drawing.get('price', 0)

            if drawing_price == 0:
                continue

            # Check if drawing is within pattern zone
            if pattern_low <= drawing_price <= pattern_high:
                drawing_type = drawing.get('type', '')

                # Stronger confluence for support/resistance
                if drawing_type in ['horizontal_line', 'trendline']:
                    score += 1.5
                else:
                    score += 0.5

        return score

    def get_confluence_factors(
        self,
        pattern: Dict[str, Any],
        indicators: Dict[str, Any],
        drawings: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Get list of confluence factors that support the pattern.

        Args:
            pattern: Detected ICT pattern
            indicators: TradingView indicator values
            drawings: TradingView user drawings

        Returns:
            List of confluence factor descriptions
        """
        factors = []
        direction = pattern.get('direction', '')

        # Check indicators
        if 'RSI_14' in indicators:
            rsi = indicators['RSI_14']
            if direction == 'BULLISH' and rsi < 40:
                factors.append(f"RSI oversold ({rsi:.1f})")
            elif direction == 'BEARISH' and rsi > 60:
                factors.append(f"RSI overbought ({rsi:.1f})")

        if 'MACD' in indicators and isinstance(indicators['MACD'], dict):
            macd = indicators['MACD']
            value = macd.get('value', 0)
            signal = macd.get('signal', 0)

            if direction == 'BULLISH' and value > signal:
                factors.append("MACD bullish crossover")
            elif direction == 'BEARISH' and value < signal:
                factors.append("MACD bearish crossover")

        # Check drawings
        pattern_high = pattern.get('gap_high', pattern.get('entry_price', 0))
        pattern_low = pattern.get('gap_low', pattern.get('stop_loss', 0))

        for drawing in drawings:
            drawing_price = drawing.get('price', 0)
            if pattern_low <= drawing_price <= pattern_high:
                drawing_type = drawing.get('type', 'drawing')
                factors.append(f"{drawing_type} at {drawing_price:.2f}")

        return factors
```

**Step 4: Run tests**

Run: `pytest tests/test_confluence_analyzer.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/utils/confluence_analyzer.py tests/test_confluence_analyzer.py
git commit -m "feat: create confluence analyzer for ICT patterns"
```

---

## Phase 5: Build Claude Skills

### Task 10: Create analyze-ict-patterns Skill

**Files:**
- Create: `skills/analyze-ict-patterns/skill.md`
- Create: `skills/analyze-ict-patterns/analyze.py`

**Step 1: Create skills directory**

Run:
```bash
mkdir -p skills/analyze-ict-patterns
```

**Step 2: Create skill definition**

Create `skills/analyze-ict-patterns/skill.md`:
```markdown
---
name: analyze-ict-patterns
description: Analyze TradingView charts for ICT patterns (Fair Value Gaps, Order Blocks, Liquidity Pools)
---

# Analyze ICT Patterns

Use this skill when the user asks to analyze their TradingView chart for ICT (Inner Circle Trader) patterns.

## What This Skill Does

1. Fetches the active TradingView chart using MCP `get_active_chart` tool
2. Runs pattern detection algorithms (FVG, Order Blocks, Liquidity Pools)
3. Returns pattern locations, strength scores, and entry/exit levels

## When to Use

- User asks: "Analyze my chart for ICT patterns"
- User asks: "Find Fair Value Gaps"
- User asks: "Show me order blocks"
- User asks: "Are there any ICT setups?"

## How to Use

Call the Python script `analyze.py` which will:
- Connect to MCP server
- Fetch chart data
- Run PatternDetector
- Format results for the user

## Output Format

Return natural language summary plus structured data:
- Pattern type (FVG, Order Block, Liquidity Pool)
- Direction (BULLISH/BEARISH)
- Price levels (entry, stop loss, take profit)
- Strength score (1-10)
```

**Step 3: Create skill implementation**

Create `skills/analyze-ict-patterns/analyze.py`:
```python
#!/usr/bin/env python3
"""Analyze ICT patterns skill implementation."""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pattern_detector import PatternDetector
from utils.mcp_client import MCPClient
from utils.config_loader import ConfigLoader


def analyze_patterns(chart_data_json: str) -> dict:
    """
    Analyze ICT patterns from chart data.

    Args:
        chart_data_json: JSON string from get_active_chart MCP tool

    Returns:
        Dictionary with detected patterns
    """
    # Parse chart data
    df = MCPClient.parse_chart_data(chart_data_json)

    if df.empty:
        return {"error": "No chart data available"}

    # Load configuration
    loader = ConfigLoader()
    config = loader.load('trading_config.yaml')

    # Initialize pattern detector
    detector = PatternDetector(config.get('patterns', {}))

    # Detect patterns
    fvgs = detector.detect_fair_value_gaps(df)
    order_blocks = detector.detect_order_blocks(df) if hasattr(detector, 'detect_order_blocks') else []
    liquidity_pools = detector.detect_liquidity_pools(df) if hasattr(detector, 'detect_liquidity_pools') else []

    # Format results
    result = {
        "symbol": json.loads(chart_data_json).get("symbol", "Unknown"),
        "patterns_found": len(fvgs) + len(order_blocks) + len(liquidity_pools),
        "fair_value_gaps": fvgs,
        "order_blocks": order_blocks,
        "liquidity_pools": liquidity_pools
    }

    return result


def format_output(analysis: dict) -> str:
    """Format analysis results for user-friendly output."""
    if "error" in analysis:
        return f"Error: {analysis['error']}"

    output = []
    output.append(f"\n📊 ICT Pattern Analysis for {analysis['symbol']}")
    output.append(f"Found {analysis['patterns_found']} patterns total\n")

    # Fair Value Gaps
    fvgs = analysis['fair_value_gaps']
    if fvgs:
        output.append(f"📈 Fair Value Gaps ({len(fvgs)}):")
        for i, fvg in enumerate(fvgs[:5], 1):  # Show top 5
            output.append(
                f"  {i}. {fvg['direction']} FVG at {fvg['gap_low']:.2f}-{fvg['gap_high']:.2f} "
                f"(Strength: {fvg['strength']}/10)"
            )
        if len(fvgs) > 5:
            output.append(f"  ... and {len(fvgs) - 5} more")
        output.append("")

    # Order Blocks
    order_blocks = analysis['order_blocks']
    if order_blocks:
        output.append(f"🟦 Order Blocks ({len(order_blocks)}):")
        for i, ob in enumerate(order_blocks[:5], 1):
            output.append(
                f"  {i}. {ob['direction']} Order Block at {ob.get('price', 'N/A')} "
                f"(Strength: {ob.get('strength', 0)}/10)"
            )
        if len(order_blocks) > 5:
            output.append(f"  ... and {len(order_blocks) - 5} more")
        output.append("")

    # Liquidity Pools
    liquidity_pools = analysis['liquidity_pools']
    if liquidity_pools:
        output.append(f"💧 Liquidity Pools ({len(liquidity_pools)}):")
        for i, lp in enumerate(liquidity_pools[:5], 1):
            output.append(
                f"  {i}. {lp.get('type', 'Unknown')} at {lp.get('price', 'N/A')}"
            )
        if len(liquidity_pools) > 5:
            output.append(f"  ... and {len(liquidity_pools) - 5} more")

    if not fvgs and not order_blocks and not liquidity_pools:
        output.append("No clear ICT patterns detected at this time.")

    return "\n".join(output)


if __name__ == "__main__":
    # Expect chart data JSON as first argument
    if len(sys.argv) < 2:
        print("Usage: python analyze.py '<chart_data_json>'")
        sys.exit(1)

    chart_data = sys.argv[1]
    analysis = analyze_patterns(chart_data)

    # Print formatted output
    print(format_output(analysis))

    # Also print JSON for Claude to parse
    print("\n---JSON---")
    print(json.dumps(analysis, indent=2))
```

**Step 4: Make script executable**

Run:
```bash
chmod +x skills/analyze-ict-patterns/analyze.py
```

**Step 5: Commit**

```bash
git add skills/analyze-ict-patterns/
git commit -m "feat: create analyze-ict-patterns Claude skill"
```

---

## Phase 6: Cleanup and Documentation

### Task 11: Delete Old Files

**Files:**
- Delete: `src/dashboard.py`
- Delete: `src/main.py`
- Delete: `src/backtester.py`
- Delete: `src/performance_reporter.py`

**Step 1: Remove old files**

Run:
```bash
git rm src/dashboard.py src/main.py src/backtester.py src/performance_reporter.py
```

**Step 2: Update imports in remaining files**

Check for any imports of deleted modules:
```bash
grep -r "from dashboard\|from main\|from backtester\|from performance_reporter" src/
```

Remove any found imports.

**Step 3: Commit**

```bash
git commit -m "cleanup: remove Streamlit dashboard, CLI, and backtester"
```

---

### Task 12: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update CLAUDE.md with new architecture**

Modify `CLAUDE.md`:
```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ICT Trading Agent is a Claude-powered trading analysis tool implementing Inner Circle Trader (ICT) concepts. Users interact with Claude naturally to analyze their TradingView charts, detect patterns, and receive trade recommendations.

**Architecture:** Three-layer system
1. **TradingView MCP Server** - Fetches chart data, indicators, drawings from TradingView
2. **Claude Skills** - Wrap Python analysis logic, callable by Claude
3. **Core Analysis Logic** - PatternDetector, RiskManager, technical indicators

**Key Concepts:**
- **Fair Value Gaps (FVGs)**: Price imbalances where gaps between candle highs/lows haven't been filled
- **Order Blocks**: Institutional order zones with specific strength thresholds
- **Market Structure**: Break of Structure (BOS) and Change of Character (CHoCH) patterns
- **Liquidity Pools**: Areas of accumulated orders identified through volume/price analysis

## Development Commands

### Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### Running MCP Server
```bash
# Start TradingView MCP server
python mcp_server/server.py

# Configure TradingView credentials
export TV_USERNAME="your_username"
export TV_PASSWORD="your_password"
```

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_patterns.py -v
pytest tests/test_mcp_server.py -v

# Run with coverage
pytest tests/ -v --cov=src --cov=mcp_server --cov-report=term-missing
```

### Code Quality
```bash
# Linter
ruff check .

# Formatter
ruff format .
```

## Architecture

### MCP Server (`mcp_server/`)

**TradingViewMCPServer** (`server.py`)
- Registers 5 MCP tools: get_active_chart, get_indicators, get_drawings, get_watchlist, get_alerts
- Handles tool calls from Claude
- Returns JSON responses

**TradingViewClient** (`tradingview_client.py`)
- Connects to TradingView via tvDatafeed websockets
- Fetches OHLCV data, indicators, user drawings
- Fallback to stub mode if connection fails

### Claude Skills (`skills/`)

**analyze-ict-patterns**
- Calls get_active_chart MCP tool
- Runs PatternDetector on DataFrame
- Returns FVGs, Order Blocks, Liquidity Pools with strength scores

**calculate-risk** (TODO)
- Position sizing and risk calculations
- Uses RiskManager module

**generate-trade-setup** (TODO)
- Complete trade plans with confluence analysis
- Combines patterns + indicators + drawings

**monitor-workspace** (TODO)
- Multi-symbol scanning
- Prioritizes opportunities by strength

### Core Modules (`src/`)

**PatternDetector** (`pattern_detector.py`)
- Accepts raw DataFrames (from MCP)
- Optional `drawings` parameter for confluence
- Methods: detect_fair_value_gaps(), detect_order_blocks(), detect_liquidity_pools()

**RiskManager** (`risk_manager.py`)
- Loads config from trading_config.yaml
- Position sizing: calculate_position_size()
- Stop loss/TP: calculate_stop_loss(), calculate_take_profit()

**Utilities** (`src/utils/`)
- `config_loader.py` - YAML config loading with env var replacement
- `mcp_client.py` - Parse MCP tool responses to DataFrames
- `confluence_analyzer.py` - Score patterns with indicators/drawings
- `data_utils.py` - Data cleaning, validation, caching
- `indicators.py` - 15+ technical indicators (backup for TradingView indicators)

## Configuration

**config/trading_config.yaml**
- Account capital and risk parameters
- Pattern detection thresholds
- Risk management settings

**config/mcp_server_config.yaml**
- TradingView credentials (use env vars: TV_USERNAME, TV_PASSWORD)
- Server host/port
- Data fetch settings

**config/skills_config.yaml**
- Enable/disable specific skills
- Skill-specific parameters

## User Interaction Flow

1. User asks Claude: "Analyze my NQ chart for ICT patterns"
2. Claude invokes `analyze-ict-patterns` skill
3. Skill calls MCP tool: get_active_chart
4. MCP server fetches data from TradingView
5. Skill runs PatternDetector on DataFrame
6. Skill formats results
7. Claude presents analysis to user in natural language

## Testing Strategy

- **Unit tests**: Pattern detection logic, risk calculations, data parsing
- **Integration tests**: MCP server tools, skill end-to-end
- **Mocking**: TradingView connection mocked for CI/CD

## Code Style

- **Linter**: Ruff
- **Line length**: 100 characters
- **Type hints**: Python 3.9+ syntax (list[dict] not List[Dict])
- **Docstrings**: Google style

## Known Patterns

1. **MCP Data Flow**: MCP returns JSON → MCPClient.parse_chart_data() → DataFrame → PatternDetector
2. **Configuration**: Skills load trading_config.yaml, MCP server loads mcp_server_config.yaml
3. **Confluence**: ConfluenceAnalyzer.calculate_confluence_score() combines pattern + indicators + drawings
4. **Error Handling**: MCP client has stub mode fallback if TradingView connection fails
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md for new Claude+TradingView architecture"
```

---

### Task 13: Update README

**Files:**
- Modify: `README.md`

**Step 1: Update README with new usage**

Update the Quick Start and Usage sections in `README.md`:

```markdown
## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Configure TradingView
```bash
cp config/mcp_server_config.example.yaml config/mcp_server_config.yaml
cp config/trading_config.example.yaml config/trading_config.yaml

# Set TradingView credentials
export TV_USERNAME="your_tradingview_username"
export TV_PASSWORD="your_tradingview_password"
```

### 3. Start MCP Server
```bash
python mcp_server/server.py
```

### 4. Chat with Claude
Open Claude Code or Claude.ai and ask:
- "Analyze my current chart for ICT patterns"
- "Give me a trade setup with risk management"
- "What are the best opportunities on my watchlist?"

Claude will use the MCP server to access your TradingView workspace and provide intelligent analysis.

## 💬 Usage Examples

### Pattern Analysis
```
You: "Analyze my NQ chart for Fair Value Gaps"

Claude: 📊 ICT Pattern Analysis for NQ=F
Found 3 Fair Value Gaps:
1. BULLISH FVG at 15,400-15,420 (Strength: 8/10)
   Entry: 15,420 | SL: 15,390 | TP: 15,510
2. BEARISH FVG at 15,550-15,565 (Strength: 6/10)
   ...
```

### Trade Setup with Confluence
```
You: "Give me a trade setup with risk management"

Claude: 🎯 LONG Setup - NQ=F

Pattern: Bullish FVG + Order Block
Entry: 15,420
Stop Loss: 15,390 (30 points)
Take Profit: 15,510 (90 points)
Position Size: 2 contracts (2% risk)
Risk/Reward: 1:3

Confluence Factors (3):
✓ RSI oversold (32.5)
✓ Your trendline support at 15,410
✓ Order block (strength 8/10)
```
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README for Claude conversational interface"
```

---

## Final Steps

### Task 14: Integration Test

**Step 1: Start MCP server**

Run: `python mcp_server/server.py`
Expected: Server starts without errors

**Step 2: Test get_active_chart tool**

Test manually or with MCP inspector that the tool returns data.

**Step 3: Test analyze-ict-patterns skill**

Create sample chart data and run:
```bash
python skills/analyze-ict-patterns/analyze.py '{"symbol": "NQ=F", "bars": []}'
```

Expected: Outputs pattern analysis

**Step 4: Document any issues**

Create issues for remaining TODOs.

**Step 5: Final commit**

```bash
git add -A
git commit -m "feat: complete Claude + TradingView integration restructure

- TradingView MCP server with 5 tools
- analyze-ict-patterns Claude skill
- Refactored core modules (PatternDetector, RiskManager)
- New utilities (MCPClient, ConfluenceAnalyzer)
- Removed Streamlit GUI and CLI
- Updated documentation

Closes #X"
```

---

## Summary

This plan restructures the ICT Trading Agent from a Streamlit GUI to a Claude-powered conversational interface with full TradingView integration.

**Completed:**
- MCP server with TradingView data access
- Refactored core analysis modules
- Claude skill for pattern analysis
- Configuration system
- Documentation updates

**Remaining (Future Tasks):**
- Complete remaining Claude skills (calculate-risk, generate-trade-setup, monitor-workspace)
- Implement remaining MCP tools (get_indicators, get_drawings, get_watchlist, get_alerts)
- Add more sophisticated TradingView connection (websockets, better scraping)
- Integration testing with real TradingView account
- Additional skills (backtesting, multi-timeframe, trade tracking)
