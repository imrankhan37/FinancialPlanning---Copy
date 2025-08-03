#!/usr/bin/env python3
"""
Comprehensive Scenario Analysis Script
Generates year-by-year financial breakdown for all scenarios in config/scenarios/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
import traceback

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.template_engine import TemplateEngine, GenericCalculationEngine
from models.unified_financial_data import UnifiedFinancialScenario, UnifiedFinancialData


class ScenarioAnalyzer:
    """Comprehensive analyzer for all financial scenarios."""
    
    def __init__(self, config_root: str = "config"):
        """Initialize with template engine and calculator."""
        self.template_engine = TemplateEngine(config_root)
        self.calculator = GenericCalculationEngine(self.template_engine)
        self.config_root = Path(config_root)
    
    def get_all_scenarios(self) -> List[str]:
        """Get list of all available scenario files."""
        scenario_dir = self.config_root / "scenarios"
        scenarios = []
        
        # Get all YAML files in scenarios directory
        for file in scenario_dir.glob("*.yaml"):
            if file.name not in ["README.yaml", "template.yaml"]:
                scenarios.append(file.stem)
        
        # Also check examples subdirectory
        examples_dir = scenario_dir / "examples"
        if examples_dir.exists():
            for file in examples_dir.glob("*.yaml"):
                scenarios.append(f"examples/{file.stem}")
        
        return sorted(scenarios)
    
    def analyze_scenario(self, scenario_id: str) -> Dict:
        """Analyze a single scenario and return year-by-year breakdown."""
        try:
            # Load and calculate scenario
            result = self.calculator.calculate_scenario_from_templates(scenario_id)
            
            # Extract year-by-year data
            yearly_data = []
            for data_point in result.data_points:
                yearly_data.append({
                    'year': data_point.year,
                    'age': data_point.age,
                    'jurisdiction': data_point.jurisdiction.value,
                    'currency': data_point.currency.value,
                    'gross_income': round(data_point.income.total_gbp, 0),
                    'salary': round(data_point.income.salary.gbp_value, 0),
                    'bonus': round(data_point.income.bonus.gbp_value, 0),
                    'rsu': round(data_point.income.rsu_vested.gbp_value, 0),
                    'total_tax': round(data_point.tax.total_gbp, 0),
                    'income_tax': round(data_point.tax.income_tax.gbp_value, 0),
                    'social_security': round(data_point.tax.social_security.gbp_value, 0),
                    'net_income': round(data_point.income.total_gbp - data_point.tax.total_gbp, 0),
                    'housing_cost': round(data_point.expenses.housing.gbp_value, 0),
                    'living_expenses': round(data_point.expenses.living.gbp_value, 0),
                    'total_expenses': round(data_point.expenses.total_gbp, 0),
                    'investments_total': round(data_point.investments.total_gbp, 0),
                    'retirement': round(data_point.investments.retirement.gbp_value, 0),
                    'taxable_investments': round(data_point.investments.taxable.gbp_value, 0),
                    'housing_equity': round(data_point.investments.housing.gbp_value, 0),
                    'net_worth': round(data_point.net_worth.total_gbp, 0),
                    'liquid_assets': round(data_point.net_worth.liquid_assets.gbp_value, 0),
                    'illiquid_assets': round(data_point.net_worth.illiquid_assets.gbp_value, 0),
                    'liabilities': round(data_point.net_worth.liabilities.gbp_value, 0)
                })
            
            # Get scenario metadata
            config = self.template_engine.load_scenario(scenario_id)
            
            return {
                'scenario_id': scenario_id,
                'name': result.name,
                'description': result.description,
                'phase': result.phase.value,
                'phases_count': len(config.phases),
                'is_multi_phase': config.is_multi_phase,
                'total_years': len(yearly_data),
                'yearly_data': yearly_data,
                'summary': {
                    'starting_income': yearly_data[0]['gross_income'] if yearly_data else 0,
                    'ending_income': yearly_data[-1]['gross_income'] if yearly_data else 0,
                    'final_net_worth': yearly_data[-1]['net_worth'] if yearly_data else 0,
                    'total_taxes_paid': sum(year['total_tax'] for year in yearly_data),
                    'total_investments': yearly_data[-1]['investments_total'] if yearly_data else 0,
                    'avg_annual_savings': round(sum(year['net_income'] - year['total_expenses'] for year in yearly_data) / len(yearly_data), 0) if yearly_data else 0
                }
            }
            
        except Exception as e:
            return {
                'scenario_id': scenario_id,
                'error': str(e),
                'status': 'failed'
            }
    
    def analyze_all_scenarios(self) -> Dict:
        """Analyze all scenarios and return comprehensive results."""
        print("🔍 COMPREHENSIVE SCENARIO ANALYSIS")
        print("=" * 60)
        
        scenarios = self.get_all_scenarios()
        results = {}
        successful_count = 0
        failed_count = 0
        
        for scenario_id in scenarios:
            print(f"Analyzing {scenario_id}...")
            result = self.analyze_scenario(scenario_id)
            results[scenario_id] = result
            
            if 'error' in result:
                failed_count += 1
                print(f"  ❌ Failed: {result['error']}")
            else:
                successful_count += 1
                summary = result['summary']
                print(f"  ✅ Success: {result['total_years']} years, "
                      f"Final Net Worth: £{summary['final_net_worth']:,.0f}, "
                      f"Phase: {result['phase']}")
        
        print("=" * 60)
        print(f"📊 SUMMARY: {successful_count} successful, {failed_count} failed out of {len(scenarios)} total scenarios")
        
        return {
            'total_scenarios': len(scenarios),
            'successful': successful_count,
            'failed': failed_count,
            'results': results
        }
    
    def export_to_csv(self, results: Dict, output_file: str = "scenario_analysis.csv"):
        """Export all scenario data to CSV format."""
        import csv
        
        # Prepare CSV data
        csv_data = []
        headers_written = False
        
        for scenario_id, data in results['results'].items():
            if 'error' in data:
                continue
                
            for year_data in data['yearly_data']:
                row = {
                    'scenario_id': scenario_id,
                    'scenario_name': data['name'],
                    'phase': data['phase'],
                    'is_multi_phase': data['is_multi_phase'],
                    **year_data
                }
                csv_data.append(row)
        
        # Write CSV
        if csv_data:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            print(f"📁 Exported detailed data to {output_file}")
    
    def print_scenario_comparison(self, results: Dict):
        """Print a comparison table of key metrics across scenarios."""
        print("\n🏆 SCENARIO COMPARISON TABLE")
        print("=" * 80)
        
        successful_results = {k: v for k, v in results['results'].items() if 'error' not in v}
        
        # Header
        print(f"{'Scenario':<25} {'Type':<12} {'Final Income':<15} {'Net Worth':<15} {'Total Tax':<12}")
        print("-" * 80)
        
        # Sort by final net worth
        sorted_scenarios = sorted(successful_results.items(), 
                                key=lambda x: x[1]['summary']['final_net_worth'], 
                                reverse=True)
        
        for scenario_id, data in sorted_scenarios:
            summary = data['summary']
            scenario_type = "Multi-phase" if data['is_multi_phase'] else "Single-phase"
            
            print(f"{scenario_id:<25} {scenario_type:<12} "
                  f"£{summary['ending_income']:>8,.0f}      "
                  f"£{summary['final_net_worth']:>8,.0f}      "
                  f"£{summary['total_taxes_paid']:>8,.0f}")


def main():
    """Main execution function."""
    analyzer = ScenarioAnalyzer()
    
    # Analyze all scenarios
    results = analyzer.analyze_all_scenarios()
    
    # Print comparison table
    analyzer.print_scenario_comparison(results)
    
    # Export to CSV
    analyzer.export_to_csv(results)
    
    print(f"\n✅ Analysis complete! Check 'scenario_analysis.csv' for detailed year-by-year data.")
    
    return results


if __name__ == "__main__":
    try:
        results = main()
    except Exception as e:
        print(f"❌ Script failed: {e}")
        traceback.print_exc()
        sys.exit(1) 