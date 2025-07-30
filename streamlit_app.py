"""
Financial Planning Dashboard - Main Application
A comprehensive Streamlit application for financial scenario analysis and planning using unified models.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import importlib.util
import os
from pathlib import Path
import traceback
import sys

# Import utilities and constants
from utils.data import load_all_scenarios, filter_scenarios, filter_scenarios_by_type
from utils.validation import validate_session_state, validate_user_inputs, handle_data_loading_error
from utils.formatting import format_currency, format_percentage, format_scenario_name
from utils.css_loader import load_main_styles
from constants import DEFAULT_SCENARIOS, DEFAULT_YEAR_RANGE, ERROR_MESSAGES, SUCCESS_MESSAGES

# Import unified models
from models.unified_financial_data import UnifiedFinancialScenario




def import_page_module(page_name: str, function_name: str):
    """Dynamically import page functions."""
    try:
        spec = importlib.util.spec_from_file_location(
            page_name, 
            os.path.join(os.path.dirname(__file__), 'pages', page_name)
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        function = getattr(module, function_name)
        return function
    except Exception as e:
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
        
        # Initialize quick filters if not present
        if 'quick_filters' not in st.session_state:
            st.session_state.quick_filters = {
                'uk_only': False,
                'international_only': False,
                'tax_free_only': False,
                'delayed_relocation_only': False
            }
    except Exception as e:
        pass


def calculate_kpis(scenarios_to_analyze: Dict[str, UnifiedFinancialScenario]) -> Dict[str, Any]:
    """
    Calculate Key Performance Indicators for the dashboard using unified models.
    
    Args:
        scenarios_to_analyze: Dictionary of scenarios to analyze with unified structure
        
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
                # Use unified methods for calculations
                final_net_worth = scenario.get_final_net_worth_gbp()
                max_net_worth = max(max_net_worth, final_net_worth)
                
                # Calculate year-over-year growth using unified structure
                if len(scenario.data_points) >= 2:
                    initial_net_worth = scenario.data_points[0].net_worth_gbp
                    final_net_worth = scenario.data_points[-1].net_worth_gbp
                    
                    if initial_net_worth > 0:
                        yoy_growth = ((final_net_worth - initial_net_worth) / initial_net_worth) * 100
                        total_yoy_growth += yoy_growth
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


def render_dashboard_header():
    """Render the main dashboard header."""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 Financial Planning Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Comprehensive financial scenario analysis with unified data models</p>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_metrics(scenarios_to_analyze: Dict[str, UnifiedFinancialScenario]):
    """Render KPI metrics using unified models."""
    try:
        kpis = calculate_kpis(scenarios_to_analyze)
        
        st.markdown("### 📈 Key Performance Indicators")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Max Net Worth",
                value=format_currency(kpis['max_net_worth']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Avg YoY Growth",
                value=format_percentage(kpis['avg_yoy_growth']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Scenarios Analyzed",
                value=str(kpis['scenarios_count']),
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering KPI metrics: {str(e)}")


def render_scenario_summary(scenarios_to_analyze: Dict[str, UnifiedFinancialScenario]):
    """Render scenario summary using unified models."""
    try:
        if not scenarios_to_analyze:
            st.warning("No scenarios selected for analysis.")
            return
        
        st.markdown("### 📋 Scenario Summary")
        
        summary_data = []
        for scenario_name, scenario in scenarios_to_analyze.items():
            if scenario.data_points:
                # Use unified methods for calculations
                final_net_worth = scenario.get_final_net_worth_gbp()
                avg_savings = scenario.get_average_annual_savings_gbp()
                total_tax = scenario.get_total_tax_burden_gbp()
                growth_rate = scenario.get_net_worth_growth_rate()
                
                summary_data.append({
                    'Scenario': scenario_name,
                    'Final Net Worth': format_currency(final_net_worth),
                    'Avg Annual Savings': format_currency(avg_savings),
                    'Total Tax Burden': format_currency(total_tax),
                    'Growth Rate': f"{growth_rate:.1f}%"
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No scenario data available for summary.")
    
    except Exception as e:
        st.error(f"Error rendering scenario summary: {str(e)}")


def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Render header
        render_dashboard_header()
        
        # Sidebar
        with st.sidebar:
            st.markdown("### 🎛️ Controls")
            
            # Scenario selector
            if render_scenario_selector:
                render_scenario_selector()
            else:
                st.warning("Scenario selector component not available.")
            
            # Year range selector
            st.markdown("### 📅 Year Range")
            year_range = st.slider(
                "Select year range",
                min_value=2025,
                max_value=2034,
                value=st.session_state.year_range,
                key="year_range_slider"
            )
            st.session_state.year_range = year_range
            
            # Data loading controls
            st.markdown("### 🔄 Data Management")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Reload Data", use_container_width=True):
                    st.session_state.data_loaded = False
                    st.rerun()
            
            with col2:
                if st.button("🧹 Clear Cache", use_container_width=True):
                    from utils.data import clear_cache
                    clear_cache()
                    st.session_state.data_loaded = False
                    st.success("Cache cleared!")
        
        # Main content
        # Fallback: if no scenarios selected, try to get all available scenarios
        if not st.session_state.selected_scenarios:
            try:
                from utils.data import get_scenario_metadata
                metadata = get_scenario_metadata()
                all_available = (metadata['uk_scenarios'] + 
                               metadata['international_scenarios'] + 
                               metadata['delayed_relocation_scenarios'])
                if all_available:
                    st.session_state.selected_scenarios = all_available
                    st.success(f"✅ All {len(all_available)} scenarios selected automatically!")
                    st.info("💡 You can customize your selection in the sidebar.")
                else:
                    st.warning("⚠️ No scenarios available. Please check the data loading.")
                    return
            except Exception as e:
                st.warning("⚠️ Please select scenarios in the sidebar to view the dashboard.")
                st.info("💡 Use the scenario selection controls in the sidebar to choose which scenarios to analyze.")
                return
        
        # Load scenario data
        if not st.session_state.data_loaded:
            with st.spinner("Loading scenario data..."):
                try:
                    all_scenarios = load_all_scenarios()
                    st.session_state.all_scenarios = all_scenarios
                    st.session_state.data_loaded = True
                    st.success("✅ Data loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to load data: {str(e)}")
                    return
        
        # Filter scenarios
        scenarios_to_analyze = filter_scenarios(
            st.session_state.all_scenarios,
            st.session_state.selected_scenarios,
            tuple(st.session_state.year_range)
        )
        
        # Validate scenarios
        if not validate_session_state():
            st.error("Invalid session state detected. Please refresh the page.")
            return
        
        # Render KPI metrics
        render_kpi_metrics(scenarios_to_analyze)
        
        # Render scenario summary
        render_scenario_summary(scenarios_to_analyze)
        
        # Page navigation
        st.markdown("---")
        st.subheader("📄 Analysis Pages")
        
        tab1, tab2, tab3 = st.tabs([
            "📈 Time Series Analysis",
            "💰 Income & Expense Breakdown",
            "⚡ Performance Monitoring"
        ])
        
        with tab1:
            if render_time_series_page:
                render_time_series_page(scenarios_to_analyze)
            else:
                st.error("Time series analysis page not available.")
        
        with tab2:
            if render_income_expense_page:
                render_income_expense_page(scenarios_to_analyze)
            else:
                st.error("Income & expense breakdown page not available.")
        
        with tab3:
            if render_performance_page:
                render_performance_page(scenarios_to_analyze)
            else:
                st.error("Performance monitoring page not available.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page or clearing the cache.")


if __name__ == "__main__":
    main() 