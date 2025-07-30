"""
Models package for financial planning dashboard.
Contains Pydantic models for financial data structures.
"""

# Unified models
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
    create_scenario_metadata_from_name,
    create_unified_currency_value,
    create_unified_income_breakdown,
    create_unified_expense_breakdown,
    create_unified_tax_breakdown,
    create_unified_investment_breakdown,
    create_unified_net_worth_breakdown,
    get_performance_metrics,
    clear_performance_caches
)

# Performance optimizations
from .performance_optimizations import (
    CurrencyConversionCache,
    CacheStrategy,
    CacheEntry,
    DataAccessOptimizer,
    PerformanceMonitor,
    cached_currency_conversion,
    optimized_currency_conversion,
    optimize_currency_value_creation,
    optimize_scenario_analysis,
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
    
    # Unified helpers
    'create_scenario_metadata_from_name',
    'create_unified_currency_value',
    'create_unified_income_breakdown',
    'create_unified_expense_breakdown',
    'create_unified_tax_breakdown',
    'create_unified_investment_breakdown',
    'create_unified_net_worth_breakdown',
    'get_performance_metrics',
    'clear_performance_caches',
    
    # Performance optimizations
    'CurrencyConversionCache',
    'CacheStrategy',
    'CacheEntry',
    'DataAccessOptimizer',
    'PerformanceMonitor',
    'cached_currency_conversion',
    'optimized_currency_conversion',
    'optimize_currency_value_creation',
    'optimize_scenario_analysis',
    'get_performance_summary',
    'clear_all_caches'
] 