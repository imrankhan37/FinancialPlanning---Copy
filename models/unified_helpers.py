"""
Unified Financial Data Helpers
Conversion utilities between old and new unified data models.
"""

from typing import Dict, Any, List
from .financial_data import FinancialDataPoint as OldFinancialDataPoint, FinancialScenario as OldFinancialScenario
from .unified_financial_data import (
    UnifiedFinancialData, UnifiedFinancialScenario, ScenarioMetadata,
    CurrencyValue, Currency, Jurisdiction, FinancialPhase,
    IncomeBreakdown, ExpenseBreakdown, TaxBreakdown, InvestmentBreakdown, NetWorthBreakdown,
    HousingExpenses, LivingExpenses, TaxExpenses, InvestmentExpenses, OtherExpenses,
    RetirementInvestments, TaxableInvestments, HousingInvestments
)


def convert_old_to_unified_data_point(old_point: OldFinancialDataPoint) -> UnifiedFinancialData:
    """Convert old FinancialDataPoint to new UnifiedFinancialData."""
    
    # Determine phase and jurisdiction from old data
    phase = FinancialPhase.UK_ONLY if old_point.phase.value == "UK" else FinancialPhase.INTERNATIONAL_ONLY
    jurisdiction = Jurisdiction.UK if old_point.phase.value == "UK" else Jurisdiction.US  # Default to US for international
    
    # Create income breakdown
    income = IncomeBreakdown(
        salary=CurrencyValue.from_gbp(old_point.gross_salary_gbp_equiv or 0.0),
        bonus=CurrencyValue.from_gbp(old_point.gross_bonus_gbp_equiv or 0.0),
        rsu_vested=CurrencyValue.from_gbp(old_point.vested_rsu_gbp_equiv or 0.0),
        other_income=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    # Create expense breakdown
    housing = HousingExpenses(
        rent=CurrencyValue.from_gbp(old_point.rent_gbp or 0.0),
        mortgage=CurrencyValue.from_gbp(old_point.mortgage_payment_gbp or 0.0),
        utilities=CurrencyValue.from_gbp(0.0),  # Not available in old model
        maintenance=CurrencyValue.from_gbp(0.0),  # Not available in old model
        property_tax=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    living = LivingExpenses(
        food=CurrencyValue.from_gbp(old_point.personal_expenses_gbp or 0.0),
        transport=CurrencyValue.from_gbp(old_point.travel_expenses_gbp or 0.0),
        healthcare=CurrencyValue.from_gbp(0.0),  # Not available in old model
        entertainment=CurrencyValue.from_gbp(0.0),  # Not available in old model
        clothing=CurrencyValue.from_gbp(0.0),  # Not available in old model
        personal_care=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    taxes = TaxExpenses(
        income_tax=CurrencyValue.from_gbp(old_point.income_tax_gbp or 0.0),
        social_security=CurrencyValue.from_gbp(old_point.national_insurance_gbp or 0.0),
        property_tax=CurrencyValue.from_gbp(0.0),  # Not available in old model
        other_taxes=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    investments = InvestmentExpenses(
        retirement_contributions=CurrencyValue.from_gbp(0.0),  # Not available in old model
        investment_fees=CurrencyValue.from_gbp(0.0),  # Not available in old model
        insurance=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    other = OtherExpenses(
        education=CurrencyValue.from_gbp(old_point.university_repayment_gbp or 0.0),
        travel=CurrencyValue.from_gbp(old_point.travel_expenses_gbp or 0.0),
        gifts=CurrencyValue.from_gbp(0.0),  # Not available in old model
        miscellaneous=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    expenses = ExpenseBreakdown(
        housing=housing,
        living=living,
        taxes=taxes,
        investments=investments,
        other=other
    )
    
    # Create tax breakdown
    tax = TaxBreakdown(
        income_tax=CurrencyValue.from_gbp(old_point.income_tax_gbp or 0.0),
        social_security=CurrencyValue.from_gbp(old_point.national_insurance_gbp or 0.0),
        other_taxes=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    # Create investment breakdown
    retirement = RetirementInvestments(
        pension=CurrencyValue.from_gbp(0.0),  # Not available in old model
        lisa=CurrencyValue.from_gbp(old_point.lisa_contribution_gbp or 0.0),
        sipp=CurrencyValue.from_gbp(old_point.sipp_contribution_gbp or 0.0),
        ira=CurrencyValue.from_gbp(0.0),  # Not available in old model
        employer_match=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    taxable = TaxableInvestments(
        isa=CurrencyValue.from_gbp(old_point.isa_contribution_gbp or 0.0),
        gia=CurrencyValue.from_gbp(old_point.gia_contribution_gbp or 0.0),
        brokerage=CurrencyValue.from_gbp(0.0),  # Not available in old model
        crypto=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    housing_inv = HousingInvestments(
        house_equity=CurrencyValue.from_gbp(old_point.house_equity_gbp or 0.0),
        rental_property=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    investments_breakdown = InvestmentBreakdown(
        retirement=retirement,
        taxable=taxable,
        housing=housing_inv
    )
    
    # Create net worth breakdown
    net_worth = NetWorthBreakdown(
        liquid_assets=CurrencyValue.from_gbp(old_point.cumulative_portfolio_gbp or 0.0),
        illiquid_assets=CurrencyValue.from_gbp(old_point.house_equity_gbp or 0.0),
        liabilities=CurrencyValue.from_gbp(0.0)  # Not available in old model
    )
    
    # Create unified data point
    return UnifiedFinancialData(
        year=old_point.year,
        age=old_point.age,
        phase=phase,
        jurisdiction=jurisdiction,
        currency=Currency.GBP,  # Default to GBP for old data
        income=income,
        expenses=expenses,
        tax=tax,
        investments=investments_breakdown,
        net_worth=net_worth,
        exchange_rates={Currency.GBP: 1.0}  # Default exchange rates
    )


def convert_old_to_unified_scenario(old_scenario: OldFinancialScenario) -> UnifiedFinancialScenario:
    """Convert old FinancialScenario to new UnifiedFinancialScenario."""
    
    # Determine metadata from scenario name
    metadata = create_scenario_metadata_from_name(old_scenario.name)
    
    # Convert all data points
    unified_data_points = []
    for old_point in old_scenario.data_points:
        unified_point = convert_old_to_unified_data_point(old_point)
        unified_data_points.append(unified_point)
    
    # Create unified scenario
    return UnifiedFinancialScenario(
        name=old_scenario.name,
        description=f"Converted from old model: {old_scenario.name}",
        phase=metadata.relocation_timing and FinancialPhase.UK_TO_INTERNATIONAL or FinancialPhase.UK_ONLY,
        data_points=unified_data_points,
        metadata=metadata
    )


def create_scenario_metadata_from_name(scenario_name: str) -> ScenarioMetadata:
    """Create scenario metadata from scenario name."""
    
    # Determine jurisdiction
    if 'UK_Scenario' in scenario_name:
        jurisdiction = Jurisdiction.UK
        tax_system = "UK Tax System"
        salary_progression = "UK Internal" if 'A' in scenario_name else "UK External"
    elif 'Seattle' in scenario_name:
        jurisdiction = Jurisdiction.US
        tax_system = "US Tax System"
        salary_progression = "US Tech"
    elif 'New_York' in scenario_name:
        jurisdiction = Jurisdiction.US
        tax_system = "US Tax System"
        salary_progression = "US Finance"
    elif 'Dubai' in scenario_name:
        jurisdiction = Jurisdiction.UAE
        tax_system = "Tax-Free"
        salary_progression = "UAE Tech"
    else:
        jurisdiction = Jurisdiction.UK
        tax_system = "UK Tax System"
        salary_progression = "Standard"
    
    # Determine housing strategy
    if 'UK_Home' in scenario_name:
        housing_strategy = "UK Home"
    elif 'Local_Home' in scenario_name:
        housing_strategy = "Local Home"
    else:
        housing_strategy = "Renting"
    
    # Determine relocation timing
    relocation_timing = None
    if 'Year4' in scenario_name:
        relocation_timing = 4
    elif 'Year5' in scenario_name:
        relocation_timing = 5
    
    # Determine investment strategy
    if jurisdiction == Jurisdiction.UK:
        investment_strategy = "UK-focused (ISA, LISA, SIPP)"
    elif jurisdiction == Jurisdiction.US:
        investment_strategy = "US-focused (401k, IRA, Brokerage)"
    elif jurisdiction == Jurisdiction.UAE:
        investment_strategy = "International (Brokerage, Real Estate)"
    else:
        investment_strategy = "Standard"
    
    return ScenarioMetadata(
        jurisdiction=jurisdiction,
        tax_system=tax_system,
        housing_strategy=housing_strategy,
        relocation_timing=relocation_timing,
        salary_progression=salary_progression,
        investment_strategy=investment_strategy,
        description=f"Scenario: {scenario_name}"
    )


def create_unified_currency_value(value: float, currency: str, exchange_rate: float = 1.0) -> CurrencyValue:
    """Create a CurrencyValue from raw data."""
    if currency == "GBP":
        return CurrencyValue.from_gbp(value)
    elif currency == "USD":
        return CurrencyValue.from_usd(value, exchange_rate)
    elif currency == "EUR":
        return CurrencyValue.from_eur(value, exchange_rate)
    else:
        # Default to GBP
        return CurrencyValue.from_gbp(value)


def create_unified_income_breakdown(
    salary_gbp: float = 0.0,
    bonus_gbp: float = 0.0,
    rsu_gbp: float = 0.0,
    other_income_gbp: float = 0.0
) -> IncomeBreakdown:
    """Create an IncomeBreakdown from GBP values."""
    return IncomeBreakdown(
        salary=CurrencyValue.from_gbp(salary_gbp),
        bonus=CurrencyValue.from_gbp(bonus_gbp),
        rsu_vested=CurrencyValue.from_gbp(rsu_gbp),
        other_income=CurrencyValue.from_gbp(other_income_gbp)
    )


def create_unified_expense_breakdown(
    housing_gbp: float = 0.0,
    living_gbp: float = 0.0,
    taxes_gbp: float = 0.0,
    investments_gbp: float = 0.0,
    other_gbp: float = 0.0
) -> ExpenseBreakdown:
    """Create an ExpenseBreakdown from GBP values."""
    return ExpenseBreakdown(
        housing=HousingExpenses(
            rent=CurrencyValue.from_gbp(housing_gbp * 0.6),  # Assume 60% rent
            mortgage=CurrencyValue.from_gbp(housing_gbp * 0.4),  # Assume 40% mortgage
            utilities=CurrencyValue.from_gbp(0.0),
            maintenance=CurrencyValue.from_gbp(0.0),
            property_tax=CurrencyValue.from_gbp(0.0)
        ),
        living=LivingExpenses(
            food=CurrencyValue.from_gbp(living_gbp * 0.3),
            transport=CurrencyValue.from_gbp(living_gbp * 0.2),
            healthcare=CurrencyValue.from_gbp(living_gbp * 0.1),
            entertainment=CurrencyValue.from_gbp(living_gbp * 0.2),
            clothing=CurrencyValue.from_gbp(living_gbp * 0.1),
            personal_care=CurrencyValue.from_gbp(living_gbp * 0.1)
        ),
        taxes=TaxExpenses(
            income_tax=CurrencyValue.from_gbp(taxes_gbp * 0.7),
            social_security=CurrencyValue.from_gbp(taxes_gbp * 0.3),
            property_tax=CurrencyValue.from_gbp(0.0),
            other_taxes=CurrencyValue.from_gbp(0.0)
        ),
        investments=InvestmentExpenses(
            retirement_contributions=CurrencyValue.from_gbp(investments_gbp * 0.8),
            investment_fees=CurrencyValue.from_gbp(investments_gbp * 0.1),
            insurance=CurrencyValue.from_gbp(investments_gbp * 0.1)
        ),
        other=OtherExpenses(
            education=CurrencyValue.from_gbp(other_gbp * 0.4),
            travel=CurrencyValue.from_gbp(other_gbp * 0.3),
            gifts=CurrencyValue.from_gbp(other_gbp * 0.2),
            miscellaneous=CurrencyValue.from_gbp(other_gbp * 0.1)
        )
    )


def create_unified_tax_breakdown(
    income_tax_gbp: float = 0.0,
    social_security_gbp: float = 0.0,
    other_taxes_gbp: float = 0.0
) -> TaxBreakdown:
    """Create a TaxBreakdown from GBP values."""
    return TaxBreakdown(
        income_tax=CurrencyValue.from_gbp(income_tax_gbp),
        social_security=CurrencyValue.from_gbp(social_security_gbp),
        other_taxes=CurrencyValue.from_gbp(other_taxes_gbp)
    )


def create_unified_investment_breakdown(
    retirement_gbp: float = 0.0,
    taxable_gbp: float = 0.0,
    housing_gbp: float = 0.0
) -> InvestmentBreakdown:
    """Create an InvestmentBreakdown from GBP values."""
    return InvestmentBreakdown(
        retirement=RetirementInvestments(
            pension=CurrencyValue.from_gbp(retirement_gbp * 0.4),
            lisa=CurrencyValue.from_gbp(retirement_gbp * 0.2),
            sipp=CurrencyValue.from_gbp(retirement_gbp * 0.2),
            ira=CurrencyValue.from_gbp(retirement_gbp * 0.1),
            employer_match=CurrencyValue.from_gbp(retirement_gbp * 0.1)
        ),
        taxable=TaxableInvestments(
            isa=CurrencyValue.from_gbp(taxable_gbp * 0.4),
            gia=CurrencyValue.from_gbp(taxable_gbp * 0.3),
            brokerage=CurrencyValue.from_gbp(taxable_gbp * 0.2),
            crypto=CurrencyValue.from_gbp(taxable_gbp * 0.1)
        ),
        housing=HousingInvestments(
            house_equity=CurrencyValue.from_gbp(housing_gbp * 0.8),
            rental_property=CurrencyValue.from_gbp(housing_gbp * 0.2)
        )
    )


def create_unified_net_worth_breakdown(
    liquid_assets_gbp: float = 0.0,
    illiquid_assets_gbp: float = 0.0,
    liabilities_gbp: float = 0.0
) -> NetWorthBreakdown:
    """Create a NetWorthBreakdown from GBP values."""
    return NetWorthBreakdown(
        liquid_assets=CurrencyValue.from_gbp(liquid_assets_gbp),
        illiquid_assets=CurrencyValue.from_gbp(illiquid_assets_gbp),
        liabilities=CurrencyValue.from_gbp(liabilities_gbp)
    ) 