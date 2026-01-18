"""Agent-specific logging system.

Provides separate log files for each AI agent (Claude, Gemini, Cursor)
with daily rotation and configurable retention.
"""

import json
import logging
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any


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
        level: str = "INFO",
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
            backupCount=5,
        )

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    def _cleanup_old_logs(self):
        """Remove log files older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        for log_file in self.log_dir.glob("*.log*"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split(".")[0]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    log_file.unlink()
                    self.logger.info(f"Removed old log file: {log_file.name}")
            except (ValueError, IndexError):
                # Skip files that don't match expected format
                pass

    def log_request(self, skill_name: str, params: dict[str, Any]):
        """
        Log an incoming request.

        Args:
            skill_name: Name of the skill being called
            params: Request parameters
        """
        self.logger.info(f"REQUEST | skill={skill_name} | params={json.dumps(params)}")

    def log_analysis(self, skill_name: str, result: dict[str, Any]):
        """
        Log analysis results.

        Args:
            skill_name: Name of the skill
            result: Analysis result dictionary
        """
        # Log summary without full data to keep logs readable
        summary = {k: v for k, v in result.items() if k != "raw_data"}
        self.logger.info(f"ANALYSIS | skill={skill_name} | result={json.dumps(summary)}")

    def log_error(self, skill_name: str, error: Exception):
        """
        Log an error.

        Args:
            skill_name: Name of the skill where error occurred
            error: The exception
        """
        self.logger.error(
            f"ERROR | skill={skill_name} | error={type(error).__name__}: {str(error)}"
        )

    def log_mcp_call(self, tool_name: str, duration_ms: float, success: bool):
        """
        Log an MCP tool call.

        Args:
            tool_name: Name of the MCP tool called
            duration_ms: Call duration in milliseconds
            success: Whether the call succeeded
        """
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"MCP_CALL | tool={tool_name} | duration_ms={duration_ms:.2f} | status={status}"
        )

    def log_pattern(self, pattern_type: str, count: int, details: dict[str, Any]):
        """
        Log detected patterns.

        Args:
            pattern_type: Type of pattern (FVG, OrderBlock, etc.)
            count: Number of patterns found
            details: Pattern details
        """
        self.logger.info(
            f"PATTERN | type={pattern_type} | count={count} | details={json.dumps(details)}"
        )


def get_agent_logger(agent_name: str, log_dir: str = "logs") -> AgentLogger:
    """
    Get or create an agent logger.

    Args:
        agent_name: Name of the agent
        log_dir: Base directory for logs

    Returns:
        AgentLogger instance
    """
    return AgentLogger(agent_name=agent_name, log_dir=log_dir)
