"""
Unified Financial Data Helpers
Helper functions for creating and managing unified financial data models.
"""

from typing import Dict, Any, List
from .unified_financial_data import (
    UnifiedFinancialData, UnifiedFinancialScenario, ScenarioMetadata,
    CurrencyValue, Currency, Jurisdiction, FinancialPhase,
    IncomeBreakdown, ExpenseBreakdown, TaxBreakdown, InvestmentBreakdown, NetWorthBreakdown,
    HousingExpenses, LivingExpenses, TaxExpenses, InvestmentExpenses, OtherExpenses,
    RetirementInvestments, TaxableInvestments, HousingInvestments
)
from .performance_optimizations import (
    optimize_currency_value_creation,
    optimize_scenario_analysis,
    get_performance_summary,
    clear_all_caches
)


def create_scenario_metadata_from_name(scenario_name: str) -> ScenarioMetadata:
    """Create scenario metadata from scenario name with intelligent parsing."""
    
    # Determine jurisdiction and phase from scenario name
    jurisdiction = Jurisdiction.UK
    phase = FinancialPhase.UK_ONLY
    
    scenario_lower = scenario_name.lower()
    
    # Determine jurisdiction
    if any(location in scenario_lower for location in ['dubai', 'uae', 'emirates']):
        jurisdiction = Jurisdiction.UAE
    elif any(location in scenario_lower for location in ['seattle', 'us', 'usa', 'america']):
        jurisdiction = Jurisdiction.US
    elif any(location in scenario_lower for location in ['uk', 'britain', 'england']):
        jurisdiction = Jurisdiction.UK
    elif any(location in scenario_lower for location in ['eu', 'europe']):
        jurisdiction = Jurisdiction.EU
    
    # Determine phase
    if any(phase_indicator in scenario_lower for phase_indicator in ['international', 'abroad', 'overseas']):
        if jurisdiction == Jurisdiction.UK:
            phase = FinancialPhase.UK_TO_INTERNATIONAL
        else:
            phase = FinancialPhase.INTERNATIONAL_ONLY
    elif any(phase_indicator in scenario_lower for phase_indicator in ['delayed', 'relocation', 'move']):
        phase = FinancialPhase.UK_TO_INTERNATIONAL
    else:
        phase = FinancialPhase.UK_ONLY
    
    # Determine scenario type
    scenario_type = "standard"
    if any(type_indicator in scenario_lower for type_indicator in ['conservative', 'safe', 'low']):
        scenario_type = "conservative"
    elif any(type_indicator in scenario_lower for type_indicator in ['aggressive', 'high', 'optimistic']):
        scenario_type = "aggressive"
    elif any(type_indicator in scenario_lower for type_indicator in ['moderate', 'balanced', 'medium']):
        scenario_type = "moderate"
    
    # Determine housing strategy
    housing_strategy = "uk_home"
    if any(strategy in scenario_lower for strategy in ['rent', 'renting']):
        housing_strategy = "rent"
    elif any(strategy in scenario_lower for strategy in ['buy', 'purchase', 'mortgage']):
        housing_strategy = "buy"
    elif any(strategy in scenario_lower for strategy in ['invest', 'investment']):
        housing_strategy = "investment"
    
    # Determine tax system
    if jurisdiction == Jurisdiction.UK:
        tax_system = "UK Tax System"
    elif jurisdiction == Jurisdiction.US:
        tax_system = "US Tax System"
    elif jurisdiction == Jurisdiction.UAE:
        tax_system = "Tax-Free"
    elif jurisdiction == Jurisdiction.EU:
        tax_system = "EU Tax System"
    else:
        tax_system = "Standard Tax System"
    
    # Determine salary progression
    if 'A' in scenario_name:
        salary_progression = "UK Internal Growth"
    elif 'B' in scenario_name:
        salary_progression = "UK External Growth"
    elif jurisdiction == Jurisdiction.US:
        salary_progression = "US Tech Progression"
    elif jurisdiction == Jurisdiction.UAE:
        salary_progression = "UAE Tech Progression"
    else:
        salary_progression = "Standard Progression"
    
    # Determine investment strategy
    if jurisdiction == Jurisdiction.UK:
        investment_strategy = "UK-focused (ISA, LISA, SIPP)"
    elif jurisdiction == Jurisdiction.US:
        investment_strategy = "US-focused (401k, IRA, Brokerage)"
    elif jurisdiction == Jurisdiction.UAE:
        investment_strategy = "International (Brokerage, Real Estate)"
    else:
        investment_strategy = "Standard Investment Strategy"
    
    # Determine relocation timing
    relocation_timing = None
    if 'year4' in scenario_lower:
        relocation_timing = 4
    elif 'year5' in scenario_lower:
        relocation_timing = 5
    
    return ScenarioMetadata(
        jurisdiction=jurisdiction,
        tax_system=tax_system,
        housing_strategy=housing_strategy,
        relocation_timing=relocation_timing,
        salary_progression=salary_progression,
        investment_strategy=investment_strategy,
        description=f"Generated scenario: {scenario_name}"
    )


