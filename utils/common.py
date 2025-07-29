"""
Common Utilities Module
Shared functions used across different tax jurisdictions and scenarios.
"""

def calculate_inflation_multiplier(year, config):
    """Calculates inflation multiplier using OBR-aligned path."""
    inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
    return (1 + inflation_rate)

def convert_usd_to_gbp(usd_amount, exchange_rate):
    """Converts USD amount to GBP using exchange rate."""
    return usd_amount / exchange_rate

def convert_gbp_to_usd(gbp_amount, exchange_rate):
    """Converts GBP amount to USD using exchange rate."""
    return gbp_amount * exchange_rate

def calculate_mortgage_payment(principal, annual_rate, term_years):
    """Calculates monthly mortgage payment."""
    monthly_rate = annual_rate / 12
    num_payments = term_years * 12
    
    if monthly_rate > 0:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
        return monthly_payment
    else:
        return principal / num_payments

def calculate_house_equity(house_value, mortgage_balance):
    """Calculates house equity (value minus mortgage balance)."""
    return max(0, house_value - mortgage_balance)

def validate_config(config):
    """Validates configuration parameters."""
    required_keys = [
        "start_year", "plan_duration_years", "inflation_rate", "investment_return_rate",
        "start_age", "student_loan_debt", "tax_bands", "tax_rates", "ni_bands", "ni_rates",
        "student_loan_plan2", "isa_allowance", "lisa_allowance", "sipp_allowance"
    ]
    
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")
    
    return True

def format_currency(amount, currency="GBP"):
    """Formats currency amount with proper formatting."""
    if currency == "GBP":
        return f"£{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.0f}"
    else:
        return f"{amount:,.0f}" 