# ICT Trading Agent - Claude + TradingView Integration Design

**Date:** 2026-01-06
**Status:** Approved for Implementation

## Overview

Restructure the ICT Trading Agent from a Streamlit GUI application to a Claude-powered conversational interface with TradingView workspace integration. This enables non-technical users to interact naturally with Claude to analyze charts, detect ICT patterns, and receive actionable trade recommendations.

## Goals

- **Remove GUI:** Delete Streamlit dashboard - not user-friendly
- **Claude Interface:** Natural conversation-based interaction
- **TradingView Integration:** Claude can read user's TradingView charts, indicators, drawings, and workspace
- **Keep Core Logic:** Preserve existing pattern detection and risk management algorithms
- **Non-Technical Users:** Anyone can use via chat, no coding required

## Architecture

### Three-Layer System

**Layer 1: TradingView MCP Server**
- Standalone MCP server providing TradingView data access
- Runs as background service
- Claude connects via MCP protocol
- Returns structured JSON data

**Layer 2: Claude Skills**
- Skills wrap existing Python logic
- Call MCP server for TradingView data
- Perform analysis and generate recommendations
- Return natural language + structured results

**Layer 3: Core Analysis Logic (Refactored)**
- Existing PatternDetector, RiskManager, Indicators
- Refactored to accept data from MCP instead of yfinance
- Importable by skills
- Battle-tested algorithms preserved

## TradingView MCP Server

### MCP Tools

1. **get_active_chart**
   - Returns: Symbol, timeframe, OHLCV data (500+ bars), visible price range
   - Use: Get current chart user is viewing

2. **get_indicators**
   - Returns: Built-in indicator values (RSI, MACD, etc.), custom indicators, parameters
   - Use: Understand user's technical analysis context

3. **get_drawings**
   - Returns: Trendlines, support/resistance, Fibonacci levels, text notes, zones
   - Use: Respect user's manual analysis and find confluence

4. **get_watchlist**
   - Returns: Symbols, current prices, custom notes
   - Use: Multi-symbol analysis

5. **get_alerts**
   - Returns: Active alerts, conditions, price levels, recent triggers
   - Use: Monitor setups and alert proximity

### Technical Implementation

- Python using MCP SDK
- TradingView websocket connection (tvDatafeed-style approach)
- Web scraping fallback for drawings/annotations
- Configuration file for TradingView credentials
- Extensible design - easy to add more tools later

### Data Format

JSON responses following MCP conventions:
```json
{
  "symbol": "NQ=F",
  "timeframe": "1h",
  "bars": [...OHLCV...],
  "indicators": {"RSI_14": 67.3, "MACD": {...}},
  "drawings": [{"type": "trendline", "points": [...]}]
}
```

## Claude Skills

### Core Skills

**1. analyze-ict-patterns**
- Purpose: Detect Fair Value Gaps, Order Blocks, Liquidity Pools
- Data: Calls get_active_chart MCP tool
- Logic: Uses PatternDetector.py
- Output: Pattern locations, strength scores, confluence zones

**2. calculate-risk**
- Purpose: Position sizing, stop-loss, take-profit calculations
- Data: Chart data + account size from config
- Logic: Uses RiskManager.py, ATR-based stops
- Output: Position size, SL/TP levels, risk/reward ratio

**3. generate-trade-setup**
- Purpose: Complete trade plan with entry/exit and reasoning
- Data: Calls get_active_chart, get_indicators, get_drawings
- Logic: Combines ICT patterns + TradingView indicators + drawings + risk calculations
- Output: Entry, SL, TP, position size, confluence factors, reasoning

**4. monitor-workspace**
- Purpose: Multi-symbol opportunity scanning
- Data: Calls get_watchlist, get_alerts
- Logic: Runs ICT analysis on each symbol, prioritizes by strength
- Output: Ranked list of opportunities

### Future Skills (Extensible)

- `backtest-pattern` - Historical pattern performance
- `compare-timeframes` - Multi-timeframe ICT analysis
- `track-trades` - Trade journaling and analysis

### Skill Architecture

Each skill follows standard pattern:
1. Call MCP tools for TradingView data
2. Import and use existing Python modules
3. Output natural language + structured data
4. Easy to add new skills using same template

## Code Refactoring

### Keep and Modify

**PatternDetector (src/pattern_detector.py)**
- Keep: All detection algorithms
- Change: Remove DataHandler dependency, accept raw DataFrame from MCP
- Add: Optional TradingView drawings parameter for confluence

**RiskManager (src/risk_manager.py)**
- Keep: Position sizing, SL/TP calculations, portfolio risk tracking
- Change: Configuration from simplified YAML file
- Add: TradingView account size integration

