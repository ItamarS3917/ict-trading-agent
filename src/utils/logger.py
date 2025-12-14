"""
Logging Configuration Module

Sets up comprehensive logging for the ICT Trading Agent.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class LoggerSetup:
    """
    Configures logging for the ICT Trading Agent.
    """
    
    @staticmethod
    def setup_logger(
        name: str = "ict_trading_agent",
        log_file: Optional[str] = None,
        level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True
    ) -> logging.Logger:
        """
        Set up a logger with file and console handlers.
        
        Args:
            name: Logger name
            log_file: Path to log file
            level: Logging level
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            console_output: Whether to output to console
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Set logging level
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        return logger
    
    @staticmethod
    def setup_from_config(config: dict) -> logging.Logger:
        """
        Set up logger from configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configured logger
        """
        logging_config = config.get('logging', {})
        
        return LoggerSetup.setup_logger(
            name="ict_trading_agent",
            log_file=logging_config.get('file', 'logs/ict_agent.log'),
            level=logging_config.get('level', 'INFO'),
            max_bytes=LoggerSetup._parse_size(logging_config.get('max_size', '10MB')),
            backup_count=logging_config.get('backup_count', 5),
            console_output=True
        )
    
    @staticmethod
    def _parse_size(size_str: str) -> int:
        """
        Parse size string like '10MB' to bytes.
        
        Args:
            size_str: Size string
            
        Returns:
            Size in bytes
        """
        units = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024,
            'GB': 1024 * 1024 * 1024
        }
        
        size_str = size_str.upper().strip()
        
        for unit, multiplier in units.items():
            if size_str.endswith(unit):
                value = float(size_str[:-len(unit)])
                return int(value * multiplier)
        
        # Default to bytes
        return int(size_str)


class TradeLogger:
    """
    Specialized logger for trade events.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize trade logger.
        
        Args:
            logger: Base logger instance
        """
        self.logger = logger
    
    def log_signal(self, signal: dict) -> None:
        """Log trading signal generation."""
        self.logger.info(
            f"Signal Generated: {signal['pattern']} {signal['direction']} "
            f"@ ${signal['price']:.2f} - Strength: {signal['strength']:.2%}"
        )
    
    def log_trade_entry(self, trade: dict) -> None:
        """Log trade entry."""
        self.logger.info(
            f"Trade Entry: {trade['direction']} @ ${trade['entry_price']:.2f} "
            f"- SL: ${trade['stop_loss']:.2f}, TP: ${trade['take_profit']:.2f}"
        )
    
    def log_trade_exit(self, trade: dict) -> None:
        """Log trade exit."""
        pnl_indicator = "✅" if trade['pnl'] > 0 else "❌"
        self.logger.info(
            f"Trade Exit {pnl_indicator}: {trade['direction']} @ ${trade['exit_price']:.2f} "
            f"- P&L: ${trade['pnl']:.2f} - Reason: {trade['exit_reason']}"
        )
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None) -> None:
        """Log error."""
        if exception:
            self.logger.error(f"{error_msg}: {str(exception)}", exc_info=True)
        else:
            self.logger.error(error_msg)
    
    def log_backtest_start(self, symbol: str, start_date: str, end_date: str) -> None:
        """Log backtest start."""
        self.logger.info(
            f"Backtest Started: {symbol} from {start_date} to {end_date}"
        )
    
    def log_backtest_complete(self, results: dict) -> None:
        """Log backtest completion."""
        self.logger.info(
            f"Backtest Complete: Total Return: {results['total_return']:.2%}, "
            f"Win Rate: {results['win_rate']:.2%}, "
            f"Total Trades: {results['total_trades']}"
        )
