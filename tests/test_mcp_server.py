"""Tests for MCP server and TradingView client."""

import pytest

# Skip tests if mcp not installed
pytest.importorskip("mcp")

from mcp_server.tradingview_client import TradingViewClient


class TestTradingViewClient:
    """Test cases for TradingView client."""

    @pytest.fixture
    def client(self):
        """Fixture for TradingView client."""
        config = {"default_symbol": "NASDAQ:NQ1!", "default_timeframe": "1h"}
        return TradingViewClient(config)

    @pytest.mark.asyncio
    async def test_client_connects(self, client):
        """Test that TradingView client can connect."""
        await client.connect()
        assert client.connected is True

    @pytest.mark.asyncio
    async def test_get_active_chart_returns_structure(self, client):
        """Test that get_active_chart returns correct structure."""
        await client.connect()
        chart_data = await client.get_active_chart(bars=100)

        assert "symbol" in chart_data
        assert "timeframe" in chart_data
        assert "bars" in chart_data
        assert isinstance(chart_data["bars"], list)
        assert "fetched_at" in chart_data

    @pytest.mark.asyncio
    async def test_get_active_chart_bars_have_ohlcv(self, client):
        """Test that chart bars have OHLCV data."""
        await client.connect()
        chart_data = await client.get_active_chart(bars=10)

        if chart_data["bars"]:
            bar = chart_data["bars"][0]
            assert "open" in bar
            assert "high" in bar
            assert "low" in bar
            assert "close" in bar
            assert "volume" in bar
            assert "timestamp" in bar

    @pytest.mark.asyncio
    async def test_get_indicators_returns_dict(self, client):
        """Test that get_indicators returns indicator data."""
        await client.connect()
        indicators = await client.get_indicators()

        assert "symbol" in indicators
        assert "indicators" in indicators
        assert isinstance(indicators["indicators"], dict)

    @pytest.mark.asyncio
    async def test_get_drawings_returns_list(self, client):
        """Test that get_drawings returns list of drawings."""
        await client.connect()
        drawings = await client.get_drawings()

        assert isinstance(drawings, list)

    @pytest.mark.asyncio
    async def test_get_watchlist_returns_list(self, client):
        """Test that get_watchlist returns list of symbols."""
        await client.connect()
        watchlist = await client.get_watchlist()

        assert isinstance(watchlist, list)
        if watchlist:
            assert "symbol" in watchlist[0]

    @pytest.mark.asyncio
    async def test_get_alerts_returns_list(self, client):
        """Test that get_alerts returns list of alerts."""
        await client.connect()
        alerts = await client.get_alerts()

        assert isinstance(alerts, list)

    def test_set_symbol(self, client):
        """Test setting symbol."""
        client.set_symbol("CME:ES1!")
        assert client.current_symbol == "CME:ES1!"

    def test_set_timeframe(self, client):
        """Test setting timeframe."""
        client.set_timeframe("5m")
        assert client.current_timeframe == "5m"