**Technical Indicators (src/utils/indicators.py)**
- Keep: All 15+ indicators unchanged
- Use: Backup/validation when TradingView indicators unavailable

**Data Handler → Data Utils**
- Remove: yfinance fetching (replaced by MCP)
- Keep: Data cleaning and validation utilities
- Rename: src/utils/data_utils.py
- Keep: Cache utilities for analysis results

### New Components

**src/utils/mcp_client.py**
- Helper functions for skills to call MCP tools
- Connection management
- Error handling

**src/utils/confluence_analyzer.py**
- Correlates ICT patterns with TradingView indicators
- Identifies multi-factor confluence zones
- Scoring system for setup quality

### Configuration Files

```
config/
  trading_config.yaml      - Account size, risk params, ICT thresholds
  mcp_server_config.yaml   - TradingView credentials, connection settings
  skills_config.yaml       - Skill-specific settings
```

### Delete

- ✗ src/dashboard.py (Streamlit GUI)
- ✗ src/main.py (CLI)
- ✗ src/backtester.py (use TradingView replay instead)
- ✗ src/performance_reporter.py (not needed without backtester)

## Data Flow

### Example 1: Quick Pattern Analysis

```
User → Claude: "Analyze my current NQ chart for ICT setups"

Claude → analyze-ict-patterns skill
Skill → MCP: get_active_chart
MCP → Returns OHLCV data
Skill → PatternDetector.detect_fair_value_gaps(df)
Skill → PatternDetector.detect_order_blocks(df)
Skill → Claude: Structured pattern data
Claude → User: "Found 2 bullish FVGs at 15,420 and 15,445.
                Strong order block at 15,400 (strength 8/10)..."
```

### Example 2: Complete Trade Setup

```
User → Claude: "Give me a trade setup with risk management"

Claude → generate-trade-setup skill
Skill → MCP: get_active_chart, get_indicators, get_drawings
MCP → Returns chart + RSI + trendlines + Fibonacci
Skill → PatternDetector (finds bullish FVG)
Skill → Confluence check:
  - RSI oversold ✓
  - Trendline at 15,400 aligns with order block ✓
  - Fibonacci 0.618 at 15,425 ✓
Skill → RiskManager.calculate_position_size()
Skill → Claude: Trade plan
Claude → User: "LONG setup at 15,420 (FVG + trendline support)
                Entry: 15,420 | SL: 15,390 | TP: 15,510
                Position: 2 contracts (2% risk = $300)
                R:R = 1:3, Confluence: 3 factors"
```

### Example 3: Multi-Symbol Monitoring

```
User → Claude: "What are the best opportunities on my watchlist?"

Claude → monitor-workspace skill
Skill → MCP: get_watchlist
MCP → ["NQ=F", "ES=F", "YM=F", "RTY=F"]
Skill → For each symbol:
  - get_active_chart (switches charts)
  - Run pattern detection
  - Score by strength + confluence
Skill → Claude: Ranked results
Claude → User: "1. ES=F - Bullish FVG + order block (9/10)
                2. NQ=F - Liquidity pool setup (7/10)
                3. YM=F - Weak bearish pattern (4/10)
                4. RTY=F - No clear setups"
```

## User Experience

### Target User
- Trader familiar with ICT concepts
- May or may not be technical
- Uses TradingView for charting
- Wants AI-powered pattern detection and trade ideas

### Interaction Model
- Natural conversation with Claude
- No coding required
- Works via Claude.ai or Claude Code CLI
- Claude reads their actual TradingView workspace
- Receives actionable trade recommendations with reasoning

### Key Benefits
1. **Natural Interface:** Chat instead of buttons/CLI commands
2. **Context-Aware:** Claude sees their indicators, drawings, watchlists
3. **Intelligent Analysis:** Combines ICT patterns with user's technical analysis
4. **Non-Technical:** Anyone can use by chatting with Claude
5. **Extensible:** Easy to add new analysis types as skills

## Success Criteria

1. **MCP Server:** Successfully connects to TradingView, fetches charts/indicators/drawings
2. **Skills:** All 4 core skills work and return accurate analysis
3. **Pattern Detection:** Existing ICT algorithms work with MCP data
4. **User Experience:** Non-technical user can chat with Claude to get trade setups
5. **Confluence:** System correlates ICT patterns with TradingView context
6. **No GUI:** Streamlit completely removed, interaction via Claude only

## Future Enhancements

- Additional skills (backtesting, multi-timeframe, trade tracking)
- More MCP tools (order execution, account info, positions)
- Integration with other trading platforms (MetaTrader, Interactive Brokers)
- Pattern performance tracking and learning
- Automated alert creation in TradingView
