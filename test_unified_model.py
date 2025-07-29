"""
Test script for the unified financial data model.
Validates the new unified model implementation and conversion utilities.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.unified_financial_data import (
    UnifiedFinancialData, UnifiedFinancialScenario, ScenarioMetadata,
    CurrencyValue, Currency, Jurisdiction, FinancialPhase,
    IncomeBreakdown, ExpenseBreakdown, TaxBreakdown, InvestmentBreakdown, NetWorthBreakdown
)
from models.unified_helpers import (
    create_unified_income_breakdown,
    create_unified_expense_breakdown,
    create_unified_tax_breakdown,
    create_unified_investment_breakdown,
    create_unified_net_worth_breakdown
)


def test_currency_value():
    """Test CurrencyValue creation and conversion."""
    print("Testing CurrencyValue...")
    
    # Test GBP creation
    gbp_value = CurrencyValue.from_gbp(50000)
    assert gbp_value.value == 50000
    assert gbp_value.currency == Currency.GBP
    assert gbp_value.gbp_value == 50000
    assert gbp_value.exchange_rate == 1.0
    print("✅ GBP CurrencyValue creation passed")
    
    # Test USD creation
    usd_value = CurrencyValue.from_usd(75000, 1.26)
    assert usd_value.value == 75000
    assert usd_value.currency == Currency.USD
    assert usd_value.gbp_value == 75000 / 1.26
    assert usd_value.exchange_rate == 1.26
    print("✅ USD CurrencyValue creation passed")
    
    # Test EUR creation
    eur_value = CurrencyValue.from_eur(60000, 1.15)
    assert eur_value.value == 60000
    assert eur_value.currency == Currency.EUR
    assert eur_value.gbp_value == 60000 / 1.15
    assert eur_value.exchange_rate == 1.15
    print("✅ EUR CurrencyValue creation passed")


def test_income_breakdown():
    """Test IncomeBreakdown creation and calculations."""
    print("Testing IncomeBreakdown...")
    
    income = create_unified_income_breakdown(
        salary_gbp=50000,
        bonus_gbp=10000,
        rsu_gbp=15000,
        other_income_gbp=5000
    )
    
    assert income.salary.gbp_value == 50000
    assert income.bonus.gbp_value == 10000
    assert income.rsu_vested.gbp_value == 15000
    assert income.other_income.gbp_value == 5000
    assert income.total_gbp == 80000
    print("✅ IncomeBreakdown creation and calculations passed")


def test_expense_breakdown():
    """Test ExpenseBreakdown creation and calculations."""
    print("Testing ExpenseBreakdown...")
    
    expenses = create_unified_expense_breakdown(
        housing_gbp=15000,
        living_gbp=12000,
        taxes_gbp=18000,
        investments_gbp=8000,
        other_gbp=5000
    )
    
    assert expenses.housing.gbp_value > 0
    assert expenses.living.gbp_value > 0
    assert expenses.taxes.gbp_value > 0
    assert expenses.investments.gbp_value > 0
    assert expenses.other.gbp_value > 0
    assert expenses.total_gbp == 58000
    print("✅ ExpenseBreakdown creation and calculations passed")


def test_tax_breakdown():
    """Test TaxBreakdown creation and calculations."""
    print("Testing TaxBreakdown...")
    
    tax = create_unified_tax_breakdown(
        income_tax_gbp=12000,
        social_security_gbp=6000,
        other_taxes_gbp=1000
    )
    
    assert tax.income_tax.gbp_value == 12000
    assert tax.social_security.gbp_value == 6000
    assert tax.other_taxes.gbp_value == 1000
    assert tax.total_gbp == 19000
    print("✅ TaxBreakdown creation and calculations passed")


def test_investment_breakdown():
    """Test InvestmentBreakdown creation and calculations."""
    print("Testing InvestmentBreakdown...")
    
    investments = create_unified_investment_breakdown(
        retirement_gbp=20000,
        taxable_gbp=15000,
        housing_gbp=25000
    )
    
    assert investments.retirement.gbp_value > 0
    assert investments.taxable.gbp_value > 0
    assert investments.housing.gbp_value > 0
    assert investments.total_gbp == 60000
    print("✅ InvestmentBreakdown creation and calculations passed")


def test_net_worth_breakdown():
    """Test NetWorthBreakdown creation and calculations."""
    print("Testing NetWorthBreakdown...")
    
    net_worth = create_unified_net_worth_breakdown(
        liquid_assets_gbp=100000,
        illiquid_assets_gbp=200000,
        liabilities_gbp=50000
    )
    
    assert net_worth.liquid_assets.gbp_value == 100000
    assert net_worth.illiquid_assets.gbp_value == 200000
    assert net_worth.liabilities.gbp_value == 50000
    assert net_worth.total_gbp == 250000
    print("✅ NetWorthBreakdown creation and calculations passed")


def test_unified_financial_data():
    """Test UnifiedFinancialData creation and properties."""
    print("Testing UnifiedFinancialData...")
    
    # Create sample data
    income = create_unified_income_breakdown(50000, 10000, 15000, 5000)
    expenses = create_unified_expense_breakdown(15000, 12000, 18000, 8000, 5000)
    tax = create_unified_tax_breakdown(12000, 6000, 1000)
    investments = create_unified_investment_breakdown(20000, 15000, 25000)
    net_worth = create_unified_net_worth_breakdown(100000, 200000, 50000)
    
    # Create unified data point
    data_point = UnifiedFinancialData(
        year=2024,
        age=25,
        phase=FinancialPhase.UK_ONLY,
        jurisdiction=Jurisdiction.UK,
        currency=Currency.GBP,
        income=income,
        expenses=expenses,
        tax=tax,
        investments=investments,
        net_worth=net_worth,
        exchange_rates={Currency.GBP: 1.0, Currency.USD: 1.26}
    )
    
    # Test computed properties
    assert data_point.net_worth_gbp == 250000
    assert data_point.annual_savings_gbp == 22000  # 80000 - 58000
    assert data_point.gross_income_gbp == 80000
    assert data_point.total_expenses_gbp == 58000
    assert data_point.total_tax_gbp == 19000
    print("✅ UnifiedFinancialData creation and computed properties passed")


def test_unified_scenario():
    """Test UnifiedFinancialScenario creation and methods."""
    print("Testing UnifiedFinancialScenario...")
    
    # Create metadata
    metadata = ScenarioMetadata(
        jurisdiction=Jurisdiction.UK,
        tax_system="UK Tax System",
        housing_strategy="UK Home",
        relocation_timing=None,
        salary_progression="UK Internal",
        investment_strategy="UK-focused (ISA, LISA, SIPP)",
        description="Test UK Scenario"
    )
    
    # Create scenario
    scenario = UnifiedFinancialScenario(
        name="Test_UK_Scenario",
        description="Test UK scenario for validation",
        phase=FinancialPhase.UK_ONLY,
        data_points=[],
        metadata=metadata
    )
    
    # Add data points
    for year in range(1, 6):
        # Use consistent values for income and expenses to get predictable savings
        income = create_unified_income_breakdown(80000, 10000, 15000, 5000)  # Total: 110000
        expenses = create_unified_expense_breakdown(15000, 12000, 18000, 8000, 5000)  # Total: 58000
        tax = create_unified_tax_breakdown(12000, 6000, 1000)  # Total: 19000
        investments = create_unified_investment_breakdown(20000, 15000, 25000)
        net_worth = create_unified_net_worth_breakdown(100000 + year * 50000, 200000, 50000)
        
        data_point = UnifiedFinancialData(
            year=year,
            age=25 + year - 1,
            phase=FinancialPhase.UK_ONLY,
            jurisdiction=Jurisdiction.UK,
            currency=Currency.GBP,
            income=income,
            expenses=expenses,
            tax=tax,
            investments=investments,
            net_worth=net_worth,
            exchange_rates={Currency.GBP: 1.0}
        )
        
        scenario.add_data_point(data_point)
    
    # Test scenario methods
    assert len(scenario.data_points) == 5
    
    final_net_worth = scenario.get_final_net_worth_gbp()
    print(f"Final net worth: {final_net_worth}")
    # For year 5: liquid_assets = 100000 + 5*50000 = 350000, illiquid_assets = 200000, liabilities = 50000
    # Net worth = 350000 + 200000 - 50000 = 500000
    expected_net_worth = 500000
    print(f"Expected net worth: {expected_net_worth}")
    assert final_net_worth == expected_net_worth
    
    avg_savings = scenario.get_average_annual_savings_gbp()
    print(f"Average savings: {avg_savings}")
    # Income: 110000, Expenses: 58000, Savings: 52000
    expected_savings = 52000
    print(f"Expected savings: {expected_savings}")
    assert avg_savings == expected_savings
    
    total_tax = scenario.get_total_tax_burden_gbp()
    print(f"Total tax burden: {total_tax}")
    expected_tax = 19000 * 5
    print(f"Expected tax burden: {expected_tax}")
    assert total_tax == expected_tax
    
    final_savings = scenario.get_final_annual_savings_gbp()
    print(f"Final annual savings: {final_savings}")
    assert final_savings == expected_savings
    
    growth_rate = scenario.get_net_worth_growth_rate()
    print(f"Growth rate: {growth_rate}")
    assert growth_rate > 0
    
    print("✅ UnifiedFinancialScenario creation and methods passed")


def test_conversion_utilities():
    """Test conversion utility functions."""
    print("Testing conversion utilities...")
    
    # Test currency value creation
    gbp_val = CurrencyValue.from_gbp(50000)
    usd_val = CurrencyValue.from_usd(75000, 1.26)
    eur_val = CurrencyValue.from_eur(60000, 1.15)
    
    assert gbp_val.gbp_value == 50000
    assert usd_val.gbp_value == 75000 / 1.26
    assert eur_val.gbp_value == 60000 / 1.15
    print("✅ Currency conversion utilities passed")
    
    # Test breakdown creation utilities
    income = create_unified_income_breakdown(50000, 10000, 15000, 5000)
    expenses = create_unified_expense_breakdown(15000, 12000, 18000, 8000, 5000)
    tax = create_unified_tax_breakdown(12000, 6000, 1000)
    investments = create_unified_investment_breakdown(20000, 15000, 25000)
    net_worth = create_unified_net_worth_breakdown(100000, 200000, 50000)
    
    assert income.total_gbp == 80000
    assert expenses.total_gbp == 58000
    assert tax.total_gbp == 19000
    assert investments.total_gbp == 60000
    assert net_worth.total_gbp == 250000
    print("✅ Breakdown creation utilities passed")


def main():
    """Run all tests."""
    print("🧪 Testing Unified Financial Data Model")
    print("=" * 50)
    
    try:
        test_currency_value()
        test_income_breakdown()
        test_expense_breakdown()
        test_tax_breakdown()
        test_investment_breakdown()
        test_net_worth_breakdown()
        test_unified_financial_data()
        test_unified_scenario()
        test_conversion_utilities()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Unified model is working correctly.")
        print("🎉 The unified data model is ready for implementation.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main() 