"""
Unified Financial Data Models using Pydantic
Defines the unified data structures for financial scenarios with currency-agnostic design.
"""

from pydantic import BaseModel, Field, computed_field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime
from dataclasses import dataclass


# 1. CORE CONCEPTS
class Currency(str, Enum):
    """Supported currencies."""
    GBP = "GBP"
    USD = "USD"
    EUR = "EUR"


class Jurisdiction(str, Enum):
    """Supported tax jurisdictions."""
    UK = "UK"
    US = "US"
    UAE = "UAE"
    EU = "EU"


class FinancialPhase(str, Enum):
    """Financial planning phases."""
    UK_ONLY = "UK_ONLY"
    INTERNATIONAL_ONLY = "INTERNATIONAL_ONLY"
    UK_TO_INTERNATIONAL = "UK_TO_INTERNATIONAL"


# NEW: Phase Configuration for Unified Architecture
@dataclass
class PhaseConfig:
    """Configuration for a single phase in a financial scenario."""
    name: str
    duration: int
    start_year: int
    end_year: int
    location_market: str
    salary_progression: Dict[str, Any]
    expense_profile: str
    housing_strategy: Dict[str, Any]
    tax_system: Dict[str, Any]
    investment_strategy: Optional[Dict[str, Any]] = None


@dataclass
class ResolvedScenarioConfig:
    """Fully resolved scenario configuration with normalized multi-phase structure."""
    scenario_metadata: Dict[str, Any]
    planning: Dict[str, Any]
    phases: List[PhaseConfig]  # Always a list (1+ phases)
    is_multi_phase: bool       # Just metadata flag


# 4. CURRENCY VALUE WRAPPER
class CurrencyValue(BaseModel):
    """Wrapper for currency values with conversion metadata."""
    value: float = Field(..., description="Value in original currency")
    currency: Currency = Field(..., description="Original currency")
    gbp_value: float = Field(..., description="Value converted to GBP")
    exchange_rate: float = Field(..., description="Exchange rate used for conversion")
    conversion_date: Optional[datetime] = Field(None, description="Date of conversion")

    @classmethod
    def from_gbp(cls, value: float) -> 'CurrencyValue':
        """Create from GBP value."""
        return cls(
            value=value,
            currency=Currency.GBP,
            gbp_value=value,
            exchange_rate=1.0
        )

    @classmethod
    def from_usd(cls, value: float, exchange_rate: float) -> 'CurrencyValue':
        """Create from USD value."""
        gbp_value = value / exchange_rate
        return cls(
            value=value,
            currency=Currency.USD,
            gbp_value=gbp_value,
            exchange_rate=exchange_rate
        )

    @classmethod
    def from_eur(cls, value: float, exchange_rate: float) -> 'CurrencyValue':
        """Create from EUR value."""
        gbp_value = value / exchange_rate
        return cls(
            value=value,
            currency=Currency.EUR,
            gbp_value=gbp_value,
            exchange_rate=exchange_rate
        )

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


