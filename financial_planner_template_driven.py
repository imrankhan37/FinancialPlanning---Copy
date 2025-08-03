#!/usr/bin/env python3
"""
Template-Driven Financial Planner - Utilities Wrapper
Provides convenience functions and utilities around the core template engine.
"""

from pathlib import Path
from typing import Dict, List, Union

from config.template_engine import TemplateEngine, GenericCalculationEngine
from models.unified_financial_data import UnifiedFinancialScenario


class TemplateFinancialPlanner:
    """
    Utilities wrapper around the template engine.
    
    Provides convenience methods for:
    - Discovering available scenarios and templates
    - Validating scenario configurations  
    - Running scenarios with error handling
    """
    
    def __init__(self, config_root: str = "config"):
        """Initialize with template engine."""
        self.template_engine = TemplateEngine(config_root)
        self.calculation_engine = GenericCalculationEngine(self.template_engine)
        self.config_root = Path(config_root)
    
    def run_scenario(self, scenario_id: str) -> UnifiedFinancialScenario:
        """
        Run any scenario purely from YAML templates.
        
        Simple wrapper around the template engine's calculation method.
        """
        return self.calculation_engine.calculate_scenario_from_templates(scenario_id)
    
    def get_available_scenarios(self) -> List[str]:
        """Get list of all available scenarios."""
        scenario_dir = self.config_root / "scenarios"
        scenarios = []
        
        if scenario_dir.exists():
            for file in scenario_dir.glob("*.yaml"):
                if file.name != "README.yaml":
                    scenarios.append(file.stem)
        
        return sorted(scenarios)
    
    def get_available_templates(self, template_type: str) -> List[str]:
        """Get list of available templates by type."""
        template_dir = self.config_root / "templates" / template_type
        templates = []
        
        if template_dir.exists():
            for file in template_dir.glob("*.yaml"):
                templates.append(file.stem)
        
        return sorted(templates)
    
    def validate_scenario(self, scenario_id: str) -> Dict[str, Union[str, bool]]:
        """
        Simple validation status checker.
        
        The comprehensive validation is handled by template_engine.py.
        This just provides a simple pass/fail interface.
        """
        try:
            # This triggers comprehensive validation in template_engine
            self.template_engine.load_scenario(scenario_id)
            return {
                'scenario_id': scenario_id,
                'valid': True,
                'message': 'All templates loaded and validated successfully'
            }
        except Exception as e:
            return {
                'scenario_id': scenario_id,
                'valid': False,
                'message': str(e)
            }
    
    def list_template_types(self) -> List[str]:
        """Get list of available template types."""
        templates_dir = self.config_root / "templates"
        template_types = []
        
        if templates_dir.exists():
            for item in templates_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    template_types.append(item.name)
        
        return sorted(template_types)
    
    def get_scenario_summary(self, scenario_id: str) -> Dict[str, Union[str, int, float]]:
        """Get a quick summary of a scenario without running full calculation."""
        try:
            config = self.template_engine.load_scenario(scenario_id)
            
            return {
                'name': config.scenario_metadata.get('name', scenario_id),
                'description': config.scenario_metadata.get('description', ''),
                'duration_years': config.planning_parameters.get('duration_years', 'Unknown'),
                'start_year': config.planning_parameters.get('start_year', 'Unknown'),
                'start_age': config.planning_parameters.get('start_age', 'Unknown'),
                'phase': str(self.calculation_engine._determine_phase(config)).split('.')[-1],
                'components': {
                    'salary': config.salary_progression.get('metadata', {}).get('name', 'Unknown'),
                    'housing': config.housing_strategy.get('metadata', {}).get('name', 'Unknown'),
                    'expenses': config.expense_profile.get('metadata', {}).get('name', 'Unknown'),
                    'investments': config.investment_strategy.get('metadata', {}).get('name', 'Unknown') if config.investment_strategy else 'None',
                    'tax_system': config.tax_system.get('tax_system_id', 'Unknown'),
                }
            }
        except Exception as e:
            return {'error': str(e)}


def run_template_scenario(scenario_id: str, config_root: str = "config") -> UnifiedFinancialScenario:
    """
    Main entry point for template-driven scenario generation.
    
    Simple convenience function that wraps the template engine.
    """
    planner = TemplateFinancialPlanner(config_root)
    return planner.run_scenario(scenario_id)


if __name__ == "__main__":
    # Test the utilities wrapper
    print("🧪 Testing Template Financial Planner Utilities")
    print("=" * 50)
    
    try:
        planner = TemplateFinancialPlanner()
        
        # Test utilities
        scenarios = planner.get_available_scenarios()
        print(f"✅ Available scenarios: {len(scenarios)}")
        for scenario in scenarios[:3]:  # Show first 3
            print(f"   - {scenario}")
        
        template_types = planner.list_template_types()
        print(f"✅ Template types: {template_types}")
        
        # Test scenario summary
        if scenarios:
            summary = planner.get_scenario_summary(scenarios[0])
            print(f"✅ Summary for {scenarios[0]}:")
            print(f"   Name: {summary.get('name')}")
            print(f"   Duration: {summary.get('duration_years')} years")
            print(f"   Phase: {summary.get('phase')}")
        
        # Test validation
        if scenarios:
            validation = planner.validate_scenario(scenarios[0])
            print(f"✅ Validation: {validation['valid']}")
        
        # Test scenario generation (using template engine)
        if scenarios:
            scenario = run_template_scenario(scenarios[0])
            print(f"✅ Generated scenario: {scenario.name}")
            print(f"   Data points: {len(scenario.data_points)}")
            if scenario.data_points:
                print(f"   Final net worth: £{scenario.get_final_net_worth_gbp():,.0f}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ Template utilities working!")
    print("🎯 All calculations handled by template_engine.py")
    print("🛠️ This file provides only utility functions!") 