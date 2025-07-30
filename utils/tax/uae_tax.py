"""
UAE Tax Utilities Module
Handles UAE-specific calculations including tax-free environment and local expenses.
"""

def calculate_uae_tax(gross_income):
    """Calculates UAE taxes (0% income tax)."""
    # UAE has 0% personal income tax
    return 0

def calculate_uae_expenses(loc_config, inf_multiplier):
    """Calculates UAE expenses including rent, healthcare, etc."""
    # Housing
    rent = loc_config["rent_monthly"] * 12 * inf_multiplier
    
    # Healthcare (much cheaper in UAE)
    healthcare = loc_config["healthcare_monthly"] * 12 * inf_multiplier
    
    # No retirement contribution (no 401k equivalent)
    retirement_contrib = 0
    
    # General living expenses
    general_expenses = loc_config["general_expenses_monthly"] * 12 * inf_multiplier
    
    return {
        "rent": rent,
        "healthcare": healthcare,
        "retirement_contribution": retirement_contrib,
        "general_expenses": general_expenses
    }

def calculate_uae_investment_allocation(annual_net_savings):
    """Calculates UAE investment allocation (simplified - no specific tax vehicles)."""
    # Simplified UAE investment - no specific tax-advantaged accounts modeled
    return {
        "total_investment": annual_net_savings
    } 