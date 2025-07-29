"""
Financial Planning Dashboard - Main Application
A comprehensive Streamlit application for financial scenario analysis and planning.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import importlib.util
import os
from pathlib import Path

# Import utilities and constants
from utils.data import load_all_scenarios, filter_scenarios, filter_scenarios_by_type
from utils.validation import validate_session_state, validate_user_inputs, handle_data_loading_error
from utils.formatting import format_currency, format_percentage, format_scenario_name
from utils.css_loader import load_main_styles
from constants import DEFAULT_SCENARIOS, DEFAULT_YEAR_RANGE, ERROR_MESSAGES, SUCCESS_MESSAGES


def import_page_module(page_name: str, function_name: str):
    """Dynamically import page functions."""
    try:
        spec = importlib.util.spec_from_file_location(
            page_name, 
            os.path.join(os.path.dirname(__file__), 'pages', page_name)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, function_name)
    except Exception as e:
        st.error(f"Failed to import {function_name} from {page_name}: {str(e)}")
        return None


# Import page functions
render_time_series_page = import_page_module('1_Time_Series_Analysis.py', 'render_time_series_page')
render_income_expense_page = import_page_module('2_Income_Expense_Breakdown.py', 'render_income_expense_page')
render_performance_page = import_page_module('3_Performance_Monitoring.py', 'render_performance_page')

# Import components
try:
    from components.scenario_selector import render_scenario_selector
    from components.utils import format_currency as component_format_currency
except ImportError as e:
    st.error(f"Failed to import components: {str(e)}")
    render_scenario_selector = None
    component_format_currency = format_currency


# Page configuration
st.set_page_config(
    page_title="Financial Planning Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load main styles
load_main_styles()


def initialize_session_state():
    """Initialize session state with default values."""
    try:
        if 'selected_scenarios' not in st.session_state:
            st.session_state.selected_scenarios = DEFAULT_SCENARIOS
        if 'year_range' not in st.session_state:
            st.session_state.year_range = list(DEFAULT_YEAR_RANGE)
        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False
        if 'all_scenarios' not in st.session_state:
            st.session_state.all_scenarios = {}
    except Exception as e:
        st.error(f"Failed to initialize session state: {str(e)}")


def calculate_kpis(scenarios_to_analyze: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate Key Performance Indicators for the dashboard.
    
    Args:
        scenarios_to_analyze: Dictionary of scenarios to analyze
        
    Returns:
        Dict containing KPI values
    """
    try:
        if not scenarios_to_analyze:
            return {
                'max_net_worth': 0,
                'avg_yoy_growth': 0,
                'scenarios_count': 0
            }
        
        max_net_worth = 0
        total_yoy_growth = 0
        scenarios_with_growth = 0
        
        for scenario_name, scenario in scenarios_to_analyze.items():
            if scenario.data_points:
                # Net worth calculation
                for point in scenario.data_points:
                    net_worth = 0
                    if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0:
                        net_worth = point.net_worth_gbp_equiv
                    elif hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0:
                        net_worth = point.net_worth_gbp
                    elif hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0:
                        net_worth = point.net_worth_usd / 1.26
                    
                    max_net_worth = max(max_net_worth, net_worth)
                
                # YoY growth calculation
                if len(scenario.data_points) >= 2:
                    yoy_growths = []
                    for i in range(1, len(scenario.data_points)):
                        prev_point = scenario.data_points[i-1]
                        curr_point = scenario.data_points[i]
                        
                        prev_income = 0
                        curr_income = 0
                        
                        # Get previous year income
                        if hasattr(prev_point, 'gross_income_gbp_equiv') and prev_point.gross_income_gbp_equiv > 0:
                            prev_income = prev_point.gross_income_gbp_equiv
                        elif hasattr(prev_point, 'gross_salary_gbp') and prev_point.gross_salary_gbp > 0:
                            prev_income = prev_point.gross_salary_gbp
                        elif hasattr(prev_point, 'gross_salary_usd') and prev_point.gross_salary_usd > 0:
                            prev_income = prev_point.gross_salary_usd / 1.26
                        elif hasattr(prev_point, 'total_gross_usd') and prev_point.total_gross_usd > 0:
                            prev_income = prev_point.total_gross_usd / 1.26
                        
                        # Get current year income
                        if hasattr(curr_point, 'gross_income_gbp_equiv') and curr_point.gross_income_gbp_equiv > 0:
                            curr_income = curr_point.gross_income_gbp_equiv
                        elif hasattr(curr_point, 'gross_salary_gbp') and curr_point.gross_salary_gbp > 0:
                            curr_income = curr_point.gross_salary_gbp
                        elif hasattr(curr_point, 'gross_salary_usd') and curr_point.gross_salary_usd > 0:
                            curr_income = curr_point.gross_salary_usd / 1.26
                        elif hasattr(curr_point, 'total_gross_usd') and curr_point.total_gross_usd > 0:
                            curr_income = curr_point.total_gross_usd / 1.26
                        
                        # Calculate YoY growth if we have valid data
                        if prev_income > 0 and curr_income > 0:
                            yoy_growth = ((curr_income - prev_income) / prev_income) * 100
                            yoy_growths.append(yoy_growth)
                    
                    # Calculate average YoY growth for this scenario
                    if yoy_growths:
                        scenario_avg_yoy = sum(yoy_growths) / len(yoy_growths)
                        total_yoy_growth += scenario_avg_yoy
                        scenarios_with_growth += 1
        
        avg_yoy_growth = total_yoy_growth / max(1, scenarios_with_growth)
        
        return {
            'max_net_worth': max_net_worth,
            'avg_yoy_growth': avg_yoy_growth,
            'scenarios_count': len(scenarios_to_analyze)
        }
    
    except Exception as e:
        st.error(f"Error calculating KPIs: {str(e)}")
        return {
            'max_net_worth': 0,
            'avg_yoy_growth': 0,
            'scenarios_count': 0
        }


