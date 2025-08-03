#!/usr/bin/env python3
"""
Detailed Scenario Display Script
Shows year-by-year financial breakdown for specific scenarios in a readable format.
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.template_engine import TemplateEngine, GenericCalculationEngine


class ScenarioDetailViewer:
    """Display detailed year-by-year breakdown for scenarios."""

    def __init__(self, config_root: str = "config"):
        """Initialize with template engine and calculator."""
        self.template_engine = TemplateEngine(config_root)
        self.calculator = GenericCalculationEngine(self.template_engine)

    def display_scenario_details(self, scenario_id: str):
        """Display comprehensive year-by-year details for a scenario."""
        try:
            print(f"\n{'='*80}")
            print(f"📊 DETAILED YEAR-BY-YEAR ANALYSIS: {scenario_id.upper()}")
            print(f"{'='*80}")

            # Calculate scenario
            result = self.calculator.calculate_scenario_from_templates(scenario_id)
            config = self.template_engine.load_scenario(scenario_id)

            # Show scenario overview
            print(f"📋 Scenario: {result.name}")
            print(f"📝 Description: {result.description}")
            print(f"🏛️  Phase Type: {result.phase.value}")
            print(f"📅 Total Years: {len(result.data_points)}")
            print(f"🔄 Multi-Phase: {'Yes' if config.is_multi_phase else 'No'} ({len(config.phases)} phase(s))")

            # Phase breakdown
            if config.is_multi_phase:
                print(f"\n🔀 PHASE BREAKDOWN:")
                for i, phase in enumerate(config.phases):
                    print(f"  Phase {i+1}: {phase.name} (Years {phase.start_year}-{phase.end_year}, {phase.location_market})")

            print(f"\n💰 YEAR-BY-YEAR FINANCIAL BREAKDOWN:")
            print(f"{'='*80}")

            # Header
            print(f"{'Year':<6} {'Age':<4} {'Jurisdiction':<12} {'Income':<12} {'Tax':<10} {'Net':<12} {'Expenses':<12} {'Savings':<12} {'Net Worth':<12}")
            print(f"{'-'*80}")

            # Year by year data
            for data_point in result.data_points:
                net_income = data_point.income.total_gbp - data_point.tax.total_gbp
                savings = net_income - data_point.expenses.total_gbp

                print(f"{data_point.year:<6} {data_point.age:<4} {data_point.jurisdiction.value:<12} "
                      f"£{data_point.income.total_gbp:>7,.0f}    "
                      f"£{data_point.tax.total_gbp:>6,.0f}   "
                      f"£{net_income:>7,.0f}    "
                      f"£{data_point.expenses.total_gbp:>7,.0f}    "
                      f"£{savings:>7,.0f}    "
                      f"£{data_point.net_worth.total_gbp:>7,.0f}")

            # Summary
            final_year = result.data_points[-1]
            first_year = result.data_points[0]
            total_taxes = sum(dp.tax.total_gbp for dp in result.data_points)
            total_income = sum(dp.income.total_gbp for dp in result.data_points)

            print(f"{'-'*80}")
            print(f"📈 SUMMARY STATISTICS:")
            print(f"  Starting Income: £{first_year.income.total_gbp:,.0f}")
            print(f"  Final Income: £{final_year.income.total_gbp:,.0f}")
            print(f"  Total Income (10 years): £{total_income:,.0f}")
            print(f"  Total Taxes Paid: £{total_taxes:,.0f}")
            print(f"  Effective Tax Rate: {(total_taxes/total_income)*100:.1f}%")
            print(f"  Final Net Worth: £{final_year.net_worth.total_gbp:,.0f}")
            print(f"  Final Liquid Assets: £{final_year.net_worth.liquid_assets.gbp_value:,.0f}")
            print(f"  Final Property Equity: £{final_year.net_worth.illiquid_assets.gbp_value:,.0f}")
            print(f"{'='*80}")

        except Exception as e:
            print(f"❌ Error analyzing {scenario_id}: {e}")

    def display_income_breakdown(self, scenario_id: str):
        """Display detailed income breakdown by component."""
        try:
            result = self.calculator.calculate_scenario_from_templates(scenario_id)

            print(f"\n💵 INCOME COMPONENT BREAKDOWN: {scenario_id.upper()}")
            print(f"{'='*70}")
            print(f"{'Year':<6} {'Salary':<12} {'Bonus':<12} {'RSU':<12} {'Total':<12}")
            print(f"{'-'*70}")

            for data_point in result.data_points:
                print(f"{data_point.year:<6} "
                      f"£{data_point.income.salary.gbp_value:>7,.0f}    "
                      f"£{data_point.income.bonus.gbp_value:>7,.0f}    "
                      f"£{data_point.income.rsu_vested.gbp_value:>7,.0f}    "
                      f"£{data_point.income.total_gbp:>7,.0f}")

            print(f"{'='*70}")

        except Exception as e:
            print(f"❌ Error analyzing income for {scenario_id}: {e}")

    def compare_scenarios(self, scenario_ids: List[str]):
        """Compare multiple scenarios side by side."""
        print(f"\n🔀 SCENARIO COMPARISON")
        print(f"{'='*100}")

        results = {}
        for scenario_id in scenario_ids:
            try:
                result = self.calculator.calculate_scenario_from_templates(scenario_id)
                results[scenario_id] = result
            except Exception as e:
                print(f"❌ Failed to load {scenario_id}: {e}")

        if not results:
            print("❌ No scenarios could be loaded for comparison")
            return

        # Header
        print(f"{'Metric':<25}", end="")
        for scenario_id in results.keys():
            print(f"{scenario_id:<20}", end="")
        print()
        print("-" * (25 + 20 * len(results)))

        # Starting income
        print(f"{'Starting Income':<25}", end="")
        for result in results.values():
            print(f"£{result.data_points[0].income.total_gbp:>15,.0f}     ", end="")
        print()

        # Final income
        print(f"{'Final Income':<25}", end="")
        for result in results.values():
            print(f"£{result.data_points[-1].income.total_gbp:>15,.0f}     ", end="")
        print()

        # Final net worth
        print(f"{'Final Net Worth':<25}", end="")
        for result in results.values():
            print(f"£{result.data_points[-1].net_worth.total_gbp:>15,.0f}     ", end="")
        print()

        # Total taxes
        print(f"{'Total Taxes (10yr)':<25}", end="")
        for result in results.values():
            total_tax = sum(dp.tax.total_gbp for dp in result.data_points)
            print(f"£{total_tax:>15,.0f}     ", end="")
        print()

        # Effective tax rate
        print(f"{'Effective Tax Rate':<25}", end="")
        for result in results.values():
            total_tax = sum(dp.tax.total_gbp for dp in result.data_points)
            total_income = sum(dp.income.total_gbp for dp in result.data_points)
            rate = (total_tax/total_income)*100 if total_income > 0 else 0
            print(f"{rate:>15.1f}%     ", end="")
        print()

        print(f"{'='*100}")


def main():
    """Main execution with examples."""
    viewer = ScenarioDetailViewer()

    # Example 1: Show detailed breakdown for UK conservative scenario
    viewer.display_scenario_details("uk_scenario_a")

    # Example 2: Show income breakdown for Seattle tech graduate
    viewer.display_income_breakdown("seattle_tech_graduate")

    # Example 3: Compare three different scenarios
    comparison_scenarios = ["uk_scenario_a", "seattle_local_home", "dubai_local_home"]
    viewer.compare_scenarios(comparison_scenarios)

    print(f"\n💡 USAGE EXAMPLES:")
    print(f"  # Show specific scenario details:")
    print(f"  viewer.display_scenario_details('seattle_year4_uk_home')")
    print(f"  ")
    print(f"  # Show income breakdown:")
    print(f"  viewer.display_income_breakdown('dubai_tech_graduate')")
    print(f"  ")
    print(f"  # Compare multiple scenarios:")
    print(f"  viewer.compare_scenarios(['uk_scenario_a', 'uk_scenario_b'])")


if __name__ == "__main__":
    main()