# 5. JURISDICTION-SPECIFIC STRUCTURES
class HousingExpenses(BaseModel):
    """Unified housing expenses."""
    rent: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    mortgage: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    utilities: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    maintenance: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    property_tax: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total housing expenses in GBP."""
        return sum(expense.gbp_value for expense in [
            self.rent, self.mortgage, self.utilities,
            self.maintenance, self.property_tax
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class LivingExpenses(BaseModel):
    """Unified living expenses."""
    food: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    transport: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    healthcare: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    entertainment: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    clothing: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    personal_care: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total living expenses in GBP."""
        return sum(expense.gbp_value for expense in [
            self.food, self.transport, self.healthcare,
            self.entertainment, self.clothing, self.personal_care
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class TaxExpenses(BaseModel):
    """Unified tax expenses."""
    income_tax: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    social_security: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    property_tax: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    other_taxes: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total tax expenses in GBP."""
        return sum(tax.gbp_value for tax in [
            self.income_tax, self.social_security,
            self.property_tax, self.other_taxes
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class InvestmentExpenses(BaseModel):
    """Unified investment-related expenses."""
    retirement_contributions: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    investment_fees: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    insurance: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total investment expenses in GBP."""
        return sum(expense.gbp_value for expense in [
            self.retirement_contributions, self.investment_fees, self.insurance
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class OtherExpenses(BaseModel):
    """Other miscellaneous expenses."""
    education: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    travel: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    gifts: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    miscellaneous: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total other expenses in GBP."""
        return sum(expense.gbp_value for expense in [
            self.education, self.travel, self.gifts, self.miscellaneous
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


# 3. SEMANTIC BREAKDOWNS
class IncomeBreakdown(BaseModel):
    """Unified income structure."""
    salary: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    bonus: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    rsu_vested: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    other_income: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def total_gbp(self) -> float:
        """Total income in GBP."""
        return sum(income.gbp_value for income in [
            self.salary, self.bonus, self.rsu_vested, self.other_income
        ])

    @computed_field
    @property
    def net_gbp(self) -> float:
        """Net income in GBP (after taxes)."""
        # This will be calculated by the tax breakdown
        return self.total_gbp

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class ExpenseBreakdown(BaseModel):
    """Unified expense structure."""
    housing: HousingExpenses = Field(default_factory=HousingExpenses)
    living: LivingExpenses = Field(default_factory=LivingExpenses)
    taxes: TaxExpenses = Field(default_factory=TaxExpenses)
    investments: InvestmentExpenses = Field(default_factory=InvestmentExpenses)
    other: OtherExpenses = Field(default_factory=OtherExpenses)

    @computed_field
    @property
    def total_gbp(self) -> float:
        """Total expenses in GBP."""
        return sum(expense.gbp_value for expense in [
            self.housing, self.living, self.taxes, self.investments, self.other
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class TaxBreakdown(BaseModel):
    """Unified tax structure."""
    income_tax: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    social_security: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    other_taxes: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def total_gbp(self) -> float:
        """Total tax burden in GBP."""
        return sum(tax.gbp_value for tax in [
            self.income_tax, self.social_security, self.other_taxes
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class RetirementInvestments(BaseModel):
    """Retirement investment vehicles."""
    pension: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    lisa: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    sipp: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    ira: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    employer_match: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total retirement investments in GBP."""
        return sum(inv.gbp_value for inv in [
            self.pension, self.lisa, self.sipp, self.ira, self.employer_match
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class TaxableInvestments(BaseModel):
    """Taxable investment accounts."""
    isa: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    gia: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    brokerage: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    crypto: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total taxable investments in GBP."""
        return sum(inv.gbp_value for inv in [
            self.isa, self.gia, self.brokerage, self.crypto
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class HousingInvestments(BaseModel):
    """Housing-related investments."""
    house_equity: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    rental_property: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def gbp_value(self) -> float:
        """Total housing investments in GBP."""
        return sum(inv.gbp_value for inv in [
            self.house_equity, self.rental_property
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class InvestmentBreakdown(BaseModel):
    """Unified investment structure."""
    retirement: RetirementInvestments = Field(default_factory=RetirementInvestments)
    taxable: TaxableInvestments = Field(default_factory=TaxableInvestments)
    housing: HousingInvestments = Field(default_factory=HousingInvestments)

    @computed_field
    @property
    def total_gbp(self) -> float:
        """Total investments in GBP."""
        return sum(inv.gbp_value for inv in [
            self.retirement, self.taxable, self.housing
        ])

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class NetWorthBreakdown(BaseModel):
    """Unified net worth structure."""
    liquid_assets: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    illiquid_assets: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))
    liabilities: CurrencyValue = Field(default_factory=lambda: CurrencyValue.from_gbp(0.0))

    @computed_field
    @property
    def total_gbp(self) -> float:
        """Net worth in GBP."""
        return self.liquid_assets.gbp_value + self.illiquid_assets.gbp_value - self.liabilities.gbp_value

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


# 2. UNIFIED FINANCIAL DATA
class UnifiedFinancialData(BaseModel):
    """Unified financial data point with currency conversion."""

    # Core metadata
    year: int = Field(..., description="Year of the data point")
    age: int = Field(..., description="Age in this year")
    phase: FinancialPhase = Field(..., description="Financial phase")
    jurisdiction: Jurisdiction = Field(..., description="Tax jurisdiction")
    currency: Currency = Field(..., description="Primary currency for this period")

    # Unified breakdowns
    income: IncomeBreakdown = Field(default_factory=IncomeBreakdown)
    expenses: ExpenseBreakdown = Field(default_factory=ExpenseBreakdown)
    tax: TaxBreakdown = Field(default_factory=TaxBreakdown)
    investments: InvestmentBreakdown = Field(default_factory=InvestmentBreakdown)
    net_worth: NetWorthBreakdown = Field(default_factory=NetWorthBreakdown)

    # Currency conversion metadata
    exchange_rates: Dict[Currency, float] = Field(default_factory=dict)

    # Computed properties for easy access
    @computed_field
    @property
    def net_worth_gbp(self) -> float:
        """Always return net worth in GBP."""
        return self.net_worth.total_gbp

    @computed_field
    @property
    def annual_savings_gbp(self) -> float:
        """Always return annual savings in GBP."""
        return self.income.total_gbp - self.expenses.total_gbp

    @computed_field
    @property
    def gross_income_gbp(self) -> float:
        """Always return gross income in GBP."""
        return self.income.total_gbp

    @computed_field
    @property
    def total_expenses_gbp(self) -> float:
        """Always return total expenses in GBP."""
        return self.expenses.total_gbp

    @computed_field
    @property
    def total_tax_gbp(self) -> float:
        """Always return total tax in GBP."""
        return self.tax.total_gbp

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


class ScenarioMetadata(BaseModel):
    """Metadata for scenario comparison."""
    jurisdiction: Jurisdiction = Field(..., description="Primary jurisdiction")
    tax_system: str = Field(..., description="Tax system description")
    housing_strategy: str = Field(..., description="Housing strategy")
    relocation_timing: Optional[int] = Field(None, description="Year of relocation if applicable")
    salary_progression: str = Field(..., description="Salary progression path")
    investment_strategy: str = Field(..., description="Investment strategy")
    description: str = Field("", description="Scenario description")

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True


# 6. UNIFIED SCENARIO
class UnifiedFinancialScenario(BaseModel):
    """Unified financial scenario."""
    name: str = Field(..., description="Scenario name")
    description: str = Field("", description="Scenario description")
    phase: FinancialPhase = Field(..., description="Financial phase")
    data_points: List[UnifiedFinancialData] = Field(default_factory=list, description="Financial data points")
    metadata: Optional[ScenarioMetadata] = Field(None, description="Scenario metadata")

    def add_data_point(self, data_point: UnifiedFinancialData) -> None:
        """Add a data point to the scenario."""
        self.data_points.append(data_point)

    def get_final_net_worth_gbp(self) -> float:
        """Get final net worth in GBP."""
        if not self.data_points:
            return 0.0
        return self.data_points[-1].net_worth_gbp

    def get_average_annual_savings_gbp(self) -> float:
        """Get average annual savings in GBP."""
        if not self.data_points:
            return 0.0
        savings = [point.annual_savings_gbp for point in self.data_points]
        return sum(savings) / len(savings)

    def get_total_tax_burden_gbp(self) -> float:
        """Get total tax burden in GBP."""
        if not self.data_points:
            return 0.0
        return sum(point.total_tax_gbp for point in self.data_points)

    def get_final_annual_savings_gbp(self) -> float:
        """Get final annual savings in GBP."""
        if not self.data_points:
            return 0.0
        return self.data_points[-1].annual_savings_gbp

    def get_final_liquid_savings_gbp(self) -> float:
        """Get final liquid assets (liquid savings) in GBP."""
        if not self.data_points:
            return 0.0
        return self.data_points[-1].net_worth.liquid_assets.gbp_value

    def get_net_worth_growth_rate(self) -> float:
        """Calculate net worth growth rate."""
        if len(self.data_points) < 2:
            return 0.0

        initial_net_worth = self.data_points[0].net_worth_gbp
        final_net_worth = self.data_points[-1].net_worth_gbp

        if initial_net_worth == 0:
            return 0.0

        return ((final_net_worth - initial_net_worth) / initial_net_worth) * 100

    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"
        from_attributes = True
