"""
Scenario Helper Functions
Common functionality used across different financial scenarios.
"""

from .uk_tax import calculate_uk_investment_allocation
from .us_tax import calculate_us_expenses, calculate_us_retirement_contribution
from .uae_tax import calculate_uae_expenses
from .common import calculate_mortgage_payment, convert_usd_to_gbp

def initialize_scenario_state(config):
    """Initialize common state variables for all scenarios."""
    return {
        "cumulative_investments": 0,
        "student_loan_balance": config["student_loan_debt"],
        "rsu_grants": [],
        "unvested_equity_value": 0,
        "house_equity": 0,
        "mortgage_balance": 0,
        "house_value": 0,
        # International housing state variables
        "uk_house_value": 0,
        "uk_mortgage_balance": 0,
        "uk_house_equity": 0,
        "local_house_value": 0,
        "local_mortgage_balance": 0,
        "local_house_equity": 0
    }

def calculate_parental_home_price(config):
    """Calculate parental home price with growth projections."""
    parental_home_price = config["parental_home_purchase"]["base_price_2025"]
    for growth in config["parental_home_purchase"]["price_grows"]:
        parental_home_price *= (1 + growth)
    return parental_home_price

def calculate_uk_salary_progression(plan_year, scenario_type):
    """Calculate UK salary based on scenario type and year."""
    if scenario_type == 'A':
        if plan_year <= 1: return 55000
        elif plan_year <= 2: return 67500
        elif plan_year <= 5: return 80000
        else: return 115000
    elif scenario_type == 'B':
        if plan_year <= 1: return 55000
        elif plan_year <= 2: return 67500
        else:
            if plan_year == 3: return 98182
            else: return 98182 * (1.125 ** (plan_year - 3))
    return 0

def calculate_uk_bonus(salary, scenario_type, plan_year):
    """Calculate UK bonus based on scenario type."""
    if scenario_type == 'A':
        return salary * 0.125
    elif scenario_type == 'B':
        if plan_year <= 2: return salary * 0.125
        else: return salary * 0.10
    return 0

def calculate_rsu_vesting_scenario_a(plan_year, salary, rsu_grants, ipo_multiplier):
    """Calculate RSU vesting for Scenario A."""
    # Add new RSU grant if starting from Year 3
    if plan_year >= 3:
        rsu_grants.append({
            "grant_year": plan_year, 
            "annual_vest_value": salary * 0.20 / 4, 
            "vesting_end_year": plan_year + 3
        })
    
    # Calculate vested value
    current_vesting_tranches = [g for g in rsu_grants if plan_year >= g["grant_year"]]
    rsu_vested_value = sum(g["annual_vest_value"] for g in current_vesting_tranches) * ipo_multiplier
    
    # Calculate unvested equity value
    unvested_equity_value = 0
    for g in rsu_grants:
        remaining_vests = max(0, g["vesting_end_year"] - plan_year + 1)
        unvested_equity_value += g["annual_vest_value"] * remaining_vests * ipo_multiplier
    
    return rsu_vested_value, unvested_equity_value

def calculate_rsu_vesting_scenario_b(plan_year, rsu_grants):
    """Calculate RSU vesting for Scenario B."""
    rsu_vested_value = 0
    unvested_equity_value = 0
    
    if rsu_grants:
        grant = rsu_grants[0]  # Assuming single grant for scenario B
        
        if plan_year >= grant["vest_cliff_year"]:
            # Determine valuation multiplier
            years_since_grant = plan_year - grant["grant_year"]
            if years_since_grant <= 1: 
                valuation_multiplier = 1.0
            elif years_since_grant == 2: 
                valuation_multiplier = 2.0
            else: 
                valuation_multiplier = 5.0
            
            # Calculate vested amount (quarterly vesting after cliff)
            if plan_year < grant["vesting_end_year"]:
                quarters_vested = min(4, plan_year - grant["vest_cliff_year"] + 1)
                rsu_vested_value = (grant["total_value"] / 4) * quarters_vested * valuation_multiplier
        
        # Calculate unvested equity value
        remaining_vests = max(0, grant["vesting_end_year"] - plan_year)
        if remaining_vests > 0:
            future_valuation = 5.0
            unvested_equity_value = (grant["total_value"] / 4) * remaining_vests * future_valuation
    
    return rsu_vested_value, unvested_equity_value

