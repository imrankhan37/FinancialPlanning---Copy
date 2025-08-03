"""
Centralized Tax Utilities
Provides unified tax calculation functions that use location-specific tax modules.
"""

from typing import Dict, Tuple, Any
import sys
import os

# Import tax modules from the same directory
from .uk_tax import calculate_uk_tax_ni, calculate_uk_student_loan
from .us_tax import calculate_us_tax
from .uae_tax import calculate_uae_tax
from models.unified_financial_data import TaxExpenses, CurrencyValue, Currency
from models.unified_helpers import optimize_currency_value_creation

# Import YAML support for enhanced tax calculations
from pathlib import Path
config_dir = Path(__file__).parent.parent.parent / "config"
if str(config_dir) not in sys.path:
    sys.path.insert(0, str(config_dir))

try:
    from yaml_loader import try_load_tax_system
    YAML_TAX_SUPPORT = True
except ImportError:
    YAML_TAX_SUPPORT = False


def calculate_tax_for_location(
    gross_income: float,
    location: str,
    year: int,
    config: Dict[str, Any],
    loan_balance: float = 0.0
) -> Tuple[float, float, float]:
    """
    Calculate total tax for a given location using the appropriate tax module.
    
    Args:
        gross_income: Annual gross income
        location: Location string ('UK', 'seattle', 'new_york', 'dubai')
        year: Tax year
        config: Configuration dictionary
        loan_balance: Student loan balance (for UK)
    
    Returns:
        Tuple of (income_tax, social_security, total_tax)
    """
    
    # Calculate student loan repayment for all locations since UK student loans
    # follow the same repayment rules regardless of location
    student_loan_repayment, _ = calculate_uk_student_loan(gross_income, loan_balance, config)
    
    if location == "UK":
        # Use UK tax calculations
        income_tax, ni = calculate_uk_tax_ni(gross_income, year, config)
        total_tax = income_tax + ni + student_loan_repayment
        return income_tax, ni, total_tax
        
    elif location in ["seattle", "new_york"]:
        # Use US tax calculations
        tax_system = "us_federal_state" if location == "seattle" else "us_federal_state_city"
        total_tax = calculate_us_tax(gross_income, tax_system, year)
        
        # Split into income tax and social security (FICA)
        # This is a simplified split - in reality FICA is separate from income tax
        fica_rate = 0.0765  # 6.2% SS + 1.45% Medicare
        fica_tax = min(gross_income, 176100) * 0.062 + gross_income * 0.0145  # 2025 limits
        income_tax = total_tax - fica_tax
        
        total_tax += student_loan_repayment
        return income_tax, fica_tax, total_tax
        
    elif location == "dubai":
        # Use UAE tax calculations (tax-free)
        total_tax = calculate_uae_tax(gross_income)
        total_tax += student_loan_repayment
        return 0.0, 0.0, total_tax
        
    else:
        # Fallback for unknown locations
        total_tax = student_loan_repayment
        return 0.0, 0.0, total_tax


def get_tax_breakdown_for_location(
    gross_income: float,
    location: str,
    year: int,
    config: Dict[str, Any],
    loan_balance: float = 0.0
) -> TaxExpenses:
    """
    Get detailed tax breakdown for a location using actual tax calculations.
    
    Args:
        gross_income: Annual gross income
        location: Location string
        year: Tax year
        config: Configuration dictionary
        loan_balance: Student loan balance (for UK)
    
    Returns:
        TaxExpenses object with detailed breakdown
    """
    
    income_tax, social_security, total_tax = calculate_tax_for_location(
        gross_income, location, year, config, loan_balance
    )
    
    # Calculate property tax (simplified - could be enhanced with actual property values)
    property_tax = 0.0
    if location == "UK":
        # UK has council tax but it's not income-based
        property_tax = 0.0
    elif location in ["seattle", "new_york"]:
        # US property tax is based on property value, not income
        property_tax = 0.0
    elif location == "dubai":
        # Dubai has no property tax
        property_tax = 0.0
    
    # Calculate other taxes
    other_taxes = total_tax - income_tax - social_security - property_tax
    
    # Create currency values based on location
    if location == "UK":
        currency = Currency.GBP
        exchange_rate = 1.0
    elif location in ["seattle", "new_york", "dubai"]:
        currency = Currency.USD
        exchange_rate = config.get("international_scenarios", {}).get(location, {}).get("exchange_rate", 1.26)
    else:
        currency = Currency.GBP
        exchange_rate = 1.0
    
    return TaxExpenses(
        income_tax=optimize_currency_value_creation(income_tax, currency, exchange_rate),
        social_security=optimize_currency_value_creation(social_security, currency, exchange_rate),
        property_tax=optimize_currency_value_creation(property_tax, currency, exchange_rate),
        other_taxes=optimize_currency_value_creation(other_taxes, currency, exchange_rate)
    )


