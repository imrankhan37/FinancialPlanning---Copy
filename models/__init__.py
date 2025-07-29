"""
Models package for financial planning dashboard.
Contains Pydantic models for financial data structures.
"""

# Legacy models (for backward compatibility)
from .financial_data import FinancialDataPoint, FinancialScenario, Phase
from .scenario_builder import (
    create_uk_data_point,
    create_international_data_point,
    build_uk_scenario,
    build_international_scenario,
    build_delayed_relocation_scenario
)

# New unified models
from .unified_financial_data import (
    UnifiedFinancialData,
    UnifiedFinancialScenario,
    ScenarioMetadata,
    CurrencyValue,
    Currency,
    Jurisdiction,
    FinancialPhase,
    IncomeBreakdown,
    ExpenseBreakdown,
    TaxBreakdown,
    InvestmentBreakdown,
    NetWorthBreakdown,
    HousingExpenses,
    LivingExpenses,
    TaxExpenses,
    InvestmentExpenses,
    OtherExpenses,
    RetirementInvestments,
    TaxableInvestments,
    HousingInvestments
)

# Unified helpers
from .unified_helpers import (
    convert_old_to_unified_data_point,
    convert_old_to_unified_scenario,
    create_scenario_metadata_from_name,
    create_unified_currency_value,
    create_unified_income_breakdown,
    create_unified_expense_breakdown,
    create_unified_tax_breakdown,
    create_unified_investment_breakdown,
    create_unified_net_worth_breakdown
)

__all__ = [
    # Legacy models
    'FinancialDataPoint',
    'FinancialScenario', 
    'Phase',
    'create_uk_data_point',
    'create_international_data_point',
    'build_uk_scenario',
    'build_international_scenario',
    'build_delayed_relocation_scenario',
    
    # New unified models
    'UnifiedFinancialData',
    'UnifiedFinancialScenario',
    'ScenarioMetadata',
    'CurrencyValue',
    'Currency',
    'Jurisdiction',
    'FinancialPhase',
    'IncomeBreakdown',
    'ExpenseBreakdown',
    'TaxBreakdown',
    'InvestmentBreakdown',
    'NetWorthBreakdown',
    'HousingExpenses',
    'LivingExpenses',
    'TaxExpenses',
    'InvestmentExpenses',
    'OtherExpenses',
    'RetirementInvestments',
    'TaxableInvestments',
    'HousingInvestments',
    
    # Unified helpers
    'convert_old_to_unified_data_point',
    'convert_old_to_unified_scenario',
    'create_scenario_metadata_from_name',
    'create_unified_currency_value',
    'create_unified_income_breakdown',
    'create_unified_expense_breakdown',
    'create_unified_tax_breakdown',
    'create_unified_investment_breakdown',
    'create_unified_net_worth_breakdown'
] 