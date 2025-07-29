"""
Scenario Builder using Pydantic Models
Helper functions to build consistent financial scenarios.
"""

from typing import Dict, Any
from .financial_data import FinancialDataPoint, FinancialScenario, Phase
import uuid


def create_uk_data_point(
    year: int,
    age: int,
    salary: float,
    bonus: float,
    rsu_vested: float,
    gross_income: float,
    net_income: float,
    total_expenses: float,
    annual_savings: float,
    cumulative_portfolio: float,
    house_equity: float,
    net_worth: float,
    expenses: Dict[str, float],
    tax: float,
    ni: float,
    sl_repayment: float,
    investment_breakdown: Dict[str, float]
) -> FinancialDataPoint:
    """Create a UK phase data point."""
    
    return FinancialDataPoint(
        year=year,
        age=age,
        phase=Phase.UK,
        # UK financial data
        gross_salary_gbp=salary,
        gross_bonus_gbp=bonus,
        vested_rsu_gbp=rsu_vested,
        total_gross_gbp=gross_income,
        net_income_gbp=net_income,
        total_expenses_gbp=total_expenses,
        annual_savings_gbp=annual_savings,
        cumulative_portfolio_gbp=cumulative_portfolio,
        house_equity_gbp=house_equity,
        net_worth_gbp=net_worth,
        # UK expenses
        personal_expenses_gbp=expenses.get("personal", 0.0),
        parental_support_gbp=expenses.get("parental_support", 0.0),
        travel_expenses_gbp=expenses.get("travel", 0.0),
        rent_gbp=expenses.get("rent", 0.0),
        university_repayment_gbp=expenses.get("university_repayment", 0.0),
        marriage_costs_gbp=expenses.get("marriage", 0.0),
        child_costs_gbp=expenses.get("child", 0.0),
        mortgage_payment_gbp=expenses.get("mortgage_payment", 0.0),
        # UK tax and deductions
        income_tax_gbp=tax,
        national_insurance_gbp=ni,
        student_loan_repayment_gbp=sl_repayment,
        # UK investment breakdown
        lisa_contribution_gbp=investment_breakdown.get("lisa_contr", 0.0),
        isa_contribution_gbp=investment_breakdown.get("isa_contr", 0.0),
        sipp_contribution_gbp=investment_breakdown.get("sipp_contr", 0.0),
        gia_contribution_gbp=investment_breakdown.get("gia_contr", 0.0),
        lisa_bonus_gbp=investment_breakdown.get("lisa_bonus", 0.0),
        # GBP equivalent values (same as GBP for UK scenarios)
        net_worth_gbp_equiv=net_worth,
        gross_income_gbp_equiv=gross_income,
        gross_salary_gbp_equiv=salary,
        gross_bonus_gbp_equiv=bonus,
        vested_rsu_gbp_equiv=rsu_vested,
        net_income_gbp_equiv=net_income,
        total_expenses_gbp_equiv=total_expenses,
        annual_savings_gbp_equiv=annual_savings,
        cumulative_portfolio_gbp_equiv=cumulative_portfolio,
        house_equity_gbp_equiv=house_equity,
    )


