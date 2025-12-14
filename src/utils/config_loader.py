"""
Configuration Loader Utility

Handles loading and validating configuration from YAML files.
"""

import yaml
import os
from typing import Dict, Any, Optional
import logging


class ConfigLoader:
    """
    Loads and validates configuration for the ICT Trading Agent.
    """
    
    DEFAULT_CONFIG_PATH = "config/config.yaml"
    EXAMPLE_CONFIG_PATH = "config/config.example.yaml"
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.logger = logging.getLogger(__name__)
        self.config = None
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        if not os.path.exists(self.config_path):
            self.logger.warning(f"Config file not found at {self.config_path}")
            
            # Try to load example config
            if os.path.exists(self.EXAMPLE_CONFIG_PATH):
                self.logger.info(f"Loading example config from {self.EXAMPLE_CONFIG_PATH}")
                self.config_path = self.EXAMPLE_CONFIG_PATH
            else:
                self.logger.warning("No config file found, using defaults")
                return self._default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
            # Validate config
            self._validate_config()
            
            return self.config
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return self._default_config()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'trading.symbol')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        if self.config is None:
            self.load()
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def _validate_config(self) -> None:
        """Validate configuration structure and values."""
        if not self.config:
            return
        
        required_sections = ['trading', 'patterns', 'risk', 'backtesting']
        
        for section in required_sections:
            if section not in self.config:
                self.logger.warning(f"Missing required config section: {section}")
    
    def _default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'trading': {
                'symbol': 'NQ=F',
                'timeframe': '1h',
                'lookback_period': 100
            },
            'patterns': {
                'fvg_min_size': 0.001,
                'orderblock_strength': 3,
                'liquidity_threshold': 0.05,
                'swing_window': 5
            },
            'risk': {
                'risk_per_trade': 0.02,
                'max_positions': 3,
                'stop_loss_atr_multiplier': 2,
                'take_profit_ratio': 2
            },
            'data': {
                'primary_source': 'yfinance',
                'cache_duration': 300
            },
            'alerts': {
                'enabled': True,
                'webhook_url': '',
                'email_enabled': False
            },
            'backtesting': {
                'initial_capital': 10000,
                'commission': 2.0,
                'slippage': 0.001,
                'start_date': '2023-01-01',
                'end_date': '2023-12-31'
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/ict_agent.log',
                'max_size': '10MB',
                'backup_count': 5
            },
            'dashboard': {
                'port': 8501,
                'host': 'localhost',
                'auto_refresh': 30,
                'theme': 'dark'
            }
        }
    
    def save(self, config: Dict[str, Any], path: Optional[str] = None) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
            path: Optional path to save to
            
        Returns:
            True if successful
        """
        save_path = path or self.config_path
        
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
