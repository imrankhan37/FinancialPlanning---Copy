"""
US Tax Utilities Module (2025)
Handles federal, FICA, New York State, and NYC taxes.
"""

def calculate_us_tax(gross_income, tax_system, year=2025):
    """
    Calculates US federal, FICA, and optional state/city taxes for 2025.
    - gross_income: total annual earnings
    - tax_system: "us_federal_state" (WA) or "us_federal_state_city" (NYC)
    - year: tax year (default 2025)
    """
    # ----- Federal Income Tax -----
    # Standard deduction for single filers
    standard_deduction = 15000  # IRS 2025 :contentReference[oaicite:6]{index=6}
    taxable_income = max(0, gross_income - standard_deduction)

    # Apply marginal rates
    brackets = [
        (11925,    0.10,     0),
        (48475,    0.12,  1192.50),     # 10% of 11,925
        (96950,    0.22,  5595.50),     # 1192.50 + .12*(48,475-11,925)
        (206700,   0.24,  17843.50),    # etc.
        (394600,   0.32,  46253.50),
        (626350,   0.35,  104755.50),
        (float('inf'), 0.37, 186601.50)
    ]
    federal_tax = 0
    for limit, rate, base in brackets:
        if taxable_income <= limit:
            federal_tax = base + (taxable_income - (brackets[brackets.index((limit, rate, base))-1][0] 
                                                    if brackets.index((limit, rate, base))>0 else 0)) * rate
            break

    # ----- FICA Taxes -----
    # Social Security
    ss_limit = 176100  # 2025 wage base :contentReference[oaicite:7]{index=7}
    social_security_tax = min(gross_income, ss_limit) * 0.062  # 6.2% :contentReference[oaicite:8]{index=8}

    # Medicare
    medicare_tax = gross_income * 0.0145                       # 1.45% :contentReference[oaicite:9]{index=9}
    additional_medicare = max(0, gross_income - 200000) * 0.009  # 0.9% over $200k :contentReference[oaicite:10]{index=10}
    fica_tax = social_security_tax + medicare_tax + additional_medicare

    total_tax = federal_tax + fica_tax

    # ----- State & Local Taxes -----
    if tax_system == "us_federal_state":  # e.g. Seattle, WA
        # No state income tax
        pass

    elif tax_system == "us_federal_state_city":  # New York City
        # New York State Tax (single)
        ti = gross_income  # or use taxable_income minus state deduction if desired
        if ti <= 8500:
            state_tax = ti * 0.04
        elif ti <= 11700:
            state_tax = 8500*0.04 + (ti - 8500)*0.045
        elif ti <= 13900:
            state_tax = 8500*0.04 + (11700-8500)*0.045 + (ti - 11700)*0.0525
        elif ti <= 80650:
            state_tax = 8500*0.04 +  (11700-8500)*0.045 + (13900-11700)*0.0525 + (ti - 13900)*0.055
        elif ti <= 215400:
            state_tax = 4271 + (ti - 80650)*0.06
        elif ti <= 1077550:
            state_tax = 4271 + (215400-80650)*0.06 + (ti - 215400)*0.0685
        else:
            state_tax = 4271 + (215400-80650)*0.06 + (1077550-215400)*0.0685 + (ti - 1077550)*0.0965
        total_tax += state_tax

        # New York City Tax (single)
        ci = ti
        if ci <= 12000:
            city_tax = ci * 0.03078
        elif ci <= 25000:
            city_tax = 12000*0.03078 + (ci - 12000)*0.03762
        elif ci <= 50000:
            city_tax = 12000*0.03078 + (25000-12000)*0.03762 + (ci - 25000)*0.03819
        else:
            city_tax = (12000*0.03078 + (25000-12000)*0.03762
                        + (50000-25000)*0.03819 + (ci - 50000)*0.03876)
        total_tax += city_tax

    return total_tax


def calculate_us_expenses(loc_config, inf_multiplier):
    """Calculates US expenses including rent, healthcare, retirement contributions, etc."""
    # Housing
    rent = loc_config["rent_monthly"] * 12 * inf_multiplier
    
    # Healthcare
    healthcare = loc_config["healthcare_monthly"] * 12 * inf_multiplier
    
    # Retirement contribution (401k)
    retirement_contrib = 0  # Will be calculated based on salary
    
    # General living expenses
    general_expenses = loc_config["general_expenses_monthly"] * 12 * inf_multiplier
    
    return {
        "rent": rent,
        "healthcare": healthcare,
        "retirement_contribution": retirement_contrib,
        "general_expenses": general_expenses
    }

def calculate_us_retirement_contribution(salary, loc_config):
    """Calculates US retirement contribution (401k)."""
    return salary * loc_config["retirement_contribution"]

def calculate_us_investment_allocation(annual_net_savings):
    """Calculates US investment allocation (simplified - no UK-specific vehicles)."""
    # Simplified US investment - no specific tax-advantaged accounts modeled
    return {
        "total_investment": annual_net_savings
    } 