def create_international_data_point(
    year: int,
    age: int,
    salary_usd: float,
    bonus_usd: float,
    rsu_vested_usd: float,
    gross_income_usd: float,
    net_income_usd: float,
    total_expenses_usd: float,
    annual_savings_usd: float,
    cumulative_portfolio_usd: float,
    net_worth_usd: float,
    house_equity_usd: float,
    expenses_usd: Dict[str, float],
    tax_usd: float,
    gbp_data: Dict[str, float],
    investment_growth_usd: float
) -> FinancialDataPoint:
    """Create an International phase data point."""
    
    return FinancialDataPoint(
        year=year,
        age=age,
        phase=Phase.INTERNATIONAL,
        # International financial data (USD)
        gross_salary_usd=salary_usd,
        gross_bonus_usd=bonus_usd,
        vested_rsu_usd=rsu_vested_usd,
        total_gross_usd=gross_income_usd,
        net_income_usd=net_income_usd,
        total_expenses_usd=total_expenses_usd,
        annual_savings_usd=annual_savings_usd,
        cumulative_portfolio_usd=cumulative_portfolio_usd,
        net_worth_usd=net_worth_usd,
        house_equity_usd=house_equity_usd,
        # International expenses (USD)
        rent_usd=expenses_usd.get("rent", 0.0),
        healthcare_usd=expenses_usd.get("healthcare", 0.0),
        retirement_contribution_usd=expenses_usd.get("retirement_contrib", 0.0),
        general_expenses_usd=expenses_usd.get("general_expenses", 0.0),
        relocation_cost_usd=expenses_usd.get("relocation_cost", 0.0),
        mortgage_payment_usd=expenses_usd.get("mortgage_payment", 0.0),
        # International tax
        income_tax_usd=tax_usd,
        # Investment growth
        investment_growth_usd=investment_growth_usd,
        # GBP equivalent values
        net_worth_gbp_equiv=gbp_data.get("gbp_net_worth", 0.0),
        gross_income_gbp_equiv=gbp_data.get("gbp_gross_income", 0.0),
        gross_salary_gbp_equiv=gbp_data.get("gbp_gross_income", 0.0) * 0.8,  # Estimate salary as 80% of gross income
        gross_bonus_gbp_equiv=gbp_data.get("gbp_gross_income", 0.0) * 0.1,  # Estimate bonus as 10% of gross income
        vested_rsu_gbp_equiv=gbp_data.get("gbp_gross_income", 0.0) * 0.1,  # Estimate RSU as 10% of gross income
        net_income_gbp_equiv=gbp_data.get("gbp_net_income", 0.0),
        total_expenses_gbp_equiv=gbp_data.get("gbp_total_expenses", 0.0),
        annual_savings_gbp_equiv=gbp_data.get("gbp_annual_savings", 0.0),
        cumulative_portfolio_gbp_equiv=gbp_data.get("gbp_cumulative_portfolio", 0.0),
        house_equity_gbp_equiv=house_equity_usd / gbp_data.get("exchange_rate", 1.26) if house_equity_usd > 0 else 0.0,
    )


def build_uk_scenario(name: str, data_points: list) -> FinancialScenario:
    """Build a UK scenario from raw data points."""
    scenario = FinancialScenario(name=name)
    
    for data in data_points:
        # Extract UK data
        data_point = create_uk_data_point(
            year=data["Year"],
            age=data["Age"],
            salary=data["Gross Salary (£)"],
            bonus=data["Gross Bonus (£)"],
            rsu_vested=data["Vested RSU (£)"],
            gross_income=data["Total Gross (£)"],
            net_income=data["Net Income (£)"],
            total_expenses=data["Total Expenses (£)"],
            annual_savings=data["Annual Savings (£)"],
            cumulative_portfolio=data["Cumulative Portfolio (£)"],
            house_equity=data["House Equity (£)"],
            net_worth=data["Net Worth (£)"],
            expenses={
                "personal": data["Personal Expenses (£)"],
                "parental_support": data["Parental Support (£)"],
                "travel": data["Travel Expenses (£)"],
                "rent": data["Rent (£)"],
                "university_repayment": data["University Repayment (£)"],
                "marriage": data["Marriage Costs (£)"],
                "child": data["Child Costs (£)"],
                "mortgage_payment": data["Mortgage Payment (£)"],
            },
            tax=data["Income Tax (£)"],
            ni=data["National Insurance (£)"],
            sl_repayment=data["Student Loan Repayment (£)"],
            investment_breakdown={
                "lisa_contr": data.get("LISA Contribution (£)", 0.0),
                "isa_contr": data.get("ISA Contribution (£)", 0.0),
                "sipp_contr": data.get("SIPP Contribution (£)", 0.0),
                "gia_contr": data.get("GIA Contribution (£)", 0.0),
                "lisa_bonus": data.get("LISA Bonus (£)", 0.0),
            }
        )
        scenario.add_data_point(data_point)
    
    return scenario


def build_international_scenario(name: str, data_points: list) -> FinancialScenario:
    """Build an International scenario from raw data points."""
    scenario = FinancialScenario(name=name)
    
    for data in data_points:
        # Extract International data
        data_point = create_international_data_point(
            year=data["Year"],
            age=data["Age"],
            salary_usd=data["Gross Salary (USD)"],
            bonus_usd=data["Gross Bonus (USD)"],
            rsu_vested_usd=data["Vested RSU (USD)"],
            gross_income_usd=data["Total Gross (USD)"],
            net_income_usd=data["Net Income (USD)"],
            total_expenses_usd=data["Total Expenses (USD)"],
            annual_savings_usd=data["Annual Savings (USD)"],
            cumulative_portfolio_usd=data["Cumulative Portfolio (USD)"],
            net_worth_usd=data["Net Worth (USD)"],
            house_equity_usd=data["House Equity (USD)"],
            expenses_usd={
                "rent": data["Rent (USD)"],
                "healthcare": data["Healthcare (USD)"],
                "retirement_contrib": data["Retirement Contribution (USD)"],
                "general_expenses": data["General Expenses (USD)"],
                "relocation_cost": data["Relocation Cost (USD)"],
                "mortgage_payment": data["Mortgage Payment (USD)"],
            },
            tax_usd=data["Income Tax (USD)"],
            gbp_data={
                "gbp_net_worth": data["Net Worth (GBP)"],
                "gbp_gross_income": data["Gross Income (GBP)"],
                "gbp_net_income": data["Net Income (GBP)"],
                "gbp_total_expenses": data["Total Expenses (GBP)"],
                "gbp_annual_savings": data["Annual Savings (GBP)"],
                "gbp_cumulative_portfolio": data["Cumulative Portfolio (GBP)"],
                "exchange_rate": 1.26,  # Default exchange rate
            },
            investment_growth_usd=data.get("Investment Growth (USD)", 0.0)
        )
        scenario.add_data_point(data_point)
    
    return scenario


