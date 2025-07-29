"""
Formatting utilities for the Financial Planning Dashboard.
"""

import pandas as pd
from typing import Union, Optional
from constants import USD_TO_GBP_RATE


def format_currency(value: Union[float, int], currency_symbol: str = "£") -> str:
    """
    Format a numeric value as currency with thousands separators.
    
    Args:
        value: The numeric value to format
        currency_symbol: The currency symbol to use (default: £)
        
    Returns:
        str: Formatted currency string
    """
    try:
        if value is None:
            return f"{currency_symbol}0"
        
        numeric_value = float(value)
        return f"{currency_symbol}{numeric_value:,.0f}"
    except (TypeError, ValueError):
        return f"{currency_symbol}0"


def format_percentage(value: Union[float, int], decimal_places: int = 1) -> str:
    """
    Format a numeric value as a percentage.
    
    Args:
        value: The numeric value to format (as decimal, e.g., 0.25 for 25%)
        decimal_places: Number of decimal places to display
        
    Returns:
        str: Formatted percentage string
    """
    try:
        if value is None:
            return "0.0%"
        
        numeric_value = float(value)
        return f"{numeric_value:.{decimal_places}f}%"
    except (TypeError, ValueError):
        return "0.0%"


def format_number(value: Union[float, int], decimal_places: int = 0) -> str:
    """
    Format a numeric value with thousands separators.
    
    Args:
        value: The numeric value to format
        decimal_places: Number of decimal places to display
        
    Returns:
        str: Formatted number string
    """
    try:
        if value is None:
            return "0"
        
        numeric_value = float(value)
        return f"{numeric_value:,.{decimal_places}f}"
    except (TypeError, ValueError):
        return "0"


def convert_usd_to_gbp(usd_value: Union[float, int]) -> float:
    """
    Convert USD value to GBP using the configured exchange rate.
    
    Args:
        usd_value: The USD value to convert
        
    Returns:
        float: The converted GBP value
    """
    try:
        if usd_value is None:
            return 0.0
        
        return float(usd_value) / USD_TO_GBP_RATE
    except (TypeError, ValueError):
        return 0.0


def convert_gbp_to_usd(gbp_value: Union[float, int]) -> float:
    """
    Convert GBP value to USD using the configured exchange rate.
    
    Args:
        gbp_value: The GBP value to convert
        
    Returns:
        float: The converted USD value
    """
    try:
        if gbp_value is None:
            return 0.0
        
        return float(gbp_value) * USD_TO_GBP_RATE
    except (TypeError, ValueError):
        return 0.0


def extract_numeric_from_currency(currency_string: str) -> float:
    """
    Extract numeric value from a formatted currency string.
    
    Args:
        currency_string: The formatted currency string (e.g., "£1,234,567")
        
    Returns:
        float: The numeric value
    """
    try:
        if not currency_string:
            return 0.0
        
        # Remove currency symbols and commas
        cleaned = currency_string.replace('£', '').replace('$', '').replace(',', '')
        return float(cleaned)
    except (TypeError, ValueError):
        return 0.0


def extract_numeric_from_percentage(percentage_string: str) -> float:
    """
    Extract numeric value from a formatted percentage string.
    
    Args:
        percentage_string: The formatted percentage string (e.g., "24.5%")
        
    Returns:
        float: The numeric value (as decimal)
    """
    try:
        if not percentage_string:
            return 0.0
        
        # Remove percentage symbol
        cleaned = percentage_string.replace('%', '')
        return float(cleaned)
    except (TypeError, ValueError):
        return 0.0


def format_scenario_name(scenario_name: str) -> str:
    """
    Format scenario name for display.
    
    Args:
        scenario_name: The raw scenario name
        
    Returns:
        str: Formatted scenario name
    """
    try:
        if not scenario_name:
            return "Unknown Scenario"
        
        # Replace underscores with spaces and capitalize
        formatted = scenario_name.replace('_', ' ').title()
        return formatted
    except (TypeError, AttributeError):
        return "Unknown Scenario"


def format_year_range(year_range: list) -> str:
    """
    Format year range for display.
    
    Args:
        year_range: List containing start and end years
        
    Returns:
        str: Formatted year range string
    """
    try:
        if not year_range or len(year_range) != 2:
            return "Year 1-10"
        
        start_year, end_year = year_range
        return f"Year {start_year}-{end_year}"
    except (TypeError, ValueError):
        return "Year 1-10"


def create_styled_dataframe(df: 'pd.DataFrame', numeric_columns: list, 
                           highlight_columns: Optional[list] = None) -> 'pd.Styler':
    """
    Create a styled DataFrame with background gradients and highlighting.
    
    Args:
        df: The pandas DataFrame to style
        numeric_columns: List of column names to apply gradients to
        highlight_columns: List of column names to highlight maximum values
        
    Returns:
        pd.Styler: The styled DataFrame
    """
    try:
        styled_df = df.style
        
        # Apply background gradients to numeric columns
        for col in numeric_columns:
            if col in df.columns:
                # Create numeric version for styling
                numeric_col = f"{col}_numeric"
                df[numeric_col] = df[col].apply(extract_numeric_from_currency)
                
                styled_df = styled_df.background_gradient(
                    subset=[numeric_col],
                    cmap='RdYlGn',
                    vmin=df[numeric_col].min(),
                    vmax=df[numeric_col].max()
                )
                
                # Highlight maximum values
                if highlight_columns and col in highlight_columns:
                    styled_df = styled_df.apply(
                        lambda x: ['background-color: #e8f5e8' if i == df[numeric_col].idxmax() else '' 
                                 for i in range(len(x))], 
                        subset=[numeric_col]
                    )
                
                # Hide the numeric column
                styled_df = styled_df.hide(axis='columns', subset=[numeric_col])
        
        return styled_df.hide(axis='index')
    
    except Exception as e:
        # Return unstyled DataFrame if styling fails
        return df.style


def format_metric_card(title: str, value: str, color_gradient: str = "primary") -> str:
    """
    Create HTML for a metric card with consistent styling.
    
    Args:
        title: The card title
        value: The metric value
        color_gradient: The color gradient to use
        
    Returns:
        str: HTML string for the metric card
    """
    from constants import GRADIENT_COLORS
    
    gradient = GRADIENT_COLORS.get(color_gradient, GRADIENT_COLORS['primary'])
    
    return f"""
    <div style="background: {gradient}; padding: 1.5rem; border-radius: 15px; margin: 0.5rem 0; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 2rem; font-weight: 700;">{value}</div>
    </div>
    """ 