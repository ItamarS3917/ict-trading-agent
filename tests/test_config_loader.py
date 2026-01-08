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