def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Validate session state
        if not validate_session_state():
            st.error(ERROR_MESSAGES['session_state_missing'])
            return
        
        # Sidebar
        with st.sidebar:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 15px; color: white; text-align: center; 
                        margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h2 style="margin: 0; font-size: 1.5rem; font-weight: 700;">📊 Financial Planning Dashboard</h2>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;">
                    Comprehensive financial scenario analysis and planning
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Scenario selector
            if render_scenario_selector:
                render_scenario_selector()
            else:
                st.warning("Scenario selector component not available.")
            
            st.markdown("---")
            
            # Year range selector
            st.markdown("### 📅 Year Range")
            year_range = st.slider(
                "Select year range for analysis:",
                min_value=1,
                max_value=20,
                value=st.session_state.year_range,
                key="year_range_selector"
            )
            st.session_state.year_range = year_range

        
        # Load data if not already loaded
        if not st.session_state.data_loaded or not st.session_state.all_scenarios:
            with st.spinner("Loading financial scenario data..."):
                try:
                    st.session_state.all_scenarios = load_all_scenarios()
                    st.session_state.data_loaded = True
                    st.success(SUCCESS_MESSAGES['data_loaded'])
                except Exception as e:
                    handle_data_loading_error(e, "main data loading")
                    return
        
        # Validate user inputs
        if not validate_user_inputs(st.session_state.selected_scenarios, st.session_state.year_range):
            st.info("Please select scenarios and year range in the sidebar to begin analysis.")
            return
        
        # Filter scenarios
        try:
            scenarios_to_analyze = filter_scenarios(
                st.session_state.all_scenarios,
                st.session_state.selected_scenarios,
                st.session_state.year_range
            )
        except Exception as e:
            st.error(f"Error filtering scenarios: {str(e)}")
            return
        
        # Calculate and display KPIs
        kpis = calculate_kpis(scenarios_to_analyze)
        
        st.markdown("### 📈 Key Performance Indicators")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{format_currency(kpis['max_net_worth'])}</div>
                <div class="kpi-label">MAX NET WORTH</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{kpis['avg_yoy_growth']:.1f}%</div>
                <div class="kpi-label">AVG YOY INCOME GROWTH</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">{kpis['scenarios_count']}</div>
                <div class="kpi-label">SCENARIOS ANALYZED</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Analysis sections
        st.markdown("### 📊 Analysis Sections")
        
        # Create navigation buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📈 Time Series Analysis", use_container_width=True):
                st.session_state.current_page = "time_series"
        
        with col2:
            if st.button("💰 Income & Expense Breakdown", use_container_width=True):
                st.session_state.current_page = "income_expense"
        
        with col3:
            if st.button("📊 Performance Monitoring", use_container_width=True):
                st.session_state.current_page = "performance"
        
        # Route to appropriate page
        current_page = st.session_state.get('current_page', 'time_series')
        
        if current_page == "time_series" and render_time_series_page:
            render_time_series_page(scenarios_to_analyze)
        elif current_page == "income_expense" and render_income_expense_page:
            render_income_expense_page(scenarios_to_analyze)
        elif current_page == "performance" and render_performance_page:
            render_performance_page(scenarios_to_analyze)
        else:
            # Default to time series analysis
            if render_time_series_page:
                render_time_series_page(scenarios_to_analyze)
            else:
                st.error("Time series analysis page not available.")
    
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.info("Please refresh the page and try again.")


if __name__ == "__main__":
    main() 