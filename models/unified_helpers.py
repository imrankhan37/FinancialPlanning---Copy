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
from .performance_optimizations import (
    optimize_currency_value_creation,
    optimize_scenario_analysis,
    get_performance_summary,
    clear_all_caches
)


def convert_old_to_unified_data_point(old_point: OldFinancialDataPoint) -> UnifiedFinancialData:
    """Convert old FinancialDataPoint to new UnifiedFinancialData."""
    
    # Determine phase and jurisdiction from old data
    phase = FinancialPhase.UK_ONLY if old_point.phase.value == "UK" else FinancialPhase.INTERNATIONAL_ONLY
    jurisdiction = Jurisdiction.UK if old_point.phase.value == "UK" else Jurisdiction.US  # Default to US for international
    
    # Create income breakdown with optimized currency conversion
    income = IncomeBreakdown(
        salary=optimize_currency_value_creation(old_point.gross_salary_gbp_equiv or 0.0, Currency.GBP),
        bonus=optimize_currency_value_creation(old_point.gross_bonus_gbp_equiv or 0.0, Currency.GBP),
        rsu_vested=optimize_currency_value_creation(old_point.vested_rsu_gbp_equiv or 0.0, Currency.GBP),
        other_income=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    # Create expense breakdown with optimized currency conversion
    housing = HousingExpenses(
        rent=optimize_currency_value_creation(old_point.rent_gbp or 0.0, Currency.GBP),
        mortgage=optimize_currency_value_creation(old_point.mortgage_payment_gbp or 0.0, Currency.GBP),
        utilities=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        maintenance=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        property_tax=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    living = LivingExpenses(
        food=optimize_currency_value_creation(old_point.personal_expenses_gbp or 0.0, Currency.GBP),
        transport=optimize_currency_value_creation(old_point.travel_expenses_gbp or 0.0, Currency.GBP),
        healthcare=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        entertainment=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        clothing=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        personal_care=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    taxes = TaxExpenses(
        income_tax=optimize_currency_value_creation(old_point.income_tax_gbp or 0.0, Currency.GBP),
        social_security=optimize_currency_value_creation(old_point.national_insurance_gbp or 0.0, Currency.GBP),
        property_tax=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        other_taxes=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    investments = InvestmentExpenses(
        retirement_contributions=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        investment_fees=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        insurance=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    other = OtherExpenses(
        education=optimize_currency_value_creation(old_point.university_repayment_gbp or 0.0, Currency.GBP),
        travel=optimize_currency_value_creation(old_point.travel_expenses_gbp or 0.0, Currency.GBP),
        gifts=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        miscellaneous=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    expenses = ExpenseBreakdown(
        housing=housing,
        living=living,
        taxes=taxes,
        investments=investments,
        other=other
    )
    
    # Create tax breakdown with optimized currency conversion
    tax = TaxBreakdown(
        income_tax=optimize_currency_value_creation(old_point.income_tax_gbp or 0.0, Currency.GBP),
        social_security=optimize_currency_value_creation(old_point.national_insurance_gbp or 0.0, Currency.GBP),
        other_taxes=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    # Create investment breakdown with optimized currency conversion
    retirement = RetirementInvestments(
        pension=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        lisa=optimize_currency_value_creation(old_point.lisa_contribution_gbp or 0.0, Currency.GBP),
        sipp=optimize_currency_value_creation(old_point.sipp_contribution_gbp or 0.0, Currency.GBP),
        ira=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        employer_match=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    taxable = TaxableInvestments(
        isa=optimize_currency_value_creation(old_point.isa_contribution_gbp or 0.0, Currency.GBP),
        gia=optimize_currency_value_creation(old_point.gia_contribution_gbp or 0.0, Currency.GBP),
        brokerage=optimize_currency_value_creation(0.0, Currency.GBP),  # Not available in old model
        crypto=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    housing_inv = HousingInvestments(
        house_equity=optimize_currency_value_creation(old_point.house_equity_gbp or 0.0, Currency.GBP),
        rental_property=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
    )
    
    investments_breakdown = InvestmentBreakdown(
        retirement=retirement,
        taxable=taxable,
        housing=housing_inv
    )
    
    # Create net worth breakdown with optimized currency conversion
    net_worth = NetWorthBreakdown(
        liquid_assets=optimize_currency_value_creation(old_point.cumulative_portfolio_gbp or 0.0, Currency.GBP),
        illiquid_assets=optimize_currency_value_creation(old_point.house_equity_gbp or 0.0, Currency.GBP),
        liabilities=optimize_currency_value_creation(0.0, Currency.GBP)  # Not available in old model
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
    """Convert old FinancialScenario to new UnifiedFinancialScenario with performance optimization."""
    
    # Use optimized scenario analysis
    def analyze_scenario(scenarios):
        # Determine metadata from scenario name
        metadata = create_scenario_metadata_from_name(old_scenario.name)
        
        # Convert all data points with optimized conversion
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
    
    # Use optimized analysis
    return optimize_scenario_analysis([old_scenario], lambda s: analyze_scenario(s[0]))['result']


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
    """Create a CurrencyValue from raw data with performance optimization."""
    currency_enum = Currency(currency)
    return optimize_currency_value_creation(value, currency_enum, exchange_rate)


def create_unified_income_breakdown(
    salary_gbp: float = 0.0,
    bonus_gbp: float = 0.0,
    rsu_gbp: float = 0.0,
    other_income_gbp: float = 0.0
) -> IncomeBreakdown:
    """Create an IncomeBreakdown from GBP values with performance optimization."""
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
    other_gbp: float = 0.0
) -> ExpenseBreakdown:
    """Create an ExpenseBreakdown from GBP values with performance optimization."""
    return ExpenseBreakdown(
        housing=HousingExpenses(
            rent=optimize_currency_value_creation(housing_gbp * 0.6, Currency.GBP),  # Assume 60% rent
            mortgage=optimize_currency_value_creation(housing_gbp * 0.4, Currency.GBP),  # Assume 40% mortgage
            utilities=optimize_currency_value_creation(0.0, Currency.GBP),
            maintenance=optimize_currency_value_creation(0.0, Currency.GBP),
            property_tax=optimize_currency_value_creation(0.0, Currency.GBP)
        ),
        living=LivingExpenses(
            food=optimize_currency_value_creation(living_gbp * 0.3, Currency.GBP),
            transport=optimize_currency_value_creation(living_gbp * 0.2, Currency.GBP),
            healthcare=optimize_currency_value_creation(living_gbp * 0.1, Currency.GBP),
            entertainment=optimize_currency_value_creation(living_gbp * 0.2, Currency.GBP),
            clothing=optimize_currency_value_creation(living_gbp * 0.1, Currency.GBP),
            personal_care=optimize_currency_value_creation(living_gbp * 0.1, Currency.GBP)
        ),
        taxes=TaxExpenses(
            income_tax=optimize_currency_value_creation(taxes_gbp * 0.7, Currency.GBP),
            social_security=optimize_currency_value_creation(taxes_gbp * 0.3, Currency.GBP),
            property_tax=optimize_currency_value_creation(0.0, Currency.GBP),
            other_taxes=optimize_currency_value_creation(0.0, Currency.GBP)
        ),
        investments=InvestmentExpenses(
            retirement_contributions=optimize_currency_value_creation(investments_gbp * 0.8, Currency.GBP),
            investment_fees=optimize_currency_value_creation(investments_gbp * 0.1, Currency.GBP),
            insurance=optimize_currency_value_creation(investments_gbp * 0.1, Currency.GBP)
        ),
        other=OtherExpenses(
            education=optimize_currency_value_creation(other_gbp * 0.4, Currency.GBP),
            travel=optimize_currency_value_creation(other_gbp * 0.3, Currency.GBP),
            gifts=optimize_currency_value_creation(other_gbp * 0.2, Currency.GBP),
            miscellaneous=optimize_currency_value_creation(other_gbp * 0.1, Currency.GBP)
        )
    )


def create_unified_tax_breakdown(
    income_tax_gbp: float = 0.0,
    social_security_gbp: float = 0.0,
    other_taxes_gbp: float = 0.0
) -> TaxBreakdown:
    """Create a TaxBreakdown from GBP values with performance optimization."""
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
    """Create an InvestmentBreakdown from GBP values with performance optimization."""
    return InvestmentBreakdown(
        retirement=RetirementInvestments(
            pension=optimize_currency_value_creation(retirement_gbp * 0.4, Currency.GBP),
            lisa=optimize_currency_value_creation(retirement_gbp * 0.2, Currency.GBP),
            sipp=optimize_currency_value_creation(retirement_gbp * 0.2, Currency.GBP),
            ira=optimize_currency_value_creation(retirement_gbp * 0.1, Currency.GBP),
            employer_match=optimize_currency_value_creation(retirement_gbp * 0.1, Currency.GBP)
        ),
        taxable=TaxableInvestments(
            isa=optimize_currency_value_creation(taxable_gbp * 0.4, Currency.GBP),
            gia=optimize_currency_value_creation(taxable_gbp * 0.3, Currency.GBP),
            brokerage=optimize_currency_value_creation(taxable_gbp * 0.2, Currency.GBP),
            crypto=optimize_currency_value_creation(taxable_gbp * 0.1, Currency.GBP)
        ),
        housing=HousingInvestments(
            house_equity=optimize_currency_value_creation(housing_gbp * 0.8, Currency.GBP),
            rental_property=optimize_currency_value_creation(housing_gbp * 0.2, Currency.GBP)
        )
    )


def create_unified_net_worth_breakdown(
    liquid_assets_gbp: float = 0.0,
    illiquid_assets_gbp: float = 0.0,
    liabilities_gbp: float = 0.0
) -> NetWorthBreakdown:
    """Create a NetWorthBreakdown from GBP values with performance optimization."""
    return NetWorthBreakdown(
        liquid_assets=optimize_currency_value_creation(liquid_assets_gbp, Currency.GBP),
        illiquid_assets=optimize_currency_value_creation(illiquid_assets_gbp, Currency.GBP),
        liabilities=optimize_currency_value_creation(liabilities_gbp, Currency.GBP)
    )


def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics for monitoring."""
    return get_performance_summary()


def clear_performance_caches() -> None:
    """Clear all performance caches."""
    clear_all_caches() 