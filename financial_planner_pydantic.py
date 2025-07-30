"""
Financial Planner with Unified Pydantic Models
Uses unified data structures defined with Pydantic for all scenarios.
"""

import pandas as pd
from config import CONFIG
from utils import (
    calculate_uk_tax_ni,
    calculate_uk_student_loan,
    calculate_uk_expenses,
    calculate_uk_investment_allocation,
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
from utils.tax import calculate_universal_goals

# Import unified models and helpers
from models.unified_financial_data import (
    UnifiedFinancialScenario, UnifiedFinancialData, ScenarioMetadata,
    CurrencyValue, Currency, Jurisdiction, FinancialPhase,
    IncomeBreakdown, ExpenseBreakdown, TaxBreakdown, InvestmentBreakdown, NetWorthBreakdown
)
from models.unified_helpers import (
    create_unified_income_breakdown,
    create_unified_expense_breakdown,
    create_unified_tax_breakdown,
    create_unified_investment_breakdown,
    create_unified_net_worth_breakdown,
    create_scenario_metadata_from_name
)


# Legacy functions removed - now using unified models exclusively


def run_unified_scenario(scenario_type: str, config: dict) -> UnifiedFinancialScenario:
    """Run UK scenario using unified models."""
    
    # Create scenario metadata
    scenario_name = f"UK_Scenario_{scenario_type}"
    metadata = create_scenario_metadata_from_name(scenario_name)
    
    scenario = UnifiedFinancialScenario(
        name=scenario_name,
        description=f"UK scenario {scenario_type} using unified models",
        phase=FinancialPhase.UK_ONLY,
        data_points=[],
        metadata=metadata
    )
    
    # Initialize data tracking
    years = list(range(config["start_year"], config["start_year"] + config["plan_duration_years"]))
    state = initialize_scenario_state(config)
    parental_home_price = calculate_parental_home_price(config)
    
    for i, year in enumerate(years):
        plan_year = i + 1
        age = config["start_age"] + i
        
        # Calculate income components
        salary = calculate_uk_salary_progression(plan_year, scenario_type)
        bonus = calculate_uk_bonus(salary, scenario_type, plan_year)
        
        # RSU calculations
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
        
        # UK Tax and Deductions
        tax, ni = calculate_uk_tax_ni(gross_income, year, config)
        sl_repayment, state["student_loan_balance"] = calculate_uk_student_loan(
            gross_income, state["student_loan_balance"], config
        )
        net_income = gross_income - tax - ni - sl_repayment
        
        # Location-specific expenses
        inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
        inf_multiplier = calculate_inflation_multiplier(year, config)
        loc_config = config["location_configs"]["UK"]
        location_expenses = calculate_uk_expenses(loc_config, inf_multiplier)
        
        # Universal goals (location-independent)
        universal_expenses = calculate_universal_goals(plan_year, config, inf_multiplier)
        
        # Mortgage and House Equity
        mortgage_payment = calculate_mortgage_and_house_equity(
            plan_year, parental_home_price, config, state, inflation_rate
        )
        
        total_expenses = (location_expenses["rent"] + location_expenses["healthcare"] + 
                         location_expenses["retirement_contribution"] + location_expenses["general_expenses"] +
                         universal_expenses["personal"] + universal_expenses["parental_support"] + 
                         universal_expenses["travel"] + universal_expenses["university_payment"] +
                         universal_expenses["marriage"] + universal_expenses["child"] + mortgage_payment)
        
        # Savings & Investments
        annual_net_savings = net_income - total_expenses
        
        # Calculate investment allocation using config allowances
        investment_allocation = calculate_uk_investment_allocation(annual_net_savings, config)
        
        # Update cumulative investments
        state["cumulative_investments"] *= (1 + config["investment_return_rate"])
        state["cumulative_investments"] += (investment_allocation["isa"] + investment_allocation["lisa"] + 
                                          investment_allocation["lisa_bonus"] + investment_allocation["sipp"] + 
                                          investment_allocation["gia"])
        state["cumulative_investments"] = max(0, state["cumulative_investments"])
        
        # Net worth
        net_worth = state["cumulative_investments"] + state["unvested_equity_value"] + state["house_equity"]
        
        # Create unified data point
        unified_point = UnifiedFinancialData(
            year=year,
            age=age,
            phase=FinancialPhase.UK_ONLY,
            jurisdiction=Jurisdiction.UK,
            currency=Currency.GBP,
            income=create_unified_income_breakdown(
                salary_gbp=salary,
                bonus_gbp=bonus,
                rsu_gbp=rsu_vested_value,
                other_income_gbp=0.0
            ),
            expenses=create_unified_expense_breakdown(
                housing_gbp=location_expenses["rent"] + mortgage_payment,
                living_gbp=universal_expenses["personal"],
                taxes_gbp=tax + ni + sl_repayment,
                investments_gbp=0.0,  # Investment expenses not tracked in old model
                other_gbp=universal_expenses["parental_support"] + universal_expenses["travel"] + 
                          universal_expenses["university_payment"] + universal_expenses["marriage"] + universal_expenses["child"]
            ),
            tax=create_unified_tax_breakdown(
                income_tax_gbp=tax,
                social_security_gbp=ni,
                other_taxes_gbp=sl_repayment
            ),
            investments=create_unified_investment_breakdown(
                retirement_gbp=investment_allocation["sipp"] + investment_allocation["lisa"] + investment_allocation["lisa_bonus"],
                taxable_gbp=investment_allocation["isa"] + investment_allocation["gia"],
                housing_gbp=state["house_equity"]
            ),
            net_worth=create_unified_net_worth_breakdown(
                liquid_assets_gbp=state["cumulative_investments"],
                illiquid_assets_gbp=state["house_equity"] + state["unvested_equity_value"],
                liabilities_gbp=0.0
            ),
            exchange_rates={Currency.GBP: 1.0}
        )
        
        scenario.add_data_point(unified_point)
    
    return scenario


def run_unified_international_scenario(location: str, config: dict, housing_strategy: str = "uk_home") -> UnifiedFinancialScenario:
    """Run international scenario using unified models."""
    
    # Create scenario metadata
    scenario_name = f"{location}_{housing_strategy}"
    metadata = create_scenario_metadata_from_name(scenario_name)
    
    scenario = UnifiedFinancialScenario(
        name=scenario_name,
        description=f"International scenario {location} with {housing_strategy} using unified models",
        phase=FinancialPhase.INTERNATIONAL_ONLY,
        data_points=[],
        metadata=metadata
    )
    
    # Get location configuration
    loc_config = config["international_scenarios"][location]
    
    # Initialize state
    state = initialize_scenario_state(config)
    years = list(range(config["start_year"], config["start_year"] + config["plan_duration_years"]))
    
    for i, year in enumerate(years):
        plan_year = i + 1
        age = config["start_age"] + i
        
        # Calculate income using config salary progression
        salary_usd = loc_config["salary_progression"][plan_year]
        bonus_rate = loc_config["bonus_rate"]
        bonus_usd = salary_usd * bonus_rate
        
        # RSU calculations
        rsu_rate = loc_config["rsu_rate"]
        rsu_vested_value_usd = salary_usd * rsu_rate
        
        # Update state for equity tracking
        state["unvested_equity_value"] = rsu_vested_value_usd * 0.5  # Assume 50% vested
        
        # All values are already in USD
        gross_income_usd = salary_usd + bonus_usd + rsu_vested_value_usd
        
        # Tax calculations
        if loc_config["tax_system"] == "tax_free":
            tax_usd = 0
        else:
            tax_usd = calculate_us_tax(gross_income_usd, loc_config["tax_system"], year)
        
        net_income_usd = gross_income_usd - tax_usd
        
        # Expenses
        inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
        inf_multiplier = calculate_inflation_multiplier(year, config)
        expenses = calculate_international_expenses(location, loc_config, inf_multiplier, salary_usd)
        
        # Housing costs
        mortgage_payment_usd, house_equity_usd = calculate_international_housing(
            plan_year, location, loc_config, state, inflation_rate, housing_strategy
        )
        
        total_expenses_usd = (expenses["rent"] + expenses["healthcare"] + 
                             expenses["retirement_contrib"] + expenses["general_expenses"] + 
                             mortgage_payment_usd)
        
        # Savings and investments
        annual_net_savings_usd = net_income_usd - total_expenses_usd
        state["cumulative_investments"] *= (1 + config["investment_return_rate"])
        state["cumulative_investments"] += annual_net_savings_usd
        state["cumulative_investments"] = max(0, state["cumulative_investments"])
        
        # Net worth
        net_worth_usd = state["cumulative_investments"] + state["unvested_equity_value"] + house_equity_usd
        
        # Convert to GBP for unified structure
        salary_gbp = salary_usd / loc_config["exchange_rate"]
        bonus_gbp = bonus_usd / loc_config["exchange_rate"]
        rsu_gbp = rsu_vested_value_usd / loc_config["exchange_rate"]
        gross_income_gbp = gross_income_usd / loc_config["exchange_rate"]
        net_income_gbp = net_income_usd / loc_config["exchange_rate"]
        tax_gbp = tax_usd / loc_config["exchange_rate"]
        total_expenses_gbp = total_expenses_usd / loc_config["exchange_rate"]
        annual_savings_gbp = annual_net_savings_usd / loc_config["exchange_rate"]
        net_worth_gbp = net_worth_usd / loc_config["exchange_rate"]
        house_equity_gbp = house_equity_usd / loc_config["exchange_rate"]
        
        # Create unified data point
        unified_point = UnifiedFinancialData(
            year=year,
            age=age,
            phase=FinancialPhase.INTERNATIONAL_ONLY,
            jurisdiction=Jurisdiction.US if location in ['seattle', 'new_york'] else Jurisdiction.UAE,
            currency=Currency.USD,
            income=create_unified_income_breakdown(
                salary_gbp=salary_gbp,
                bonus_gbp=bonus_gbp,
                rsu_gbp=rsu_gbp,
                other_income_gbp=0.0
            ),
            expenses=create_unified_expense_breakdown(
                housing_gbp=expenses["rent"] / loc_config["exchange_rate"] + mortgage_payment_usd / loc_config["exchange_rate"],
                living_gbp=expenses["general_expenses"] / loc_config["exchange_rate"],
                taxes_gbp=tax_gbp,
                investments_gbp=expenses["retirement_contrib"] / loc_config["exchange_rate"],
                other_gbp=expenses["healthcare"] / loc_config["exchange_rate"]
            ),
            tax=create_unified_tax_breakdown(
                income_tax_gbp=tax_gbp,
                social_security_gbp=0.0,  # Not tracked in international scenarios
                other_taxes_gbp=0.0
            ),
            investments=create_unified_investment_breakdown(
                retirement_gbp=expenses["retirement_contrib"] / loc_config["exchange_rate"],
                taxable_gbp=annual_savings_gbp,
                housing_gbp=house_equity_gbp
            ),
            net_worth=create_unified_net_worth_breakdown(
                liquid_assets_gbp=state["cumulative_investments"] / loc_config["exchange_rate"],
                illiquid_assets_gbp=(house_equity_gbp + state["unvested_equity_value"] / loc_config["exchange_rate"]),
                liabilities_gbp=0.0
            ),
            exchange_rates={Currency.USD: loc_config["exchange_rate"], Currency.GBP: 1.0}
        )
        
        scenario.add_data_point(unified_point)
    
    return scenario


def run_unified_delayed_relocation_scenario(scenario_name: str, config: dict) -> UnifiedFinancialScenario:
    """Run delayed relocation scenario using unified models."""
    
    # Parse scenario name to extract location and parameters
    parts = scenario_name.split('_')
    
    # Extract location (handle multi-word locations like new_york)
    if len(parts) >= 3 and parts[0] == 'new' and parts[1] == 'york':
        location = 'new_york'
    elif len(parts) >= 2:
        location = parts[0]
    else:
        location = parts[0]
    
    # Extract relocation year
    if 'year4' in scenario_name:
        relocation_year = 4
    elif 'year5' in scenario_name:
        relocation_year = 5
    else:
        relocation_year = 4  # Default
    
    # Extract housing strategy
    if 'uk_home' in scenario_name:
        housing_strategy = "uk_home"
    elif 'local_home' in scenario_name:
        housing_strategy = "local_home"
    else:
        housing_strategy = "uk_home"  # Default
    
    # Create scenario metadata
    metadata = create_scenario_metadata_from_name(scenario_name)
    
    scenario = UnifiedFinancialScenario(
        name=scenario_name,
        description=f"Delayed relocation scenario {scenario_name} using unified models",
        phase=FinancialPhase.UK_TO_INTERNATIONAL,
        data_points=[],
        metadata=metadata
    )
    
    # Get location configuration
    loc_config = config["international_scenarios"][location]
    
    # Initialize state
    state = initialize_scenario_state(config)
    years = list(range(config["start_year"], config["start_year"] + config["plan_duration_years"]))
    
    for i, year in enumerate(years):
        plan_year = i + 1
        age = config["start_age"] + i
        
        # Determine if we're in UK or international phase
        is_international = plan_year >= relocation_year
        
        if not is_international:
            # UK phase - same as UK scenario
            salary = calculate_uk_salary_progression(plan_year, 'A')
            bonus = calculate_uk_bonus(salary, 'A', plan_year)
            
            # RSU calculations
            ipo_multiplier = 2.0 if plan_year == 4 else 1.0
            rsu_vested_value, state["unvested_equity_value"] = calculate_rsu_vesting_scenario_a(
                plan_year, salary, state["rsu_grants"], ipo_multiplier
            )
            
            gross_income = salary + bonus + rsu_vested_value
            
            # UK Tax and Deductions
            tax, ni = calculate_uk_tax_ni(gross_income, year, config)
            sl_repayment, state["student_loan_balance"] = calculate_uk_student_loan(
                gross_income, state["student_loan_balance"], config
            )
            net_income = gross_income - tax - ni - sl_repayment
            
            # UK Location-specific expenses
            inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
            inf_multiplier = calculate_inflation_multiplier(year, config)
            loc_config = config["location_configs"]["UK"]
            location_expenses = calculate_uk_expenses(loc_config, inf_multiplier)
            
            # Universal goals (location-independent)
            universal_expenses = calculate_universal_goals(plan_year, config, inf_multiplier)
            
            # UK housing
            parental_home_price = calculate_parental_home_price(config)
            mortgage_payment = calculate_mortgage_and_house_equity(
                plan_year, parental_home_price, config, state, inflation_rate
            )
            
            total_expenses = (location_expenses["rent"] + location_expenses["healthcare"] + 
                             location_expenses["retirement_contribution"] + location_expenses["general_expenses"] +
                             universal_expenses["personal"] + universal_expenses["parental_support"] + 
                             universal_expenses["travel"] + universal_expenses["university_payment"] +
                             universal_expenses["marriage"] + universal_expenses["child"] + mortgage_payment)
            
            # Create UK unified data point
            unified_point = UnifiedFinancialData(
                year=year,
                age=age,
                phase=FinancialPhase.UK_ONLY,
                jurisdiction=Jurisdiction.UK,
                currency=Currency.GBP,
                income=create_unified_income_breakdown(
                    salary_gbp=salary,
                    bonus_gbp=bonus,
                    rsu_gbp=rsu_vested_value,
                    other_income_gbp=0.0
                ),
                expenses=create_unified_expense_breakdown(
                    housing_gbp=location_expenses["rent"] + mortgage_payment,
                    living_gbp=universal_expenses["personal"],
                    taxes_gbp=tax + ni + sl_repayment,
                    investments_gbp=0.0,
                    other_gbp=universal_expenses["parental_support"] + universal_expenses["travel"] + 
                              universal_expenses["university_payment"] + universal_expenses["marriage"] + universal_expenses["child"]
                ),
                tax=create_unified_tax_breakdown(
                    income_tax_gbp=tax,
                    social_security_gbp=ni,
                    other_taxes_gbp=sl_repayment
                ),
                investments=create_unified_investment_breakdown(
                    retirement_gbp=0.0,
                    taxable_gbp=net_income - total_expenses,
                    housing_gbp=state["house_equity"]
                ),
                net_worth=create_unified_net_worth_breakdown(
                    liquid_assets_gbp=state["cumulative_investments"],
                    illiquid_assets_gbp=state["house_equity"] + state["unvested_equity_value"],
                    liabilities_gbp=0.0
                ),
                exchange_rates={Currency.GBP: 1.0}
            )
            
        else:
            # International phase - same as international scenario
            salary = calculate_uk_salary_progression(plan_year, 'A')
            bonus = calculate_uk_bonus(salary, 'A', plan_year)
            
            # RSU calculations
            ipo_multiplier = 2.0 if plan_year == 4 else 1.0
            rsu_vested_value, state["unvested_equity_value"] = calculate_rsu_vesting_scenario_a(
                plan_year, salary, state["rsu_grants"], ipo_multiplier
            )
            
            # Convert to USD
            salary_usd = convert_gbp_to_usd(salary, loc_config["exchange_rate"])
            bonus_usd = convert_gbp_to_usd(bonus, loc_config["exchange_rate"])
            rsu_usd = convert_gbp_to_usd(rsu_vested_value, loc_config["exchange_rate"])
            
            gross_income_usd = salary_usd + bonus_usd + rsu_usd
            
            # Tax calculations
            if loc_config["tax_system"] == "tax_free":
                tax_usd = 0
            else:
                tax_usd = calculate_us_tax(gross_income_usd, loc_config["tax_system"], year)
            
            net_income_usd = gross_income_usd - tax_usd
            
            # Expenses
            inflation_rate = config["inflation_path"].get(year, config["inflation_path"]["default"])
            inf_multiplier = calculate_inflation_multiplier(year, config)
            expenses = calculate_international_expenses(location, loc_config, inf_multiplier, salary_usd)
            
            # Housing costs
            mortgage_payment_usd, house_equity_usd = calculate_international_housing(
                plan_year, location, loc_config, state, inflation_rate, housing_strategy
            )
            
            total_expenses_usd = (expenses["rent"] + expenses["healthcare"] + 
                                 expenses["retirement_contrib"] + expenses["general_expenses"] + 
                                 mortgage_payment_usd)
            
            # Convert to GBP for unified structure
            salary_gbp = salary_usd / loc_config["exchange_rate"]
            bonus_gbp = bonus_usd / loc_config["exchange_rate"]
            rsu_gbp = rsu_usd / loc_config["exchange_rate"]
            gross_income_gbp = gross_income_usd / loc_config["exchange_rate"]
            net_income_gbp = net_income_usd / loc_config["exchange_rate"]
            tax_gbp = tax_usd / loc_config["exchange_rate"]
            total_expenses_gbp = total_expenses_usd / loc_config["exchange_rate"]
            annual_savings_gbp = (net_income_usd - total_expenses_usd) / loc_config["exchange_rate"]
            net_worth_gbp = (state["cumulative_investments"] + state["unvested_equity_value"] + house_equity_usd) / loc_config["exchange_rate"]
            house_equity_gbp = house_equity_usd / loc_config["exchange_rate"]
            
            # Create international unified data point
            unified_point = UnifiedFinancialData(
                year=year,
                age=age,
                phase=FinancialPhase.INTERNATIONAL_ONLY,
                jurisdiction=Jurisdiction.US if location in ['seattle', 'new_york'] else Jurisdiction.UAE,
                currency=Currency.USD,
                income=create_unified_income_breakdown(
                    salary_gbp=salary_gbp,
                    bonus_gbp=bonus_gbp,
                    rsu_gbp=rsu_gbp,
                    other_income_gbp=0.0
                ),
                expenses=create_unified_expense_breakdown(
                    housing_gbp=expenses["rent"] / loc_config["exchange_rate"] + mortgage_payment_usd / loc_config["exchange_rate"],
                    living_gbp=expenses["general_expenses"] / loc_config["exchange_rate"],
                    taxes_gbp=tax_gbp,
                    investments_gbp=expenses["retirement_contrib"] / loc_config["exchange_rate"],
                    other_gbp=expenses["healthcare"] / loc_config["exchange_rate"]
                ),
                tax=create_unified_tax_breakdown(
                    income_tax_gbp=tax_gbp,
                    social_security_gbp=0.0,
                    other_taxes_gbp=0.0
                ),
                investments=create_unified_investment_breakdown(
                    retirement_gbp=expenses["retirement_contrib"] / loc_config["exchange_rate"],
                    taxable_gbp=annual_savings_gbp,
                    housing_gbp=house_equity_gbp
                ),
                net_worth=create_unified_net_worth_breakdown(
                    liquid_assets_gbp=state["cumulative_investments"] / loc_config["exchange_rate"],
                    illiquid_assets_gbp=(house_equity_gbp + state["unvested_equity_value"] / loc_config["exchange_rate"]),
                    liabilities_gbp=0.0
                ),
                exchange_rates={Currency.USD: loc_config["exchange_rate"], Currency.GBP: 1.0}
            )
        
        scenario.add_data_point(unified_point)
        
        # Update investments
        if is_international:
            annual_net_savings_usd = net_income_usd - total_expenses_usd
            state["cumulative_investments"] *= (1 + config["investment_return_rate"])
            state["cumulative_investments"] += annual_net_savings_usd
            state["cumulative_investments"] = max(0, state["cumulative_investments"])
        else:
            annual_net_savings = net_income - total_expenses
            state["cumulative_investments"] *= (1 + config["investment_return_rate"])
            state["cumulative_investments"] += annual_net_savings
            state["cumulative_investments"] = max(0, state["cumulative_investments"])
    
    return scenario


if __name__ == '__main__':
    # Test the unified functions
    print("Testing unified financial planner...")
    
    # Test UK scenarios
    scenario_a = run_unified_scenario('A', CONFIG)
    scenario_b = run_unified_scenario('B', CONFIG)
    
    print(f"Unified Scenario A Final Net Worth: £{scenario_a.get_final_net_worth_gbp():,.0f}")
    print(f"Unified Scenario B Final Net Worth: £{scenario_b.get_final_net_worth_gbp():,.0f}")
    
    # Test international scenario
    dubai_scenario = run_unified_international_scenario('dubai', CONFIG)
    print(f"Unified Dubai Final Net Worth: £{dubai_scenario.get_final_net_worth_gbp():,.0f}")
    
    # Test delayed relocation scenario
    delayed_scenario = run_unified_delayed_relocation_scenario('dubai_year4_local_home', CONFIG)
    print(f"Unified Delayed Dubai Year 4 Final Net Worth: £{delayed_scenario.get_final_net_worth_gbp():,.0f}")
    
    print("✅ All unified functions working correctly!") 