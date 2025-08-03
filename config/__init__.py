"""
Configuration Package
Contains YAML-based configuration system and re-exports legacy CONFIG.
"""

import os
import importlib.util

# Import the legacy CONFIG from the root config.py to maintain compatibility
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(parent_dir, 'config.py')

# Load the config module dynamically
spec = importlib.util.spec_from_file_location("legacy_config", config_path)
legacy_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy_config)

# Re-export CONFIG for backward compatibility
CONFIG = legacy_config.CONFIG

__all__ = ['CONFIG'] 