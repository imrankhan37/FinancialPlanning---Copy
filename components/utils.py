"""
Utility functions for the financial planning dashboard.
Includes formatting, color management, and helper functions.
"""

from typing import Dict, List, Any, Tuple, Union
import locale


def format_currency(amount: float, currency: str = "GBP") -> str:
    """
    Format currency amounts with proper locale formatting.
    
    Args:
        amount: Amount to format
        currency: Currency code (GBP, USD, etc.)
    
    Returns:
        Formatted currency string
    """
    try:
        # Set locale for proper formatting
        locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
    except:
        # Fallback if locale not available
        pass
    
    if currency == "GBP":
        return f"£{amount:,.0f}"
    elif currency == "USD":
        return f"${amount:,.0f}"
    else:
        return f"{amount:,.0f}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage values.
    
    Args:
        value: Percentage value (0-100)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"


def get_scenario_color(scenario_name: str) -> str:
    """
    Get color for a scenario based on its type and location.
    
    Args:
        scenario_name: Name of the scenario
    
    Returns:
        Hex color code
    """
    # Color scheme based on scenario type
    if 'UK_Scenario' in scenario_name:
        if 'A' in scenario_name:
            return '#1f77b4'  # Blue for UK Scenario A
        else:
            return '#ff7f0e'  # Orange for UK Scenario B
    
    elif 'Seattle' in scenario_name:
        if 'Year4' in scenario_name:
            return '#2ca02c' if 'UK_Home' in scenario_name else '#d62728'  # Green/Red
        else:
            return '#9467bd' if 'UK_Home' in scenario_name else '#8c564b'  # Purple/Brown
    
    elif 'New_York' in scenario_name:
        if 'Year4' in scenario_name:
            return '#e377c2' if 'UK_Home' in scenario_name else '#7f7f7f'  # Pink/Gray
        else:
            return '#bcbd22' if 'UK_Home' in scenario_name else '#17becf'  # Yellow/Cyan
    
    elif 'Dubai' in scenario_name:
        if 'Year4' in scenario_name:
            return '#ff9896' if 'UK_Home' in scenario_name else '#98df8a'  # Light Red/Green
        else:
            return '#fdd0a2' if 'UK_Home' in scenario_name else '#c5b0d5'  # Light Orange/Purple
    
    else:
        return '#636363'  # Default gray


def create_hover_template(metric: str, currency: str = "GBP") -> str:
    """
    Create hover template for Plotly charts.
    
    Args:
        metric: Metric name
        currency: Currency code
    
    Returns:
        Hover template string
    """
    if currency == "GBP":
        return f'<b>%{{fullData.name}}</b><br>{metric}: £%{{y:,.0f}}<extra></extra>'
    else:
        return f'<b>%{{fullData.name}}</b><br>{metric}: %{{y:,.0f}}<extra></extra>'


