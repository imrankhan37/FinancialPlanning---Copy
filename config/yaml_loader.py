"""
Simple YAML Configuration Loader
Provides optional YAML loading with fallback to legacy CONFIG.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any, List
import sys
import os

# Import the legacy CONFIG directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(parent_dir, 'config.py')

# Load the config module dynamically to avoid circular imports
import importlib.util
spec = importlib.util.spec_from_file_location("config_module", config_path)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
LEGACY_CONFIG = config_module.CONFIG

def try_load_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """Try to load scenario from YAML, return None if not found."""
    try:
        path = Path(__file__).parent / "scenarios" / f"{scenario_id}.yaml"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception:
        pass  # Fail silently, use legacy fallback
    return None

def try_load_tax_system(tax_id: str) -> Optional[Dict[str, Any]]:
    """Try to load tax system from YAML, return None if not found."""
    try:
        # Try main tax systems directory
        path = Path(__file__).parent / "tax_systems" / f"{tax_id}.yaml"
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Try US states subdirectory
        us_states_path = Path(__file__).parent / "tax_systems" / "us_states" / f"{tax_id.replace('us_', '')}.yaml"
        if us_states_path.exists():
            with open(us_states_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
    except Exception:
        pass
    return None

def get_available_yaml_scenarios() -> List[str]:
    """Get list of available YAML scenario files."""
    try:
        scenarios_dir = Path(__file__).parent / "scenarios"
        if scenarios_dir.exists():
            return [f.stem for f in scenarios_dir.glob("*.yaml") if f.name != "README.md"]
    except Exception:
        pass
    return []

def map_scenario_name_to_yaml_id(scenario_name: str) -> Optional[str]:
    """Map legacy scenario names to YAML file IDs."""
    name_mapping = {
        # UK Scenarios
        'UK_Scenario_A': 'uk_scenario_a',
        'UK_Scenario_B': 'uk_scenario_b',
        
        # International Scenarios
        'seattle_tech_graduate': 'seattle_tech_graduate',
        'seattle_uk_home': 'seattle_uk_home',
        'seattle_local_home': 'seattle_local_home',
        'new_york_uk_home': 'new_york_uk_home',
        'dubai_tech_graduate': 'dubai_tech_graduate',
        'dubai_uk_home': 'dubai_uk_home',
        'dubai_local_home': 'dubai_local_home',
        
        # Delayed Relocation Scenarios
        'seattle_year4_uk_home': 'seattle_year4_uk_home',
        'seattle_year4_local_home': 'seattle_year4_local_home',
        'seattle_year5_uk_home': 'seattle_year5_uk_home',
        'seattle_year5_local_home': 'seattle_year5_local_home'
    }
    return name_mapping.get(scenario_name)

def get_tax_system_for_location(location: str) -> str:
    """Map location to tax system ID."""
    location_mapping = {
        'uk': 'uk_income_tax_ni',
        'seattle': 'us_washington',
        'new_york': 'us_new_york',
        'dubai': 'tax_free',
        'california': 'us_california',
        'texas': 'us_texas'
    }
    return location_mapping.get(location.lower(), 'uk_income_tax_ni')

class SimpleConfigFallback:
    """Simple wrapper that tries YAML first, falls back to legacy CONFIG."""
    
    def __init__(self):
        self.legacy_config = LEGACY_CONFIG
    
    def get_scenario_config(self, scenario_name: str) -> Dict[str, Any]:
        """Get scenario config with YAML fallback."""
        yaml_id = map_scenario_name_to_yaml_id(scenario_name)
        if yaml_id:
            yaml_scenario = try_load_scenario(yaml_id)
            if yaml_scenario:
                # Convert YAML to legacy format if needed
                return self._convert_yaml_to_legacy_format(yaml_scenario)
        
        # Fallback to generating from legacy CONFIG
        return self._generate_legacy_scenario_config(scenario_name)
    
    def get_tax_config(self, location: str) -> Dict[str, Any]:
        """Get tax config with YAML fallback."""
        tax_system = get_tax_system_for_location(location)
        yaml_tax = try_load_tax_system(tax_system)
        if yaml_tax:
            return yaml_tax
        
        # Fallback to legacy CONFIG
        return self._extract_legacy_tax_config(location)
    
    def _convert_yaml_to_legacy_format(self, yaml_scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Convert YAML scenario to legacy CONFIG format for backward compatibility."""
        # This is where we'd map YAML structure to legacy structure
        # For now, just return the YAML as-is and enhance gradually
        return yaml_scenario
    
    def _generate_legacy_scenario_config(self, scenario_name: str) -> Dict[str, Any]:
        """Generate scenario config from legacy CONFIG."""
        # Return the entire legacy CONFIG for now
        return self.legacy_config
    
    def _extract_legacy_tax_config(self, location: str) -> Dict[str, Any]:
        """Extract tax config from legacy CONFIG."""
        if location.lower() == 'uk':
            return {
                'tax_bands': self.legacy_config['tax_bands'],
                'tax_rates': self.legacy_config['tax_rates'],
                'ni_bands': self.legacy_config['ni_bands'],
                'ni_rates': self.legacy_config['ni_rates'],
                'student_loan_plan2': self.legacy_config['student_loan_plan2']
            }
        # For non-UK, return simplified structure
        return {'tax_system': 'simplified', 'location': location}
    
    def __getitem__(self, key: str):
        """Fallback to legacy CONFIG for any missing keys."""
        return self.legacy_config[key]
    
    def get(self, key: str, default=None):
        """Safe access method."""
        return self.legacy_config.get(key, default)

# Global instance for easy access
CONFIG_LOADER = SimpleConfigFallback() 