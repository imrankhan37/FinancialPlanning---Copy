"""
Financial Data Models using Pydantic
Defines the data structures for financial scenarios and data points.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum


class Phase(str, Enum):
    """Enumeration for different phases of financial planning."""
    UK = "UK"
    INTERNATIONAL = "INTERNATIONAL"


class FinancialDataPoint(BaseModel):
    """Represents a single financial data point for a specific year."""
    
    # Basic information
    year: int = Field(..., description="Year of the data point")
    age: int = Field(..., description="Age in this year")
    phase: Phase = Field(..., description="Phase (UK or International)")
    
    # UK financial data (GBP)
    gross_salary_gbp: Optional[float] = Field(0.0, description="Gross salary in GBP")
    gross_bonus_gbp: Optional[float] = Field(0.0, description="Gross bonus in GBP")
    vested_rsu_gbp: Optional[float] = Field(0.0, description="Vested RSU value in GBP")
    total_gross_gbp: Optional[float] = Field(0.0, description="Total gross income in GBP")
    net_income_gbp: Optional[float] = Field(0.0, description="Net income in GBP")
    total_expenses_gbp: Optional[float] = Field(0.0, description="Total expenses in GBP")
    annual_savings_gbp: Optional[float] = Field(0.0, description="Annual savings in GBP")
    cumulative_portfolio_gbp: Optional[float] = Field(0.0, description="Cumulative portfolio value in GBP")
    house_equity_gbp: Optional[float] = Field(0.0, description="House equity in GBP")
    net_worth_gbp: Optional[float] = Field(0.0, description="Net worth in GBP")
    
    # UK expenses (GBP)
    personal_expenses_gbp: Optional[float] = Field(0.0, description="Personal expenses in GBP")
    parental_support_gbp: Optional[float] = Field(0.0, description="Parental support in GBP")
    travel_expenses_gbp: Optional[float] = Field(0.0, description="Travel expenses in GBP")
    rent_gbp: Optional[float] = Field(0.0, description="Rent in GBP")
    university_repayment_gbp: Optional[float] = Field(0.0, description="University repayment in GBP")
    marriage_costs_gbp: Optional[float] = Field(0.0, description="Marriage costs in GBP")
    child_costs_gbp: Optional[float] = Field(0.0, description="Child costs in GBP")
    mortgage_payment_gbp: Optional[float] = Field(0.0, description="Mortgage payment in GBP")
    
    # UK tax and deductions (GBP)
    income_tax_gbp: Optional[float] = Field(0.0, description="Income tax in GBP")
    national_insurance_gbp: Optional[float] = Field(0.0, description="National insurance in GBP")
    student_loan_repayment_gbp: Optional[float] = Field(0.0, description="Student loan repayment in GBP")
    
    # UK investment breakdown (GBP)
    lisa_contribution_gbp: Optional[float] = Field(0.0, description="LISA contribution in GBP")
    isa_contribution_gbp: Optional[float] = Field(0.0, description="ISA contribution in GBP")
    sipp_contribution_gbp: Optional[float] = Field(0.0, description="SIPP contribution in GBP")
    gia_contribution_gbp: Optional[float] = Field(0.0, description="GIA contribution in GBP")
    lisa_bonus_gbp: Optional[float] = Field(0.0, description="LISA bonus in GBP")
    
    # International financial data (USD)
    gross_salary_usd: Optional[float] = Field(0.0, description="Gross salary in USD")
    gross_bonus_usd: Optional[float] = Field(0.0, description="Gross bonus in USD")
    vested_rsu_usd: Optional[float] = Field(0.0, description="Vested RSU value in USD")
    total_gross_usd: Optional[float] = Field(0.0, description="Total gross income in USD")
    net_income_usd: Optional[float] = Field(0.0, description="Net income in USD")
    total_expenses_usd: Optional[float] = Field(0.0, description="Total expenses in USD")
    annual_savings_usd: Optional[float] = Field(0.0, description="Annual savings in USD")
    cumulative_portfolio_usd: Optional[float] = Field(0.0, description="Cumulative portfolio value in USD")
    net_worth_usd: Optional[float] = Field(0.0, description="Net worth in USD")
    house_equity_usd: Optional[float] = Field(0.0, description="House equity in USD")
    
    # International expenses (USD)
    rent_usd: Optional[float] = Field(0.0, description="Rent in USD")
    healthcare_usd: Optional[float] = Field(0.0, description="Healthcare costs in USD")
    retirement_contribution_usd: Optional[float] = Field(0.0, description="Retirement contribution in USD")
    general_expenses_usd: Optional[float] = Field(0.0, description="General expenses in USD")
    relocation_cost_usd: Optional[float] = Field(0.0, description="Relocation cost in USD")
    mortgage_payment_usd: Optional[float] = Field(0.0, description="Mortgage payment in USD")
    
    # International tax (USD)
    income_tax_usd: Optional[float] = Field(0.0, description="Income tax in USD")
    
    # Investment growth (USD)
    investment_growth_usd: Optional[float] = Field(0.0, description="Investment growth in USD")
    
    # GBP equivalent values (for comparison)
    net_worth_gbp_equiv: Optional[float] = Field(0.0, description="Net worth in GBP equivalent")
    gross_income_gbp_equiv: Optional[float] = Field(0.0, description="Gross income in GBP equivalent")
    gross_salary_gbp_equiv: Optional[float] = Field(0.0, description="Gross salary in GBP equivalent")
    gross_bonus_gbp_equiv: Optional[float] = Field(0.0, description="Gross bonus in GBP equivalent")
    vested_rsu_gbp_equiv: Optional[float] = Field(0.0, description="Vested RSU in GBP equivalent")
    net_income_gbp_equiv: Optional[float] = Field(0.0, description="Net income in GBP equivalent")
    total_expenses_gbp_equiv: Optional[float] = Field(0.0, description="Total expenses in GBP equivalent")
    annual_savings_gbp_equiv: Optional[float] = Field(0.0, description="Annual savings in GBP equivalent")
    cumulative_portfolio_gbp_equiv: Optional[float] = Field(0.0, description="Cumulative portfolio in GBP equivalent")
    house_equity_gbp_equiv: Optional[float] = Field(0.0, description="House equity in GBP equivalent")
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"


class FinancialScenario(BaseModel):
    """Represents a complete financial scenario with multiple data points."""
    
    name: str = Field(..., description="Name of the scenario")
    data_points: List[FinancialDataPoint] = Field(default_factory=list, description="List of financial data points")
    
    def add_data_point(self, data_point: FinancialDataPoint) -> None:
        """Add a data point to the scenario."""
        self.data_points.append(data_point)
    
    def get_final_net_worth(self) -> float:
        """Get the final net worth from the last data point."""
        if not self.data_points:
            return 0.0
        
        # Try GBP equivalent first, then GBP, then USD converted
        last_point = self.data_points[-1]
        
        if hasattr(last_point, 'net_worth_gbp_equiv') and last_point.net_worth_gbp_equiv > 0:
            return last_point.net_worth_gbp_equiv
        elif hasattr(last_point, 'net_worth_gbp') and last_point.net_worth_gbp > 0:
            return last_point.net_worth_gbp
        elif hasattr(last_point, 'net_worth_usd') and last_point.net_worth_usd > 0:
            return last_point.net_worth_usd / 1.26  # Convert USD to GBP
        else:
            return 0.0
    
    def get_final_annual_savings(self) -> float:
        """Get the final annual savings from the last data point."""
        if not self.data_points:
            return 0.0
        
        last_point = self.data_points[-1]
        
        if hasattr(last_point, 'annual_savings_gbp_equiv') and last_point.annual_savings_gbp_equiv > 0:
            return last_point.annual_savings_gbp_equiv
        elif hasattr(last_point, 'annual_savings_gbp') and last_point.annual_savings_gbp > 0:
            return last_point.annual_savings_gbp
        elif hasattr(last_point, 'annual_savings_usd') and last_point.annual_savings_usd > 0:
            return last_point.annual_savings_usd / 1.26  # Convert USD to GBP
        else:
            return 0.0
    
    def get_total_tax_burden(self) -> float:
        """Calculate total tax burden across all years."""
        total_tax = 0.0
        
        for point in self.data_points:
            # Try GBP equivalent first, then GBP, then USD converted
            if hasattr(point, 'income_tax_gbp_equiv') and point.income_tax_gbp_equiv > 0:
                total_tax += point.income_tax_gbp_equiv
            elif hasattr(point, 'income_tax_gbp') and point.income_tax_gbp > 0:
                total_tax += point.income_tax_gbp
            elif hasattr(point, 'income_tax_usd') and point.income_tax_usd > 0:
                total_tax += point.income_tax_usd / 1.26  # Convert USD to GBP
        
        return total_tax
    
    def get_average_savings_rate(self) -> float:
        """Calculate average savings rate across all years."""
        if not self.data_points:
            return 0.0
        
        total_savings = 0.0
        total_income = 0.0
        valid_years = 0
        
        for point in self.data_points:
            # Get savings
            savings = 0.0
            if hasattr(point, 'annual_savings_gbp_equiv') and point.annual_savings_gbp_equiv > 0:
                savings = point.annual_savings_gbp_equiv
            elif hasattr(point, 'annual_savings_gbp') and point.annual_savings_gbp > 0:
                savings = point.annual_savings_gbp
            elif hasattr(point, 'annual_savings_usd') and point.annual_savings_usd > 0:
                savings = point.annual_savings_usd / 1.26
            
            # Get income
            income = 0.0
            if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0:
                income = point.gross_income_gbp_equiv
            elif hasattr(point, 'total_gross_gbp') and point.total_gross_gbp > 0:
                income = point.total_gross_gbp
            elif hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0:
                income = point.total_gross_usd / 1.26
            
            if income > 0:
                total_savings += savings
                total_income += income
                valid_years += 1
        
        if valid_years == 0 or total_income == 0:
            return 0.0
        
        return (total_savings / total_income) * 100
    
    def copy(self) -> 'FinancialScenario':
        """Create a copy of the scenario."""
        # Create a new scenario with the same name
        new_scenario = FinancialScenario(name=self.name)
        
        # Copy all data points
        for data_point in self.data_points:
            # Create a new data point with the same values
            new_data_point = FinancialDataPoint(
                year=data_point.year,
                age=data_point.age,
                phase=data_point.phase,
                # UK financial data
                gross_salary_gbp=data_point.gross_salary_gbp,
                gross_bonus_gbp=data_point.gross_bonus_gbp,
                vested_rsu_gbp=data_point.vested_rsu_gbp,
                total_gross_gbp=data_point.total_gross_gbp,
                net_income_gbp=data_point.net_income_gbp,
                total_expenses_gbp=data_point.total_expenses_gbp,
                annual_savings_gbp=data_point.annual_savings_gbp,
                cumulative_portfolio_gbp=data_point.cumulative_portfolio_gbp,
                house_equity_gbp=data_point.house_equity_gbp,
                net_worth_gbp=data_point.net_worth_gbp,
                # UK expenses
                personal_expenses_gbp=data_point.personal_expenses_gbp,
                parental_support_gbp=data_point.parental_support_gbp,
                travel_expenses_gbp=data_point.travel_expenses_gbp,
                rent_gbp=data_point.rent_gbp,
                university_repayment_gbp=data_point.university_repayment_gbp,
                marriage_costs_gbp=data_point.marriage_costs_gbp,
                child_costs_gbp=data_point.child_costs_gbp,
                mortgage_payment_gbp=data_point.mortgage_payment_gbp,
                # UK tax and deductions
                income_tax_gbp=data_point.income_tax_gbp,
                national_insurance_gbp=data_point.national_insurance_gbp,
                student_loan_repayment_gbp=data_point.student_loan_repayment_gbp,
                # UK investment breakdown
                lisa_contribution_gbp=data_point.lisa_contribution_gbp,
                isa_contribution_gbp=data_point.isa_contribution_gbp,
                sipp_contribution_gbp=data_point.sipp_contribution_gbp,
                gia_contribution_gbp=data_point.gia_contribution_gbp,
                lisa_bonus_gbp=data_point.lisa_bonus_gbp,
                # International financial data
                gross_salary_usd=data_point.gross_salary_usd,
                gross_bonus_usd=data_point.gross_bonus_usd,
                vested_rsu_usd=data_point.vested_rsu_usd,
                total_gross_usd=data_point.total_gross_usd,
                net_income_usd=data_point.net_income_usd,
                total_expenses_usd=data_point.total_expenses_usd,
                annual_savings_usd=data_point.annual_savings_usd,
                cumulative_portfolio_usd=data_point.cumulative_portfolio_usd,
                net_worth_usd=data_point.net_worth_usd,
                house_equity_usd=data_point.house_equity_usd,
                # International expenses
                rent_usd=data_point.rent_usd,
                healthcare_usd=data_point.healthcare_usd,
                retirement_contribution_usd=data_point.retirement_contribution_usd,
                general_expenses_usd=data_point.general_expenses_usd,
                relocation_cost_usd=data_point.relocation_cost_usd,
                mortgage_payment_usd=data_point.mortgage_payment_usd,
                # International tax
                income_tax_usd=data_point.income_tax_usd,
                # Investment growth
                investment_growth_usd=data_point.investment_growth_usd,
                # GBP equivalent values
                net_worth_gbp_equiv=data_point.net_worth_gbp_equiv,
                gross_income_gbp_equiv=data_point.gross_income_gbp_equiv,
                gross_salary_gbp_equiv=data_point.gross_salary_gbp_equiv,
                gross_bonus_gbp_equiv=data_point.gross_bonus_gbp_equiv,
                vested_rsu_gbp_equiv=data_point.vested_rsu_gbp_equiv,
                net_income_gbp_equiv=data_point.net_income_gbp_equiv,
                total_expenses_gbp_equiv=data_point.total_expenses_gbp_equiv,
                annual_savings_gbp_equiv=data_point.annual_savings_gbp_equiv,
                cumulative_portfolio_gbp_equiv=data_point.cumulative_portfolio_gbp_equiv,
                house_equity_gbp_equiv=data_point.house_equity_gbp_equiv,
            )
            new_scenario.add_data_point(new_data_point)
        
        return new_scenario
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid" 