"""
Data Handler Module for ICT Trading Agent

DEPRECATED: This module is maintained for backwards compatibility.
Use src/utils/data_utils.py (DataUtils) for new code.

Data fetching is now handled by MCP server - this module provides
data cleaning, validation, and caching utilities.
"""

# Import from new location for backwards compatibility
from utils.data_utils import DataUtils, DataHandler

__all__ = ["DataHandler", "DataUtils"]