def calculate_mortgage_and_house_equity(plan_year, parental_home_price, config, state, inflation_rate):
    """Calculate mortgage payment and house equity."""
    mortgage_payment = 0
    
    if plan_year >= config["parental_home_purchase"]["target_year"] + 1:
        mortgage_amount = parental_home_price * (1 - config["parental_home_purchase"]["deposit_pct"])
        annual_rate = config["parental_home_purchase"]["mortgage_rate"]
        term_years = config["parental_home_purchase"]["mortgage_term_years"]
        monthly_payment = calculate_mortgage_payment(mortgage_amount, annual_rate, term_years)
        mortgage_payment = monthly_payment * 12
        
        # Track house equity
        if plan_year == config["parental_home_purchase"]["target_year"] + 1:
            # House is purchased at start of this year
            state["house_value"] = parental_home_price
            state["mortgage_balance"] = mortgage_amount
            state["house_equity"] = parental_home_price * config["parental_home_purchase"]["deposit_pct"]
        else:
            # House value appreciates with inflation
            state["house_value"] *= (1 + inflation_rate)
            # Reduce mortgage balance by principal portion of payment
            if state["mortgage_balance"] > 0:
                interest_paid = state["mortgage_balance"] * config["parental_home_purchase"]["mortgage_rate"]
                principal_paid = mortgage_payment - interest_paid
                state["mortgage_balance"] = max(0, state["mortgage_balance"] - principal_paid)
                state["house_equity"] = state["house_value"] - state["mortgage_balance"]
    
    return mortgage_payment

def calculate_international_housing(plan_year, location, loc_config, state, inflation_rate, housing_strategy):
    """Calculate housing costs and equity for international scenarios."""
    mortgage_payment = 0
    house_equity = 0
    
    if housing_strategy == "uk_home":
        # Buy UK home (parents live there)
        uk_home_config = loc_config["housing_options"]["uk_home"]
        if plan_year >= uk_home_config["purchase_year"] + 1:
            # Calculate UK home price with growth
            uk_home_price = uk_home_config["price_gbp"]
            for i, growth in enumerate(uk_home_config["price_growth"]):
                if i < plan_year - uk_home_config["purchase_year"]:
                    uk_home_price *= (1 + growth)
            
            mortgage_amount = uk_home_price * (1 - uk_home_config["deposit_pct"])
            annual_rate = uk_home_config["mortgage_rate"]
            term_years = uk_home_config["mortgage_term_years"]
            monthly_payment = calculate_mortgage_payment(mortgage_amount, annual_rate, term_years)
            mortgage_payment = monthly_payment * 12
            
            # Track house equity
            if plan_year == uk_home_config["purchase_year"] + 1:
                state["uk_house_value"] = uk_home_price
                state["uk_mortgage_balance"] = mortgage_amount
                state["uk_house_equity"] = uk_home_price * uk_home_config["deposit_pct"]
            else:
                # House value appreciates with inflation
                state["uk_house_value"] *= (1 + inflation_rate)
                # Reduce mortgage balance by principal portion of payment
                if state["uk_mortgage_balance"] > 0:
                    interest_paid = state["uk_mortgage_balance"] * uk_home_config["mortgage_rate"]
                    principal_paid = mortgage_payment - interest_paid
                    state["uk_mortgage_balance"] = max(0, state["uk_mortgage_balance"] - principal_paid)
                    state["uk_house_equity"] = state["uk_house_value"] - state["uk_mortgage_balance"]
            
            house_equity = state.get("uk_house_equity", 0)
            
    elif housing_strategy == "local_home":
        # Buy local home in the new country
        local_home_config = loc_config["housing_options"]["local_home"]
        if plan_year >= local_home_config["purchase_year"] + 1:
            # Calculate local home price with growth
            local_home_price = local_home_config["price_usd"]
            for i, growth in enumerate(local_home_config["price_growth"]):
                if i < plan_year - local_home_config["purchase_year"]:
                    local_home_price *= (1 + growth)
            
            mortgage_amount = local_home_price * (1 - local_home_config["deposit_pct"])
            annual_rate = local_home_config["mortgage_rate"]
            term_years = local_home_config["mortgage_term_years"]
            monthly_payment = calculate_mortgage_payment(mortgage_amount, annual_rate, term_years)
            mortgage_payment = monthly_payment * 12
            
            # Track house equity
            if plan_year == local_home_config["purchase_year"] + 1:
                state["local_house_value"] = local_home_price
                state["local_mortgage_balance"] = mortgage_amount
                state["local_house_equity"] = local_home_price * local_home_config["deposit_pct"]
            else:
                # House value appreciates with inflation
                state["local_house_value"] *= (1 + inflation_rate)
                # Reduce mortgage balance by principal portion of payment
                if state["local_mortgage_balance"] > 0:
                    interest_paid = state["local_mortgage_balance"] * local_home_config["mortgage_rate"]
                    principal_paid = mortgage_payment - interest_paid
                    state["local_mortgage_balance"] = max(0, state["local_mortgage_balance"] - principal_paid)
                    state["local_house_equity"] = state["local_house_value"] - state["local_mortgage_balance"]
            
            house_equity = state.get("local_house_equity", 0)
    
    return mortgage_payment, house_equity

