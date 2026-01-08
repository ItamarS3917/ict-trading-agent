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
