"""
Tax Utilities Package
Centralized tax calculation functions for UK, US, and UAE scenarios.
"""

from .tax_utils import calculate_tax_for_location, get_tax_breakdown_for_location, get_tax_multiplier_for_location, validate_tax_calculation, calculate_universal_goals
from .uk_tax import calculate_uk_tax_ni, calculate_uk_student_loan, calculate_uk_investment_allocation, calculate_uk_expenses
from .us_tax import calculate_us_tax, calculate_us_expenses, calculate_us_retirement_contribution, calculate_us_investment_allocation
from .uae_tax import calculate_uae_tax, calculate_uae_expenses, calculate_uae_investment_allocation

__all__ = [
    # Tax utilities
    'calculate_tax_for_location',
    'get_tax_breakdown_for_location',
    'get_tax_multiplier_for_location',
    'validate_tax_calculation',
    'calculate_universal_goals',
    
    # UK tax functions
    'calculate_uk_tax_ni',
    'calculate_uk_student_loan',
    'calculate_uk_investment_allocation',
    'calculate_uk_expenses',
    
    # US tax functions
    'calculate_us_tax',
    'calculate_us_expenses',
    'calculate_us_retirement_contribution',
    'calculate_us_investment_allocation',
    
    # UAE tax functions
    'calculate_uae_tax',
    'calculate_uae_expenses',
    'calculate_uae_investment_allocation'
] 