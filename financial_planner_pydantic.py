"""
Financial Planner with Pydantic Models
Uses consistent data structures defined with Pydantic for all scenarios.
"""

import pandas as pd
from config import CONFIG
from models import (
    FinancialScenario, 
    create_uk_data_point,
    create_international_data_point
)
from utils import (
    calculate_uk_tax_ni,
    calculate_uk_student_loan,
    calculate_uk_expenses,
    calculate_us_tax,
    calculate_inflation_multiplier,
    convert_gbp_to_usd,
    # Helper functions
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


def run_scenario_pydantic(scenario_type: str, config: dict) -> FinancialScenario:
    """Run UK scenario using Pydantic models for consistent data structure."""
    
    scenario = FinancialScenario(name=f"UK_Scenario_{scenario_type}")
    
    # Initialize data tracking
    years = list(range(config["start_year"], config["start_year"] + config["plan_duration_years"]))
    
    # Initialize state using helper function
    state = initialize_scenario_state(config)
    
    # Pre-calculate parental home price using helper function
    parental_home_price = calculate_parental_home_price(config)
    
    for i, year in enumerate(years):
        plan_year = i + 1
        age = config["start_age"] + i
        
        # --- Income Calculation ---
        salary = calculate_uk_salary_progression(plan_year, scenario_type)
        bonus = calculate_uk_bonus(salary, scenario_type, plan_year)
        
        # RSU calculations using helper functions
        if scenario_type == 'A':
            ipo_multiplier = 2.0 if plan_year == 4 else 1.0
            rsu_vested_value, state["unvested_equity_value"] = calculate_rsu_vesting_scenario_a(
                plan_year, salary, state["rsu_grants"], ipo_multiplier
            )
        elif scenario_type == 'B':
            if plan_year == 3:
                state["rsu_grants"].append({
                    "grant_year": plan_year, 
                    "total_value": 30000, 
                    "vest_cliff_year": plan_year + 1, 
                    "vesting_end_year": plan_year + 4
                })
            rsu_vested_value, state["unvested_equity_value"] = calculate_rsu_vesting_scenario_b(
                plan_year, state["rsu_grants"]
            )
        
        gross_income = salary + bonus + rsu_vested_value
        
        # --- UK Tax and Deductions ---
        tax, ni = calculate_uk_tax_ni(gross_income, year, config)
        sl_repayment, state["student_loan_balance"] = calculate_uk_student_loan(
            gross_income, state["student_loan_balance"], config
        )
        net_income = gross_income - tax - ni - sl_repayment
        
        # --- Expenses ---
        inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
        inf_multiplier = calculate_inflation_multiplier(year, config)
        
        expenses = calculate_uk_expenses(plan_year, year, config, inf_multiplier)
        
        # --- Mortgage and House Equity ---
        mortgage_payment = calculate_mortgage_and_house_equity(
            plan_year, parental_home_price, config, state, inflation_rate
        )
        
        total_expenses = (expenses["personal"] + expenses["parental_support"] + 
                         expenses["travel"] + expenses["rent"] + expenses["university_payment"] +
                         expenses["marriage"] + expenses["child"] + mortgage_payment)
        
        # --- Savings & Investments ---
        annual_net_savings = net_income - total_expenses
        
        # Investment growth using helper function
        investment_breakdown = calculate_uk_investment_growth(annual_net_savings, config, state)
        
        # Total net worth including house equity
        net_worth = state["cumulative_investments"] + state["unvested_equity_value"] + state["house_equity"]
        
        # Create data point using Pydantic model
        data_point = create_uk_data_point(
            year=plan_year,
            age=age,
            salary=salary,
            bonus=bonus,
            rsu_vested=rsu_vested_value,
            gross_income=gross_income,
            net_income=net_income,
            total_expenses=total_expenses,
            annual_savings=annual_net_savings,
            cumulative_portfolio=state["cumulative_investments"],
            house_equity=state["house_equity"],
            net_worth=net_worth,
            expenses=expenses,
            tax=tax,
            ni=ni,
            sl_repayment=sl_repayment,
            investment_breakdown=investment_breakdown
        )
        
        scenario.add_data_point(data_point)
    
    return scenario


def run_international_scenario_pydantic(location: str, config: dict, housing_strategy: str = "uk_home") -> FinancialScenario:
    """Run international scenario using Pydantic models."""
    
    scenario = FinancialScenario(name=f"{location.title()}_International")
    
    # Get location configuration
    loc_config = config["international_scenarios"][location]
    
    # Initialize data tracking
    years = list(range(config["start_year"], config["start_year"] + config["plan_duration_years"]))
    
    # Initialize state
    state = {"cumulative_investments": 0, "unvested_equity_value": 0}
    
    # Relocation cost (one-time in Year 1)
    relocation_cost = loc_config["relocation_cost"] if location in ["seattle", "new_york", "dubai"] else 0
    
    for i, year in enumerate(years):
        plan_year = i + 1
        age = config["start_age"] + i
        
        # --- Income (in USD) ---
        salary = loc_config["salary_progression"].get(plan_year, loc_config["salary_progression"][10])
        bonus = salary * loc_config["bonus_rate"]
        
        # RSU calculations (simplified - annual grants)
        rsu_vested_value = 0
        if plan_year >= 3:  # Start RSU grants from Year 3
            rsu_vested_value = salary * loc_config["rsu_rate"] / 4  # Quarterly vesting
        
        gross_income = salary + bonus + rsu_vested_value
        
        # --- Tax Calculations ---
        if loc_config["tax_system"] == "tax_free":
            tax = 0
        else:
            tax = calculate_us_tax(gross_income, loc_config["tax_system"], year)
        
        net_income = gross_income - tax
        
        # --- Expenses (in USD) ---
        inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
        inf_multiplier = calculate_inflation_multiplier(year, config)
        
        # Use helper function for international expenses
        expenses = calculate_international_expenses(location, loc_config, inf_multiplier, salary)
        
        # International housing costs based on strategy
        mortgage_payment, house_equity = calculate_international_housing(
            plan_year, location, loc_config, state, inflation_rate, housing_strategy
        )
        
        # Relocation cost (Year 1 only)
        relocation_expense = relocation_cost if plan_year == 1 else 0
        if relocation_expense > 0:
            relocation_expense = convert_gbp_to_usd(relocation_expense, loc_config["exchange_rate"])
        
        total_expenses = (expenses["rent"] + expenses["healthcare"] + 
                         expenses["retirement_contrib"] + expenses["general_expenses"] + 
                         relocation_expense + mortgage_payment)
        
        # --- Savings & Investments ---
        annual_net_savings = net_income - total_expenses
        
        # Portfolio growth (simplified)
        state["cumulative_investments"] *= (1 + config["investment_return_rate"])
        state["cumulative_investments"] += annual_net_savings
        state["cumulative_investments"] = max(0, state["cumulative_investments"])
        
        # Net worth including house equity
        net_worth = state["cumulative_investments"] + state["unvested_equity_value"] + house_equity
        
        # Convert to GBP for comparison using helper function
        data_dict = {
            "net_worth": net_worth,
            "gross_income": gross_income,
            "net_income": net_income,
            "total_expenses": total_expenses,
            "annual_net_savings": annual_net_savings,
            "cumulative_investments": state["cumulative_investments"]
        }
        gbp_data = convert_to_gbp_for_comparison(data_dict, loc_config["exchange_rate"])
        
        # Add relocation cost to expenses for the data point
        expenses["relocation_cost"] = relocation_expense
        expenses["mortgage_payment"] = mortgage_payment
        
        # Create data point using Pydantic model
        data_point = create_international_data_point(
            year=plan_year,
            age=age,
            salary_usd=salary,
            bonus_usd=bonus,
            rsu_vested_usd=rsu_vested_value,
            gross_income_usd=gross_income,
            net_income_usd=net_income,
            total_expenses_usd=total_expenses,
            annual_savings_usd=annual_net_savings,
            cumulative_portfolio_usd=state["cumulative_investments"],
            net_worth_usd=net_worth,
            house_equity_usd=house_equity,
            expenses_usd=expenses,
            tax_usd=tax,
            gbp_data=gbp_data,
            investment_growth_usd=annual_net_savings
        )
        
        scenario.add_data_point(data_point)
    
    return scenario


def run_delayed_relocation_scenario_pydantic(scenario_name: str, config: dict) -> FinancialScenario:
    """Run delayed relocation scenario using Pydantic models."""
    
    scenario = FinancialScenario(name=scenario_name)
    
    # Get scenario configuration
    scenario_config = config["delayed_relocation"][scenario_name]
    uk_years = scenario_config["uk_years"]
    location = scenario_config["location"]
    salary_multiplier = scenario_config["salary_multiplier"]
    housing_strategy = scenario_config["housing_strategy"]
    
    # Get location configuration
    loc_config = config["international_scenarios"][location]
    
    # Initialize data tracking
    years = list(range(config["start_year"], config["start_year"] + config["plan_duration_years"]))
    
    # Initialize state using helper function
    state = initialize_scenario_state(config)
    
    # Pre-calculate parental home price using helper function
    parental_home_price = calculate_parental_home_price(config)
    
    # Relocation cost (one-time when moving)
    relocation_cost = loc_config["relocation_cost"]
    
    for i, year in enumerate(years):
        plan_year = i + 1
        age = config["start_age"] + i
        
        # Determine if we're in UK or international phase
        is_uk_phase = plan_year <= uk_years
        
        if is_uk_phase:
            # --- UK Phase (Years 1-2, 1-3, or 1-4) ---
            # Use UK Scenario B progression (external growth path)
            salary = calculate_uk_salary_progression(plan_year, 'B')
            bonus = calculate_uk_bonus(salary, 'B', plan_year)
            
            # RSU Vesting with valuation growth
            if plan_year == 3:
                state["rsu_grants"].append({
                    "grant_year": plan_year, 
                    "total_value": 30000, 
                    "vest_cliff_year": plan_year + 1, 
                    "vesting_end_year": plan_year + 4
                })
            
            rsu_vested_value, state["unvested_equity_value"] = calculate_rsu_vesting_scenario_b(
                plan_year, state["rsu_grants"]
            )
            
            gross_income = salary + bonus + rsu_vested_value
            
            # UK tax calculations
            tax, ni = calculate_uk_tax_ni(gross_income, year, config)
            sl_repayment, state["student_loan_balance"] = calculate_uk_student_loan(
                gross_income, state["student_loan_balance"], config
            )
            net_income = gross_income - tax - ni - sl_repayment
            
            # UK expenses
            inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
            inf_multiplier = calculate_inflation_multiplier(year, config)
            
            expenses = calculate_uk_expenses(plan_year, year, config, inf_multiplier)
            
            # Mortgage payment for parents using helper function
            mortgage_payment = calculate_mortgage_and_house_equity(
                plan_year, parental_home_price, config, state, inflation_rate
            )
            
            total_expenses = (expenses["personal"] + expenses["parental_support"] + 
                             expenses["travel"] + expenses["rent"] + expenses["university_payment"] +
                             expenses["marriage"] + expenses["child"] + mortgage_payment)
            
            # UK investment allocation using helper function
            annual_net_savings = net_income - total_expenses
            investment_breakdown = calculate_uk_investment_growth(annual_net_savings, config, state)
            
            net_worth = state["cumulative_investments"] + state["unvested_equity_value"] + state["house_equity"]
            
            # Create UK data point
            data_point = create_uk_data_point(
                year=plan_year,
                age=age,
                salary=salary,
                bonus=bonus,
                rsu_vested=rsu_vested_value,
                gross_income=gross_income,
                net_income=net_income,
                total_expenses=total_expenses,
                annual_savings=annual_net_savings,
                cumulative_portfolio=state["cumulative_investments"],
                house_equity=state["house_equity"],
                net_worth=net_worth,
                expenses=expenses,
                tax=tax,
                ni=ni,
                sl_repayment=sl_repayment,
                investment_breakdown=investment_breakdown
            )
            
        else:
            # --- International Phase (After UK years) ---
            int_plan_year = plan_year - uk_years
            
            # Get salary with experience multiplier
            base_salary = loc_config["salary_progression"].get(int_plan_year, loc_config["salary_progression"][10])
            salary = base_salary * salary_multiplier
            bonus = salary * loc_config["bonus_rate"]
            
            # RSU calculations
            rsu_vested_value = 0
            if int_plan_year >= 1:  # Start RSU grants from first international year
                rsu_vested_value = salary * loc_config["rsu_rate"] / 4
            
            gross_income = salary + bonus + rsu_vested_value
            
            # International tax calculations
            if loc_config["tax_system"] == "tax_free":
                tax = 0
            else:
                tax = calculate_us_tax(gross_income, loc_config["tax_system"], year)
            
            net_income = gross_income - tax
            
            # International expenses using helper function
            inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
            inf_multiplier = calculate_inflation_multiplier(year, config)
            
            expenses = calculate_international_expenses(location, loc_config, inf_multiplier, salary)
            
            # International housing costs based on strategy
            mortgage_payment, house_equity = calculate_international_housing(
                plan_year, location, loc_config, state, inflation_rate, housing_strategy
            )
            
            # Relocation cost only in first international year
            relocation_expense = relocation_cost if int_plan_year == 1 else 0
            if relocation_expense > 0:
                relocation_expense = convert_gbp_to_usd(relocation_expense, loc_config["exchange_rate"])
            
            total_expenses = (expenses["rent"] + expenses["healthcare"] + 
                             expenses["retirement_contrib"] + expenses["general_expenses"] + 
                             relocation_expense + mortgage_payment)
            
            # International investment (simplified)
            annual_net_savings = net_income - total_expenses
            state["cumulative_investments"] *= (1 + config["investment_return_rate"])
            state["cumulative_investments"] += annual_net_savings
            state["cumulative_investments"] = max(0, state["cumulative_investments"])
            
            # Net worth including house equity
            net_worth = state["cumulative_investments"] + state["unvested_equity_value"] + house_equity
            
            # Convert to GBP for comparison using helper function
            data_dict = {
                "net_worth": net_worth,
                "gross_income": gross_income,
                "net_income": net_income,
                "total_expenses": total_expenses,
                "annual_net_savings": annual_net_savings,
                "cumulative_investments": state["cumulative_investments"]
            }
            gbp_data = convert_to_gbp_for_comparison(data_dict, loc_config["exchange_rate"])
            
            # Add relocation cost to expenses for the data point
            expenses["relocation_cost"] = relocation_expense
            expenses["mortgage_payment"] = mortgage_payment
            
            # Create International data point
            data_point = create_international_data_point(
                year=plan_year,
                age=age,
                salary_usd=salary,
                bonus_usd=bonus,
                rsu_vested_usd=rsu_vested_value,
                gross_income_usd=gross_income,
                net_income_usd=net_income,
                total_expenses_usd=total_expenses,
                annual_savings_usd=annual_net_savings,
                cumulative_portfolio_usd=state["cumulative_investments"],
                net_worth_usd=net_worth,
                house_equity_usd=house_equity,
                expenses_usd=expenses,
                tax_usd=tax,
                gbp_data=gbp_data,
                investment_growth_usd=annual_net_savings
            )
        
        scenario.add_data_point(data_point)
    
    return scenario


if __name__ == '__main__':
    # Test the Pydantic-based functions
    print("Testing Pydantic-based financial planner...")
    
    # Test UK scenarios
    scenario_a = run_scenario_pydantic('A', CONFIG)
    scenario_b = run_scenario_pydantic('B', CONFIG)
    
    print(f"Scenario A Final Net Worth: £{scenario_a.get_final_net_worth():,.0f}")
    print(f"Scenario B Final Net Worth: £{scenario_b.get_final_net_worth():,.0f}")
    
    # Test international scenario
    dubai_scenario = run_international_scenario_pydantic('dubai', CONFIG)
    print(f"Dubai Final Net Worth: £{dubai_scenario.get_final_net_worth():,.0f}")
    
    # Test delayed relocation scenario
    delayed_scenario = run_delayed_relocation_scenario_pydantic('dubai_year4_local_home', CONFIG)
    print(f"Delayed Dubai Year 4 Final Net Worth: £{delayed_scenario.get_final_net_worth():,.0f}")
    
    print("✅ All Pydantic-based functions working correctly!") 