def create_unified_currency_value(value: float, currency: str, exchange_rate: float = 1.0) -> CurrencyValue:
    """Create a unified currency value with optimized creation."""
    return optimize_currency_value_creation(value, Currency(currency), exchange_rate)


def create_unified_income_breakdown(
    salary_gbp: float = 0.0,
    bonus_gbp: float = 0.0,
    rsu_gbp: float = 0.0,
    other_income_gbp: float = 0.0
) -> IncomeBreakdown:
    """Create a unified income breakdown with optimized currency values."""
    
    return IncomeBreakdown(
        salary=optimize_currency_value_creation(salary_gbp, Currency.GBP),
        bonus=optimize_currency_value_creation(bonus_gbp, Currency.GBP),
        rsu_vested=optimize_currency_value_creation(rsu_gbp, Currency.GBP),
        other_income=optimize_currency_value_creation(other_income_gbp, Currency.GBP)
    )


def create_unified_expense_breakdown(
    housing_gbp: float = 0.0,
    living_gbp: float = 0.0,
    taxes_gbp: float = 0.0,
    investments_gbp: float = 0.0,
    other_gbp: float = 0.0,
    location: str = "UK",
    year: int = 2025,
    config: dict = None,
    gross_income: float = 0.0
) -> ExpenseBreakdown:
    """Create a unified expense breakdown with optimized currency values."""
    
    # Create sub-breakdowns
    housing = HousingExpenses(
        rent=optimize_currency_value_creation(housing_gbp * 0.6, Currency.GBP),  # Assume 60% rent
        mortgage=optimize_currency_value_creation(housing_gbp * 0.3, Currency.GBP),  # Assume 30% mortgage
        utilities=optimize_currency_value_creation(housing_gbp * 0.05, Currency.GBP),  # Assume 5% utilities
        maintenance=optimize_currency_value_creation(housing_gbp * 0.03, Currency.GBP),  # Assume 3% maintenance
        property_tax=optimize_currency_value_creation(housing_gbp * 0.02, Currency.GBP)  # Assume 2% property tax
    )
    
    living = LivingExpenses(
        food=optimize_currency_value_creation(living_gbp * 0.3, Currency.GBP),  # Assume 30% food
        transport=optimize_currency_value_creation(living_gbp * 0.25, Currency.GBP),  # Assume 25% transport
        healthcare=optimize_currency_value_creation(living_gbp * 0.15, Currency.GBP),  # Assume 15% healthcare
        entertainment=optimize_currency_value_creation(living_gbp * 0.15, Currency.GBP),  # Assume 15% entertainment
        clothing=optimize_currency_value_creation(living_gbp * 0.1, Currency.GBP),  # Assume 10% clothing
        personal_care=optimize_currency_value_creation(living_gbp * 0.05, Currency.GBP)  # Assume 5% personal care
    )
    
    # Use actual tax calculations if config and gross_income are provided
    if config and gross_income > 0:
        try:
            from utils.tax.tax_utils import get_tax_breakdown_for_location
            taxes = get_tax_breakdown_for_location(gross_income, location, year, config)
        except ImportError:
            # Fallback to simplified tax breakdown
            taxes = TaxExpenses(
                income_tax=optimize_currency_value_creation(taxes_gbp * 0.8, Currency.GBP),  # Assume 80% income tax
                social_security=optimize_currency_value_creation(taxes_gbp * 0.15, Currency.GBP),  # Assume 15% social security
                property_tax=optimize_currency_value_creation(taxes_gbp * 0.03, Currency.GBP),  # Assume 3% property tax
                other_taxes=optimize_currency_value_creation(taxes_gbp * 0.02, Currency.GBP)  # Assume 2% other taxes
            )
    else:
        # Simplified tax breakdown
        taxes = TaxExpenses(
            income_tax=optimize_currency_value_creation(taxes_gbp * 0.8, Currency.GBP),  # Assume 80% income tax
            social_security=optimize_currency_value_creation(taxes_gbp * 0.15, Currency.GBP),  # Assume 15% social security
            property_tax=optimize_currency_value_creation(taxes_gbp * 0.03, Currency.GBP),  # Assume 3% property tax
            other_taxes=optimize_currency_value_creation(taxes_gbp * 0.02, Currency.GBP)  # Assume 2% other taxes
        )
    
    # Simplified investment breakdown
    investments = InvestmentExpenses(
        retirement_contributions=optimize_currency_value_creation(investments_gbp * 0.7, Currency.GBP),  # Assume 70% retirement
        investment_fees=optimize_currency_value_creation(investments_gbp * 0.2, Currency.GBP),  # Assume 20% fees
        insurance=optimize_currency_value_creation(investments_gbp * 0.1, Currency.GBP)  # Assume 10% insurance
    )
    
    other = OtherExpenses(
        education=optimize_currency_value_creation(other_gbp * 0.4, Currency.GBP),  # Assume 40% education
        travel=optimize_currency_value_creation(other_gbp * 0.3, Currency.GBP),  # Assume 30% travel
        gifts=optimize_currency_value_creation(other_gbp * 0.2, Currency.GBP),  # Assume 20% gifts
        miscellaneous=optimize_currency_value_creation(other_gbp * 0.1, Currency.GBP)  # Assume 10% miscellaneous
    )
    
    return ExpenseBreakdown(
        housing=housing,
        living=living,
        taxes=taxes,
        investments=investments,
        other=other
    )