def calculate_international_expenses(location, loc_config, inf_multiplier, salary):
    """Calculate international expenses including housing costs."""
    # Base expenses
    rent = loc_config["rent_monthly"] * 12 * inf_multiplier
    healthcare = loc_config["healthcare_monthly"] * 12 * inf_multiplier
    retirement_contrib = salary * loc_config["retirement_contribution"]
    general_expenses = loc_config["general_expenses_monthly"] * 12 * inf_multiplier
    
    return {
        "rent": rent,
        "healthcare": healthcare,
        "retirement_contrib": retirement_contrib,
        "general_expenses": general_expenses
    }

def calculate_uk_investment_growth(annual_net_savings, config, state):
    """Calculate UK investment growth and allocation."""
    # Investment Allocation
    investment_allocation = calculate_uk_investment_allocation(annual_net_savings, config)
    lisa_contr = investment_allocation["lisa"]
    isa_contr = investment_allocation["isa"]
    sipp_contr = investment_allocation["sipp"]
    gia_contr = investment_allocation["gia"]
    lisa_bonus = investment_allocation["lisa_bonus"]
    
    # Portfolio Growth
    state["cumulative_investments"] *= (1 + config["investment_return_rate"])
    state["cumulative_investments"] += (lisa_contr + lisa_bonus + isa_contr + sipp_contr + gia_contr)
    state["cumulative_investments"] = max(0, state["cumulative_investments"])
    
    return {
        "lisa_contr": lisa_contr,
        "isa_contr": isa_contr,
        "sipp_contr": sipp_contr,
        "gia_contr": gia_contr,
        "lisa_bonus": lisa_bonus
    }

def convert_to_gbp_for_comparison(data_dict, exchange_rate):
    """Convert USD amounts to GBP for comparison."""
    return {
        "gbp_net_worth": convert_usd_to_gbp(data_dict["net_worth"], exchange_rate),
        "gbp_gross_income": convert_usd_to_gbp(data_dict["gross_income"], exchange_rate),
        "gbp_net_income": convert_usd_to_gbp(data_dict["net_income"], exchange_rate),
        "gbp_total_expenses": convert_usd_to_gbp(data_dict["total_expenses"], exchange_rate),
        "gbp_annual_savings": convert_usd_to_gbp(data_dict["annual_net_savings"], exchange_rate),
        "gbp_cumulative_portfolio": convert_usd_to_gbp(data_dict["cumulative_investments"], exchange_rate)
    } 