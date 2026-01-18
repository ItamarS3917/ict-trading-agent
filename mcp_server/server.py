"""TradingView MCP Server.

Provides MCP tools for Claude to access TradingView chart data,
indicators, drawings, watchlists, and alerts.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from .tradingview_client import TradingViewClient
from utils.config_loader import ConfigLoader


logger = logging.getLogger(__name__)


class TradingViewMCPServer:
    """MCP Server for TradingView integration."""

    def __init__(self):
        """Initialize the MCP server."""
        self.server = Server("tradingview-mcp-server")
        self.tv_client: Optional[TradingViewClient] = None
        self.config: dict[str, Any] = {}

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
                    description="Get OHLCV data from the currently active TradingView chart",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bars": {
                                "type": "integer",
                                "description": "Number of bars to fetch (default: 500)",
                                "default": 500,
                            }
                        },
                    },
                ),
                types.Tool(
                    name="get_indicators",
                    description="Get indicator values from the active chart (RSI, MACD, etc.)",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="get_drawings",
                    description="Get user drawings from the active chart (trendlines, Fib levels, etc.)",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="get_watchlist",
                    description="Get symbols from user's watchlist",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="get_alerts",
                    description="Get user's active alerts and recent triggers",
                    inputSchema={"type": "object", "properties": {}},
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls."""
            if not self.tv_client:
                return [
                    types.TextContent(
                        type="text", text="Error: TradingView client not initialized"
                    )
                ]

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
                    return [
                        types.TextContent(
                            type="text", text=f"Error: Unknown tool '{name}'"
                        )
                    ]

                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def start(self):
        """Start the MCP server."""
        # Load configuration
        try:
            loader = ConfigLoader()
            self.config = loader.load("mcp_server_config.yaml")
        except FileNotFoundError:
            logger.warning("Config file not found, using defaults")
            self.config = {"tradingview": {}}

        # Initialize TradingView client
        self.tv_client = TradingViewClient(self.config.get("tradingview", {}))
        await self.tv_client.connect()

        logger.info("TradingView MCP Server started")

    async def run(self):
        """Run the server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main():
    """Main entry point."""
    logging.basicConfig(level=logging.INFO)

    server = TradingViewMCPServer()
    await server.start()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