def create_unified_tax_breakdown(
    income_tax_gbp: float = 0.0,
    social_security_gbp: float = 0.0,
    other_taxes_gbp: float = 0.0
) -> TaxBreakdown:
    """Create a unified tax breakdown with optimized currency values."""
    
    return TaxBreakdown(
        income_tax=optimize_currency_value_creation(income_tax_gbp, Currency.GBP),
        social_security=optimize_currency_value_creation(social_security_gbp, Currency.GBP),
        other_taxes=optimize_currency_value_creation(other_taxes_gbp, Currency.GBP)
    )


def create_unified_investment_breakdown(
    retirement_gbp: float = 0.0,
    taxable_gbp: float = 0.0,
    housing_gbp: float = 0.0
) -> InvestmentBreakdown:
    """Create a unified investment breakdown with optimized currency values."""
    
    # Create sub-breakdowns with simplified assumptions
    retirement = RetirementInvestments(
        pension=optimize_currency_value_creation(retirement_gbp * 0.5, Currency.GBP),     # Assume 50% pension
        lisa=optimize_currency_value_creation(retirement_gbp * 0.25, Currency.GBP),       # Assume 25% LISA
        sipp=optimize_currency_value_creation(retirement_gbp * 0.25, Currency.GBP),       # Assume 25% SIPP
        ira=optimize_currency_value_creation(0, Currency.GBP),                            # No IRA for UK
        employer_match=optimize_currency_value_creation(0, Currency.GBP)                   # No employer match for UK
    )
    
    taxable = TaxableInvestments(
        isa=optimize_currency_value_creation(taxable_gbp * 0.5, Currency.GBP),      # Assume 50% ISA
        gia=optimize_currency_value_creation(taxable_gbp * 0.3, Currency.GBP),       # Assume 30% GIA
        brokerage=optimize_currency_value_creation(taxable_gbp * 0.2, Currency.GBP), # Assume 20% brokerage
        crypto=optimize_currency_value_creation(0, Currency.GBP)                     # No crypto for now
    )
    
    housing = HousingInvestments(
        house_equity=optimize_currency_value_creation(housing_gbp * 0.8, Currency.GBP),  # Assume 80% house equity
        rental_property=optimize_currency_value_creation(housing_gbp * 0.2, Currency.GBP)  # Assume 20% rental property
    )
    
    return InvestmentBreakdown(
        retirement=retirement,
        taxable=taxable,
        housing=housing
    )


def create_unified_net_worth_breakdown(
    liquid_assets_gbp: float = 0.0,
    illiquid_assets_gbp: float = 0.0,
    liabilities_gbp: float = 0.0
) -> NetWorthBreakdown:
    """Create a unified net worth breakdown with optimized currency values."""
    
    return NetWorthBreakdown(
        liquid_assets=optimize_currency_value_creation(liquid_assets_gbp, Currency.GBP),
        illiquid_assets=optimize_currency_value_creation(illiquid_assets_gbp, Currency.GBP),
        liabilities=optimize_currency_value_creation(liabilities_gbp, Currency.GBP)
    )


def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics for unified models."""
    return get_performance_summary()


def clear_performance_caches() -> None:
    """Clear all performance caches."""
    clear_all_caches() 


 