"""
Financial Planning Utilities Package
Contains tax calculations and utilities for different jurisdictions.
"""

from .tax.uk_tax import (
    calculate_uk_tax_ni,
    calculate_uk_student_loan,
    calculate_uk_investment_allocation,
    calculate_uk_expenses
)

from .tax.us_tax import (
    calculate_us_tax,
    calculate_us_expenses,
    calculate_us_retirement_contribution
)

from .tax.uae_tax import (
    calculate_uae_expenses
)

from .common import (
    calculate_inflation_multiplier,
    convert_usd_to_gbp,
    convert_gbp_to_usd,
    calculate_mortgage_payment
)

from .scenario_helpers import (
    initialize_scenario_state,
    calculate_parental_home_price,
    calculate_uk_salary_progression,
    calculate_uk_bonus,
    calculate_rsu_vesting_scenario_a,
    calculate_rsu_vesting_scenario_b,
    calculate_mortgage_and_house_equity,
    calculate_uk_investment_growth,
    calculate_international_expenses,
    calculate_international_housing,
    convert_to_gbp_for_comparison
)

__all__ = [
    # UK functions
    'calculate_uk_tax_ni',
    'calculate_uk_student_loan',
    'calculate_uk_investment_allocation',
    'calculate_uk_expenses',
    
    # US functions
    'calculate_us_tax',
    'calculate_us_expenses',
    'calculate_us_retirement_contribution',
    
    # UAE functions
    'calculate_uae_expenses',
    
    # Common functions
    'calculate_inflation_multiplier',
    'convert_usd_to_gbp',
    'convert_gbp_to_usd',
    'calculate_mortgage_payment',
    
    # Scenario helper functions
    'initialize_scenario_state',
    'calculate_parental_home_price',
    'calculate_uk_salary_progression',
    'calculate_uk_bonus',
    'calculate_rsu_vesting_scenario_a',
    'calculate_rsu_vesting_scenario_b',
    'calculate_mortgage_and_house_equity',
    'calculate_uk_investment_growth',
    'calculate_international_expenses',
    'calculate_international_housing',
    'convert_to_gbp_for_comparison'
] 