def get_tax_multiplier_for_location(location: str, config: Dict[str, Any]) -> float:
    """
    Get tax multiplier for a location to adjust unified breakdowns.
    
    Args:
        location: Location string
        config: Configuration dictionary
    
    Returns:
        Tax multiplier (0.0 for tax-free, 1.0 for normal, etc.)
    """
    
    if location == "dubai":
        return 0.0  # Tax-free
    elif location in ["seattle", "new_york"]:
        # US has higher tax rates than UK
        return 1.2  # 20% higher than UK baseline
    else:
        return 1.0  # UK baseline


def validate_tax_calculation(
    gross_income: float,
    location: str,
    year: int,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate tax calculation and return detailed breakdown for debugging.
    
    Args:
        gross_income: Annual gross income
        location: Location string
        year: Tax year
        config: Configuration dictionary
    
    Returns:
        Dictionary with validation results
    """
    
    try:
        income_tax, social_security, total_tax = calculate_tax_for_location(
            gross_income, location, year, config
        )
        
        tax_breakdown = get_tax_breakdown_for_location(
            gross_income, location, year, config
        )
        
        return {
            "success": True,
            "gross_income": gross_income,
            "location": location,
            "year": year,
            "income_tax": income_tax,
            "social_security": social_security,
            "total_tax": total_tax,
            "effective_tax_rate": total_tax / gross_income if gross_income > 0 else 0,
            "tax_breakdown": tax_breakdown
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "gross_income": gross_income,
            "location": location,
            "year": year
        }


def calculate_universal_goals(plan_year: int, config: Dict[str, Any], inf_multiplier: float) -> Dict[str, float]:
    """
    Calculate universal goal-based expenses that apply regardless of location.
    These are personal goals like marriage, children, education, etc.
    
    Args:
        plan_year: Current plan year
        config: Configuration dictionary
        inf_multiplier: Inflation multiplier
    
    Returns:
        Dictionary of universal goal expenses
    """
    expenses = {}
    
    # University fee payment (3 payments of £5,600 in Year 1 for current masters)
    uni_payment = 0
    if plan_year == config["university_fee_payment"]["year"]:
        uni_payment = config["university_fee_payment"]["amount"]
    expenses["university_payment"] = uni_payment
    
    # Goal-based expenses
    marriage_cost = 0
    if config["marriage_goal"]["start_year"] <= plan_year <= config["marriage_goal"]["end_year"]:
        marriage_cost = config["marriage_goal"]["total_cost"] / (config["marriage_goal"]["end_year"] - config["marriage_goal"]["start_year"] + 1)
    expenses["marriage"] = marriage_cost
    
    child_cost = 0
    if plan_year == config["child_costs"]["start_year"]:
        child_cost = config["child_costs"]["one_off_cost"]
    elif plan_year > config["child_costs"]["start_year"]:
        child_cost = config["child_costs"]["ongoing_annual_cost"] * inf_multiplier
    expenses["child"] = child_cost
    
    # Personal expenses (location-independent)
    personal_expenses = config["personal_expenses"].get(plan_year, config["personal_expenses"]["default"]) * inf_multiplier
    expenses["personal"] = personal_expenses
    
    # Parental support (location-independent)
    parental_support = (config["parental_support"]["after_house"] if plan_year >= config["parental_support"]["house_purchase_year"] else config["parental_support"]["before_house"]) * inf_multiplier
    expenses["parental_support"] = parental_support
    
    # Travel (location-independent)
    travel = config["annual_travel"] * inf_multiplier
    expenses["travel"] = travel
    
    return expenses


# ===== WEEK 3: YAML TAX CALCULATION FUNCTIONS =====

def calculate_yaml_tax_for_location(
    gross_income: float,
    tax_system_id: str,
    year: int,
    loan_balance: float = 0.0
) -> Dict[str, float]:
    """
    Calculate tax using YAML tax system configuration.
    
    Args:
        gross_income: Annual gross income in GBP
        tax_system_id: YAML tax system identifier (e.g., 'uk_income_tax_ni')
        year: Tax year
        loan_balance: Student loan balance (for UK)
    
    Returns:
        Dictionary with tax breakdown: {
            'income_tax': float,
            'social_security': float,
            'student_loan': float,
            'total_tax': float
        }
    """
    
    if not YAML_TAX_SUPPORT:
        raise ValueError("YAML tax support not available")
    
    # Load YAML tax configuration
    tax_config = try_load_tax_system(tax_system_id)
    if not tax_config:
        raise ValueError(f"Could not load tax system: {tax_system_id}")
    
    # Route to appropriate calculation based on tax system
    if tax_system_id == 'uk_income_tax_ni':
        return calculate_uk_tax_from_yaml(gross_income, tax_config, year, loan_balance)
    elif tax_system_id.startswith('us_'):
        return calculate_us_tax_from_yaml(gross_income, tax_config, year)
    elif tax_system_id == 'tax_free':
        return calculate_tax_free_from_yaml(gross_income, tax_config, year)
    else:
        raise ValueError(f"Unsupported tax system: {tax_system_id}")


def calculate_uk_tax_from_yaml(gross_income: float, tax_config: Dict[str, Any], year: int, loan_balance: float = 0.0) -> Dict[str, float]:
    """Calculate UK taxes using YAML configuration."""
    
    # Extract configuration
    income_tax_config = tax_config.get('income_tax', {})
    ni_config = tax_config.get('national_insurance', {})
    student_loan_config = tax_config.get('student_loan', {})
    
    bands = income_tax_config.get('bands', {})
    rates = income_tax_config.get('rates', {})
    ni_bands = ni_config.get('bands', {})
    ni_rates = ni_config.get('rates', {})
    
    # Adjust thresholds for inflation if needed
    threshold_freeze_until = bands.get('threshold_freeze_until', 2028)
    if year >= threshold_freeze_until:
        # For now, use static thresholds - inflation adjustment can be added later
        pass
    
    # Personal Allowance with taper
    pa = bands.get('personal_allowance', 12570)
    pa_taper_threshold = bands.get('pa_taper_threshold', 100000)
    
    if gross_income > pa_taper_threshold:
        taper_amount = (gross_income - pa_taper_threshold) / 2
        pa = max(0, pa - taper_amount)
    
    # Calculate Income Tax
    taxable_income = max(0, gross_income - pa)
    income_tax = 0
    
    basic_rate_limit = bands.get('basic_rate_limit', 50270)
    higher_rate_limit = bands.get('higher_rate_limit', 125140)
    
    basic_rate = rates.get('basic', 0.20)
    higher_rate = rates.get('higher', 0.40)
    additional_rate = rates.get('additional', 0.45)
    
    if taxable_income > 0:
        # Additional rate band
        if taxable_income > higher_rate_limit - pa:
            income_tax += (taxable_income - (higher_rate_limit - pa)) * additional_rate
            taxable_income = higher_rate_limit - pa
        
        # Higher rate band
        if taxable_income > basic_rate_limit - pa:
            income_tax += (taxable_income - (basic_rate_limit - pa)) * higher_rate
            taxable_income = basic_rate_limit - pa
        
        # Basic rate band
        income_tax += taxable_income * basic_rate
    
    # Calculate National Insurance
    primary_threshold = ni_bands.get('primary_threshold', 12570)
    upper_earnings_limit = ni_bands.get('upper_earnings_limit', 50270)
    main_rate = ni_rates.get('main', 0.08)
    upper_rate = ni_rates.get('upper', 0.02)
    
    national_insurance = 0
    if gross_income > primary_threshold:
        # Main rate band
        niable_income_main = min(gross_income, upper_earnings_limit) - primary_threshold
        national_insurance += max(0, niable_income_main) * main_rate
        
        # Upper rate band
        if gross_income > upper_earnings_limit:
            niable_income_upper = gross_income - upper_earnings_limit
            national_insurance += niable_income_upper * upper_rate
    
    # Calculate Student Loan (if applicable)
    student_loan = 0
    if loan_balance > 0 and student_loan_config:
        threshold = student_loan_config.get('threshold', 28470)
        repayment_rate = student_loan_config.get('repayment_rate', 0.09)
        
        if gross_income > threshold:
            student_loan = (gross_income - threshold) * repayment_rate
            student_loan = min(student_loan, loan_balance)  # Can't repay more than balance
    
    total_tax = income_tax + national_insurance + student_loan
    
    return {
        'income_tax': income_tax,
        'social_security': national_insurance,
        'student_loan': student_loan,
        'total_tax': total_tax
    }


def calculate_us_tax_from_yaml(gross_income: float, tax_config: Dict[str, Any], year: int) -> Dict[str, float]:
    """Calculate US taxes using YAML configuration."""
    
    # For now, use a simplified US calculation
    # This can be enhanced later with full federal + state calculations
    
    federal_config = tax_config.get('federal', {})
    state_config = tax_config.get('state', {})
    
    # Federal tax (simplified)
    federal_rate = federal_config.get('effective_rate', 0.22)  # Default 22%
    federal_tax = gross_income * federal_rate
    
    # State tax
    state_rate = state_config.get('rate', 0.0)  # Default 0% (e.g., Washington)
    state_tax = gross_income * state_rate
    
    # FICA (Social Security + Medicare)
    fica_rate = 0.0765  # 7.65% total (6.2% SS + 1.45% Medicare)
    fica_tax = gross_income * fica_rate
    
    total_tax = federal_tax + state_tax + fica_tax
    
    return {
        'income_tax': federal_tax + state_tax,
        'social_security': fica_tax,
        'student_loan': 0,
        'total_tax': total_tax
    }


def calculate_tax_free_from_yaml(gross_income: float, tax_config: Dict[str, Any], year: int) -> Dict[str, float]:
    """Calculate taxes for tax-free jurisdictions using YAML configuration."""
    
    # Tax-free jurisdictions like UAE
    return {
        'income_tax': 0,
        'social_security': 0,
        'student_loan': 0,
        'total_tax': 0
    } 