def calculate_percentage_change(initial: float, final: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        initial: Initial value
        final: Final value
    
    Returns:
        Percentage change
    """
    if initial == 0:
        return 0
    return ((final - initial) / initial) * 100


def calculate_compound_growth_rate(initial: float, final: float, periods: int) -> float:
    """
    Calculate compound annual growth rate.
    
    Args:
        initial: Initial value
        final: Final value
        periods: Number of periods
    
    Returns:
        Compound growth rate as percentage
    """
    if initial <= 0 or periods <= 0:
        return 0
    
    growth_rate: float = (final / initial) ** (1 / periods) - 1
    return growth_rate * 100


def format_large_number(value: float) -> str:
    """
    Format large numbers with K, M, B suffixes.
    
    Args:
        value: Number to format
    
    Returns:
        Formatted string
    """
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:,.0f}"


def get_scenario_category(scenario_name: str) -> str:
    """
    Get the category of a scenario.
    
    Args:
        scenario_name: Name of the scenario
    
    Returns:
        Category string
    """
    if 'UK_Scenario' in scenario_name:
        return 'UK'
    elif 'Seattle' in scenario_name:
        return 'Seattle'
    elif 'New_York' in scenario_name:
        return 'New York'
    elif 'Dubai' in scenario_name:
        return 'Dubai'
    else:
        return 'Other'


def get_scenario_tax_status(scenario_name: str) -> str:
    """
    Get the tax status of a scenario.
    
    Args:
        scenario_name: Name of the scenario
    
    Returns:
        Tax status string
    """
    if 'Dubai' in scenario_name:
        return 'Tax-Free'
    else:
        return 'Taxed'


def get_scenario_housing_strategy(scenario_name: str) -> str:
    """
    Get the housing strategy of a scenario.
    
    Args:
        scenario_name: Name of the scenario
    
    Returns:
        Housing strategy string
    """
    if 'UK_Home' in scenario_name:
        return 'UK Home'
    elif 'Local_Home' in scenario_name:
        return 'Local Home'
    else:
        return 'N/A'


def get_scenario_relocation_timing(scenario_name: str) -> str:
    """
    Get the relocation timing for delayed relocation scenarios.
    
    Args:
        scenario_name: Name of the scenario
    
    Returns:
        Relocation timing string
    """
    if 'Year4' in scenario_name:
        return 'Year 4 (3 UK years)'
    elif 'Year5' in scenario_name:
        return 'Year 5 (4 UK years)'
    else:
        return 'N/A'


def create_scenario_summary(scenario_name: str, metrics: Dict[str, Any]) -> Dict[str, Union[str, float]]:
    """
    Create a summary dictionary for a scenario.
    
    Args:
        scenario_name: Name of the scenario
        metrics: Dictionary containing scenario metrics
    
    Returns:
        Summary dictionary
    """
    return {
        'name': scenario_name,
        'category': get_scenario_category(scenario_name),
        'tax_status': get_scenario_tax_status(scenario_name),
        'housing_strategy': get_scenario_housing_strategy(scenario_name),
        'relocation_timing': get_scenario_relocation_timing(scenario_name),
        'final_net_worth': metrics.get('final_net_worth', 0),
        'avg_annual_savings': metrics.get('avg_annual_savings', 0),
        'total_tax_burden': metrics.get('total_tax_burden', 0),
        'avg_savings_rate': metrics.get('avg_savings_rate', 0)
    }


def validate_scenario_selection(selected_scenarios: List[str]) -> bool:
    """
    Validate scenario selection.
    
    Args:
        selected_scenarios: List of selected scenario names
    
    Returns:
        True if selection is valid
    """
    if not selected_scenarios:
        return False
    
    if len(selected_scenarios) > 3:
        return False
    
    return True


def get_scenario_comparison_insights(scenario1_metrics: Dict[str, Any], scenario2_metrics: Dict[str, Any]) -> List[str]:
    """
    Generate insights for scenario comparison.
    
    Args:
        scenario1_metrics: Metrics for first scenario
        scenario2_metrics: Metrics for second scenario
    
    Returns:
        List of insight strings
    """
    insights: List[str] = []
    
    # Net worth comparison
    net_worth_diff: float = scenario1_metrics['final_net_worth'] - scenario2_metrics['final_net_worth']
    if abs(net_worth_diff) > 10000:  # Significant difference
        if net_worth_diff > 0:
            insights.append(f"Scenario 1 has £{format_large_number(net_worth_diff)} higher final net worth")
        else:
            insights.append(f"Scenario 2 has £{format_large_number(abs(net_worth_diff))} higher final net worth")
    
    # Savings rate comparison
    savings_diff: float = scenario1_metrics['avg_savings_rate'] - scenario2_metrics['avg_savings_rate']
    if abs(savings_diff) > 2:  # Significant difference
        if savings_diff > 0:
            insights.append(f"Scenario 1 has {savings_diff:.1f}% higher savings rate")
        else:
            insights.append(f"Scenario 2 has {abs(savings_diff):.1f}% higher savings rate")
    
    # Tax burden comparison
    tax_diff: float = scenario1_metrics['total_tax_burden'] - scenario2_metrics['total_tax_burden']
    if abs(tax_diff) > 5000:  # Significant difference
        if tax_diff < 0:
            insights.append(f"Scenario 1 has £{format_large_number(abs(tax_diff))} lower tax burden")
        else:
            insights.append(f"Scenario 2 has £{format_large_number(tax_diff)} lower tax burden")
    
    return insights


def create_performance_ranking_table(rankings: Dict[str, List[Tuple[str, float]]]) -> str:
    """
    Create a formatted table string for performance rankings.
    
    Args:
        rankings: Dictionary containing ranking data
    
    Returns:
        Formatted table string
    """
    table_rows: List[str] = []
    
    # Net worth rankings
    table_rows.append("<strong>Net Worth Rankings:</strong>")
    for i, (scenario, value) in enumerate(rankings['net_worth'][:5], 1):
        table_rows.append(f"{i}. {scenario}: {format_currency(value)}")
    
    table_rows.append("")  # Empty line
    
    # Savings rate rankings
    table_rows.append("<strong>Savings Rate Rankings:</strong>")
    for i, (scenario, value) in enumerate(rankings['savings_rate'][:5], 1):
        table_rows.append(f"{i}. {scenario}: {format_percentage(value)}")
    
    return "\n".join(table_rows) 