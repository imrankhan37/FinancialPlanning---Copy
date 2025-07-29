"""
Data validation and error handling utilities for the Financial Planning Dashboard.
"""

import streamlit as st
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from constants import ERROR_MESSAGES, SUCCESS_MESSAGES


def validate_session_state() -> bool:
    """
    Validate that required session state variables are initialized.
    
    Returns:
        bool: True if session state is valid, False otherwise
    """
    try:
        required_keys = ['selected_scenarios', 'year_range']
        for key in required_keys:
            if key not in st.session_state:
                st.session_state[key] = [] if key == 'selected_scenarios' else [1, 10]
        return True
    except Exception as e:
        st.error(f"Session state validation failed: {str(e)}")
        return False


def validate_scenario_data(scenarios: Dict[str, Any]) -> bool:
    """
    Validate that scenario data is properly structured.
    
    Args:
        scenarios: Dictionary of scenario data
        
    Returns:
        bool: True if data is valid, False otherwise
    """
    if not scenarios:
        st.warning("No scenarios provided for validation.")
        return False
    
    try:
        for scenario_name, scenario in scenarios.items():
            if not hasattr(scenario, 'data_points'):
                st.error(f"Scenario {scenario_name} missing data_points attribute.")
                return False
            
            if not scenario.data_points:
                st.warning(f"Scenario {scenario_name} has no data points.")
                continue
            
            # Validate each data point
            for i, point in enumerate(scenario.data_points):
                if not hasattr(point, '__dict__'):
                    st.error(f"Data point {i} in scenario {scenario_name} is not a valid object.")
                    return False
        
        return True
    except Exception as e:
        st.error(f"Scenario data validation failed: {str(e)}")
        return False


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling division by zero.
    
    Args:
        numerator: The numerator value
        denominator: The denominator value
        default: Default value to return if denominator is zero
        
    Returns:
        float: The result of the division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default


def validate_numeric_value(value: Any, min_value: Optional[float] = None, 
                          max_value: Optional[float] = None) -> bool:
    """
    Validate that a value is numeric and within specified bounds.
    
    Args:
        value: The value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        
    Returns:
        bool: True if value is valid, False otherwise
    """
    try:
        numeric_value = float(value)
        
        if min_value is not None and numeric_value < min_value:
            return False
        
        if max_value is not None and numeric_value > max_value:
            return False
        
        return True
    except (TypeError, ValueError):
        return False


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that a DataFrame has the required columns.
    
    Args:
        df: The DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        bool: True if DataFrame is valid, False otherwise
    """
    try:
        if df is None or df.empty:
            return False
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return False
        
        return True
    except Exception as e:
        st.error(f"DataFrame validation failed: {str(e)}")
        return False


def handle_data_loading_error(error: Exception, context: str = "") -> None:
    """
    Handle data loading errors with appropriate user feedback.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    error_message = f"Error loading data{f' in {context}' if context else ''}: {str(error)}"
    st.error(error_message)
    
    # Provide helpful suggestions based on error type
    if "session_state" in str(error).lower():
        st.info("Try refreshing the page to reinitialize the application.")
    elif "data" in str(error).lower():
        st.info("Check that all scenario data files are available and properly formatted.")
    elif "validation" in str(error).lower():
        st.info("Please verify that all input data is in the correct format.")


def validate_user_inputs(selected_scenarios: List[str], year_range: List[int]) -> bool:
    """
    Validate user inputs from the interface.
    
    Args:
        selected_scenarios: List of selected scenario names
        year_range: List containing start and end years
        
    Returns:
        bool: True if inputs are valid, False otherwise
    """
    try:
        # Validate selected scenarios
        if not selected_scenarios:
            st.warning("Please select at least one scenario to analyze.")
            return False
        
        # Validate year range
        if len(year_range) != 2:
            st.error("Year range must contain exactly two values.")
            return False
        
        start_year, end_year = year_range
        if not validate_numeric_value(start_year, min_value=1):
            st.error("Start year must be a positive number.")
            return False
        
        if not validate_numeric_value(end_year, min_value=start_year):
            st.error("End year must be greater than or equal to start year.")
            return False
        
        return True
    except Exception as e:
        st.error(f"Input validation failed: {str(e)}")
        return False


def log_validation_error(error: Exception, context: str = "") -> None:
    """
    Log validation errors for debugging purposes.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    # In a production environment, this would log to a file or monitoring service
    print(f"Validation Error{f' in {context}' if context else ''}: {str(error)}")


def create_error_summary(errors: List[str]) -> str:
    """
    Create a summary of validation errors.
    
    Args:
        errors: List of error messages
        
    Returns:
        str: Formatted error summary
    """
    if not errors:
        return "No validation errors found."
    
    summary = "Validation Errors:\n"
    for i, error in enumerate(errors, 1):
        summary += f"{i}. {error}\n"
    
    return summary 