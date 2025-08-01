"""
UK Tax Utilities Module
Handles all UK-specific tax calculations including Income Tax, National Insurance, and Student Loan repayments.
"""

def calculate_uk_tax_ni(gross_income, year, config):
    """Calculates UK Income Tax and National Insurance for a given year."""
    # Adjust thresholds for inflation after the freeze
    if year >= config["tax_bands"]["threshold_freeze_until"]:
        inflation_multiplier = (1 + config["inflation_rate"]) ** (year - config["tax_bands"]["threshold_freeze_until"])
        pa = config["tax_bands"]["personal_allowance"] * inflation_multiplier
        br_limit = config["tax_bands"]["basic_rate_limit"] * inflation_multiplier
        hr_limit = config["tax_bands"]["higher_rate_limit"] * inflation_multiplier
        pa_taper_threshold = config["tax_bands"]["pa_taper_threshold"] * inflation_multiplier
    else:
        pa = config["tax_bands"]["personal_allowance"]
        br_limit = config["tax_bands"]["basic_rate_limit"]
        hr_limit = config["tax_bands"]["higher_rate_limit"]
        pa_taper_threshold = config["tax_bands"]["pa_taper_threshold"]
    
    # Personal Allowance Taper
    if gross_income > pa_taper_threshold:
        taper_amount = (gross_income - pa_taper_threshold) / 2
        pa = max(0, pa - taper_amount)
    
    taxable_income = max(0, gross_income - pa)
    tax = 0
    
    # Income Tax
    if taxable_income > 0:
        if taxable_income > hr_limit - pa:
            tax += (taxable_income - (hr_limit - pa)) * config["tax_rates"]["additional"]
            taxable_income = hr_limit - pa
        if taxable_income > br_limit - pa:
            tax += (taxable_income - (br_limit - pa)) * config["tax_rates"]["higher"]
            taxable_income = br_limit - pa
        tax += taxable_income * config["tax_rates"]["basic"]

    # National Insurance
    ni = 0
    if gross_income > config["ni_bands"]["primary_threshold"]:
        niable_income_main = min(gross_income, config["ni_bands"]["upper_earnings_limit"]) - config["ni_bands"]["primary_threshold"]
        ni += max(0, niable_income_main) * config["ni_rates"]["main"]
    if gross_income > config["ni_bands"]["upper_earnings_limit"]:
        niable_income_upper = gross_income - config["ni_bands"]["upper_earnings_limit"]
        ni += niable_income_upper * config["ni_rates"]["upper"]

    return tax, ni

def calculate_uk_student_loan(gross_income, loan_balance, config):
    """Calculates Plan 2 student loan repayment and interest."""
    p2 = config["student_loan_plan2"]
    
    # Repayment
    repayment = 0
    if gross_income > p2["threshold"]:
        repayment = (gross_income - p2["threshold"]) * p2["repayment_rate"]
    
    # Interest
    if gross_income <= p2["interest_lower_income_threshold"]:
        interest_rate = p2["interest_rate_rpi"]
    elif gross_income >= p2["interest_upper_income_threshold"]:
        interest_rate = p2["interest_rate_rpi"] + p2["interest_rate_max_premium"]
    else:
        # Linear scaling
        income_range = p2["interest_upper_income_threshold"] - p2["interest_lower_income_threshold"]
        premium = (gross_income - p2["interest_lower_income_threshold"]) / income_range * p2["interest_rate_max_premium"]
        interest_rate = p2["interest_rate_rpi"] + premium
        
    interest_accrued = loan_balance * interest_rate
    new_balance = loan_balance + interest_accrued - repayment
    
    return repayment, new_balance

def calculate_uk_investment_allocation(annual_net_savings, config):
    """Calculates UK investment allocation across ISA, LISA, SIPP, and GIA."""
    # Investment Allocation - LISA and ISA are separate allowances
    lisa_contr = min(max(0, annual_net_savings), config["lisa_allowance"])
    remaining_savings = max(0, annual_net_savings - lisa_contr)
    
    # ISA gets full allowance (separate from LISA)
    isa_contr = min(remaining_savings, config["isa_allowance"])
    remaining_savings -= isa_contr
    
    # Simple SIPP logic for overflow, a real plan would optimize for the 60% band
    sipp_contr = min(remaining_savings, config["sipp_allowance"])
    remaining_savings -= sipp_contr
    
    gia_contr = remaining_savings
    
    return {
        "lisa": lisa_contr,
        "isa": isa_contr,
        "sipp": sipp_contr,
        "gia": gia_contr,
        "lisa_bonus": lisa_contr * config["lisa_bonus_rate"]
    }

def calculate_uk_expenses(loc_config, inf_multiplier):
    """Calculates UK location-specific expenses including rent, healthcare, etc."""
    # Housing
    rent = loc_config["rent_monthly"] * 12 * inf_multiplier
    
    # Healthcare (NHS is free, but private healthcare costs)
    healthcare = loc_config["healthcare_monthly"] * 12 * inf_multiplier
    
    # Retirement contribution (pension)
    retirement_contrib = 0  # Will be calculated based on salary
    
    # General living expenses
    general_expenses = loc_config["general_expenses_monthly"] * 12 * inf_multiplier
    
    return {
        "rent": rent,
        "healthcare": healthcare,
        "retirement_contribution": retirement_contrib,
        "general_expenses": general_expenses
    } 