def build_delayed_relocation_scenario(name: str, data_points: list) -> FinancialScenario:
    """Build a delayed relocation scenario from raw data points."""
    scenario = FinancialScenario(name=name)
    
    for data in data_points:
        if data.get("Phase") == "UK":
            # UK phase data point
            data_point = create_uk_data_point(
                year=data["Year"],
                age=data["Age"],
                salary=data["Gross Salary (£)"],
                bonus=data["Gross Bonus (£)"],
                rsu_vested=data["Vested RSU (£)"],
                gross_income=data["Total Gross (£)"],
                net_income=data["Net Income (£)"],
                total_expenses=data["Total Expenses (£)"],
                annual_savings=data["Annual Savings (£)"],
                cumulative_portfolio=data["Cumulative Portfolio (£)"],
                house_equity=data["House Equity (£)"],
                net_worth=data["Net Worth (£)"],
                expenses={
                    "personal": data["Personal Expenses (£)"],
                    "parental_support": data["Parental Support (£)"],
                    "travel": data["Travel Expenses (£)"],
                    "rent": data["Rent (£)"],
                    "university_repayment": data["University Repayment (£)"],
                    "marriage": data["Marriage Costs (£)"],
                    "child": data["Child Costs (£)"],
                    "mortgage_payment": data["Mortgage Payment (£)"],
                },
                tax=data["Income Tax (£)"],
                ni=data["National Insurance (£)"],
                sl_repayment=data["Student Loan Repayment (£)"],
                investment_breakdown={
                    "lisa_contr": data.get("LISA Contribution (£)", 0.0),
                    "isa_contr": data.get("ISA Contribution (£)", 0.0),
                    "sipp_contr": data.get("SIPP Contribution (£)", 0.0),
                    "gia_contr": data.get("GIA Contribution (£)", 0.0),
                    "lisa_bonus": data.get("LISA Bonus (£)", 0.0),
                }
            )
        else:
            # International phase data point
            data_point = create_international_data_point(
                year=data["Year"],
                age=data["Age"],
                salary_usd=data["Gross Salary (USD)"],
                bonus_usd=data["Gross Bonus (USD)"],
                rsu_vested_usd=data["Vested RSU (USD)"],
                gross_income_usd=data["Total Gross (USD)"],
                net_income_usd=data["Net Income (USD)"],
                total_expenses_usd=data["Total Expenses (USD)"],
                annual_savings_usd=data["Annual Savings (USD)"],
                cumulative_portfolio_usd=data["Cumulative Portfolio (USD)"],
                net_worth_usd=data["Net Worth (USD)"],
                house_equity_usd=data["House Equity (USD)"],
                expenses_usd={
                    "rent": data["Rent (USD)"],
                    "healthcare": data["Healthcare (USD)"],
                    "retirement_contrib": data["Retirement Contribution (USD)"],
                    "general_expenses": data["General Expenses (USD)"],
                    "relocation_cost": data["Relocation Cost (USD)"],
                    "mortgage_payment": data["Mortgage Payment (USD)"],
                },
                tax_usd=data["Income Tax (USD)"],
                gbp_data={
                    "gbp_net_worth": data["Net Worth (GBP)"],
                    "gbp_gross_income": data["Gross Income (GBP)"],
                    "gbp_net_income": data["Net Income (GBP)"],
                    "gbp_total_expenses": data["Total Expenses (GBP)"],
                    "gbp_annual_savings": data["Annual Savings (GBP)"],
                    "gbp_cumulative_portfolio": data["Cumulative Portfolio (GBP)"],
                    "exchange_rate": 1.26,  # Default exchange rate
                },
                investment_growth_usd=data.get("Investment Growth (USD)", 0.0)
            )
        
        scenario.add_data_point(data_point)
    
    return scenario 