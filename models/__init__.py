"""
Models package for financial planning dashboard.
Contains Pydantic models for financial data structures.
"""

# Unified models - ALL USED
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
    HousingInvestments,
    PhaseConfig,
    ResolvedScenarioConfig
)

# Unified helpers - ONLY USED FUNCTIONS
from .unified_helpers import (
    create_unified_income_breakdown,
    create_unified_expense_breakdown,
    create_unified_tax_breakdown,
    create_unified_investment_breakdown,
    create_unified_net_worth_breakdown,
    get_performance_metrics,
    clear_performance_caches
)

# Performance optimizations - ONLY USED FUNCTIONS
from .performance_optimizations import (
    optimize_currency_value_creation,
    get_performance_summary,
    clear_all_caches
)

__all__ = [
    # Unified models
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
    'PhaseConfig',
    'ResolvedScenarioConfig',
    
    # Unified helpers - only used functions
    'create_unified_income_breakdown',
    'create_unified_expense_breakdown',
    'create_unified_tax_breakdown',
    'create_unified_investment_breakdown',
    'create_unified_net_worth_breakdown',
    'get_performance_metrics',
    'clear_performance_caches',
    
    # Performance optimizations - only used functions
    'optimize_currency_value_creation',
    'get_performance_summary',
    'clear_all_caches'
] 