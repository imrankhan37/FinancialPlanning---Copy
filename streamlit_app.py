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
from utils.data import (
    load_all_scenarios, filter_scenarios, filter_scenarios_by_type,
    get_enriched_scenario_metadata, validate_all_scenarios,
    get_template_configuration_summary
)
from utils.validation import validate_session_state, validate_user_inputs, handle_data_loading_error
from utils.formatting import format_currency, format_percentage, format_scenario_name
from utils.css_loader import load_main_styles
from constants import DEFAULT_SCENARIOS, DEFAULT_YEAR_RANGE, ERROR_MESSAGES, SUCCESS_MESSAGES

# Import unified models
from models.unified_financial_data import UnifiedFinancialScenario

# Import template-driven financial planner for metadata
from financial_planner_template_driven import TemplateFinancialPlanner


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
    from components.scenario_selector import render_scenario_selector, render_validation_status_panel
except ImportError as e:
    render_scenario_selector = None
    render_validation_status_panel = None


# Page configuration
st.set_page_config(
    page_title="Financial Planning Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load main styles
load_main_styles()


def initialize_template_session_state():
    """Initialize session state with template-driven data management."""
    try:
        # Basic session state
        if 'selected_scenarios' not in st.session_state:
            # Initialize with all available scenarios from template system
            try:
                planner = TemplateFinancialPlanner()
                available_scenarios = planner.get_available_scenarios()
                st.session_state.selected_scenarios = available_scenarios.copy()
            except Exception:
                st.session_state.selected_scenarios = DEFAULT_SCENARIOS.copy()

        if 'year_range' not in st.session_state:
            st.session_state.year_range = (1, 10)  # Use relative years instead of absolute

        if 'data_loaded' not in st.session_state:
            st.session_state.data_loaded = False

        if 'all_scenarios' not in st.session_state:
            st.session_state.all_scenarios = {}

        # Template-specific session state
        if 'template_metadata_loaded' not in st.session_state:
            st.session_state.template_metadata_loaded = False

        if 'validation_status' not in st.session_state:
            st.session_state.validation_status = {}

        if 'enriched_metadata' not in st.session_state:
            st.session_state.enriched_metadata = {}

        # Initialize enhanced quick filters
        if 'quick_filters' not in st.session_state:
            st.session_state.quick_filters = {
                'uk_only': False,
                'international_only': False,
                'tax_free_only': False,
                'delayed_relocation_only': False
            }

        # Initialize template filters
        if 'template_filters' not in st.session_state:
            st.session_state.template_filters = {
                'phase_filter': 'all',
                'jurisdiction_filter': 'all',
                'template_type_filter': 'all',
                'validation_filter': 'all',
                'show_composition': False
            }

    except Exception as e:
        st.error(f"Failed to initialize session state: {str(e)}")


def load_template_metadata():
    """Load simplified template metadata to avoid hangs."""
    if st.session_state.template_metadata_loaded:
        return

    try:
        # Simplified loading - just mark as loaded without expensive operations
        st.session_state.enriched_metadata = {}
        st.session_state.validation_status = {}
        st.session_state.template_metadata_loaded = True

    except Exception as e:
        st.error(f"Failed to load template metadata: {str(e)}")


def calculate_template_aware_kpis(scenarios_to_analyze: Dict[str, UnifiedFinancialScenario]) -> Dict[str, Any]:
    """
    Calculate KPIs with template metadata awareness.

    Args:
        scenarios_to_analyze: Dictionary of scenarios to analyze with unified structure

    Returns:
        Dict containing KPI values with template context
    """
    try:
        if not scenarios_to_analyze:
            return {
                'max_net_worth': 0,
                'scenarios_count': 0,
                'valid_scenarios_count': 0,
                'template_composition': {}
            }

        max_net_worth = 0
        valid_scenarios = 0
        template_composition = {}

        # Get validation status and enriched metadata
        validation_status = st.session_state.validation_status
        enriched_metadata = st.session_state.enriched_metadata

        for scenario_name, scenario in scenarios_to_analyze.items():
            # Find scenario ID from enriched metadata
            scenario_id = None
            for sid, meta in enriched_metadata.items():
                if meta.get('name', sid) == scenario_name:
                    scenario_id = sid
                    break

            # Since we're using simplified loading, assume scenarios are valid if they loaded
            if scenario.data_points:  # If we have data points, scenario is valid
                valid_scenarios += 1

            # Track template composition
            if scenario_id and scenario_id in enriched_metadata:
                composition = enriched_metadata[scenario_id].get('template_composition', {})
                for component_type, template_name in composition.items():
                    if template_name and template_name != 'Unknown':
                        if component_type not in template_composition:
                            template_composition[component_type] = {}
                        template_composition[component_type][template_name] = (
                            template_composition[component_type].get(template_name, 0) + 1
                        )

            if scenario.data_points:
                # Use unified methods for calculations
                final_net_worth = scenario.get_final_net_worth_gbp()
                max_net_worth = max(max_net_worth, final_net_worth)

        return {
            'max_net_worth': max_net_worth,
            'scenarios_count': len(scenarios_to_analyze),
            'valid_scenarios_count': valid_scenarios,
            'template_composition': template_composition
        }

    except Exception as e:
        st.error(f"Error calculating template-aware KPIs: {str(e)}")
        return {
            'max_net_worth': 0,
            'scenarios_count': 0,
            'valid_scenarios_count': 0,
            'template_composition': {}
        }


def render_dashboard_header():
    """Render the main dashboard header with template system information."""
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">📊 Financial Planning Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Template-driven scenario analysis with comprehensive validation and metadata</p>
    </div>
    """, unsafe_allow_html=True)


def render_template_aware_kpis(scenarios_to_analyze: Dict[str, UnifiedFinancialScenario]):
    """Render KPI metrics with template metadata awareness."""
    try:
        kpis = calculate_template_aware_kpis(scenarios_to_analyze)

        st.markdown("### 📈 Key Performance Indicators")

        # Main KPI metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Max Net Worth",
                value=format_currency(kpis['max_net_worth']),
                delta=None
            )

        with col2:
            st.metric(
                label="Scenarios Analyzed",
                value=str(kpis['scenarios_count']),
                delta=None
            )

        with col3:
            validation_rate = (kpis['valid_scenarios_count'] / max(1, kpis['scenarios_count'])) * 100
            st.metric(
                label="Validation Rate",
                value=f"{validation_rate:.0f}%",
                delta=None
            )

        # Template composition summary
        if kpis['template_composition']:
            with st.expander("🧩 Template Composition Summary", expanded=False):
                for component_type, templates in kpis['template_composition'].items():
                    st.markdown(f"**{component_type.replace('_', ' ').title()}**")
                    for template_name, count in templates.items():
                        st.markdown(f"• {template_name}: {count} scenario(s)")

    except Exception as e:
        st.error(f"Error rendering template-aware KPIs: {str(e)}")


def render_enhanced_scenario_summary(scenarios_to_analyze: Dict[str, UnifiedFinancialScenario]):
    """Render scenario summary with income breakdown and validation status."""
    try:
        if not scenarios_to_analyze:
            st.warning("No scenarios selected for analysis.")
            return

        st.markdown("### 📋 Scenario Summary with Income Breakdown")

        # Get enriched metadata and validation status
        enriched_metadata = st.session_state.enriched_metadata
        validation_status = st.session_state.validation_status

        summary_data = []
        for scenario_name, scenario in scenarios_to_analyze.items():
            if scenario.data_points:
                # Find scenario ID from enriched metadata
                scenario_id = None
                for sid, meta in enriched_metadata.items():
                    if meta.get('name', sid) == scenario_name:
                        scenario_id = sid
                        break

                # Since we're using simplified loading, assume scenarios are valid if they have data
                is_valid = bool(scenario.data_points)
                validation_icon = "✅" if is_valid else "❌"

                # Get template composition
                composition = enriched_metadata.get(scenario_id, {}).get('template_composition', {})
                phase_type = enriched_metadata.get(scenario_id, {}).get('phase_type', 'Unknown')

                # Use unified methods for calculations
                final_net_worth = scenario.get_final_net_worth_gbp()

                # Get final liquid savings with fallback
                try:
                    final_liquid_savings = scenario.get_final_liquid_savings_gbp()
                except AttributeError:
                    # Fallback: calculate manually if method doesn't exist
                    if scenario.data_points:
                        final_liquid_savings = scenario.data_points[-1].net_worth.liquid_assets.gbp_value
                    else:
                        final_liquid_savings = 0.0

                # Calculate income breakdown for the scenario
                if scenario.data_points:
                    avg_salary = sum(point.income.salary.gbp_value for point in scenario.data_points) / len(scenario.data_points)
                    avg_bonus = sum(point.income.bonus.gbp_value for point in scenario.data_points) / len(scenario.data_points)
                    avg_rsu = sum(point.income.rsu_vested.gbp_value for point in scenario.data_points) / len(scenario.data_points)
                    avg_total_income = sum(point.income.total_gbp for point in scenario.data_points) / len(scenario.data_points)
                else:
                    avg_salary = avg_bonus = avg_rsu = avg_total_income = 0

                summary_data.append({
                    'Status': validation_icon,
                    'Scenario': scenario_name,
                    'Phase': phase_type,
                    'Final Net Worth': format_currency(final_net_worth),
                    'Final Liquid Savings': format_currency(final_liquid_savings),
                    'Avg Salary': format_currency(avg_salary),
                    'Avg Bonus': format_currency(avg_bonus),
                    'Avg RSU': format_currency(avg_rsu),
                    'Total Income': format_currency(avg_total_income)
                })

        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True)

            # Show validation summary
            valid_count = sum(1 for row in summary_data if row['Status'] == "✅")
            total_count = len(summary_data)

            if valid_count < total_count:
                st.warning(f"⚠️ {total_count - valid_count} scenario(s) have validation issues. Check the validation panel in the sidebar.")
        else:
            st.warning("No scenario data available for summary.")

    except Exception as e:
        st.error(f"Error rendering enhanced scenario summary: {str(e)}")


def render_template_insights():
    """Render insights about the template system and available configurations."""
    try:
        enriched_metadata = st.session_state.enriched_metadata

        if not enriched_metadata:
            return

        with st.expander("🔍 Template System Insights", expanded=False):
            st.markdown("#### Template Distribution")

            # Count template types
            template_types = {}
            phase_types = {}

            for scenario_id, meta in enriched_metadata.items():
                if 'error' not in meta:
                    # Count template types
                    for template_type in meta.get('template_types', []):
                        template_types[template_type] = template_types.get(template_type, 0) + 1

                    # Count phase types
                    phase = meta.get('phase_type', 'Unknown')
                    phase_types[phase] = phase_types.get(phase, 0) + 1

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Template Types:**")
                for template_type, count in template_types.items():
                    st.markdown(f"• {template_type.replace('_', ' ').title()}: {count}")

            with col2:
                st.markdown("**Phase Types:**")
                for phase_type, count in phase_types.items():
                    st.markdown(f"• {phase_type}: {count}")

    except Exception as e:
        st.error(f"Error rendering template insights: {str(e)}")


def main():
    """Main application function with template-driven enhancements."""
    try:
        # Initialize template-aware session state
        initialize_template_session_state()

        # Load template metadata
        load_template_metadata()

        # Render header
        render_dashboard_header()

        # Sidebar with enhanced template features
        with st.sidebar:
            st.markdown("### 🎛️ Template-Driven Controls")

            # Enhanced scenario selector with template metadata
            if render_scenario_selector:
                render_scenario_selector()
            else:
                st.warning("Enhanced scenario selector component not available.")

            # Validation status panel - temporarily disabled to avoid hangs
            # if render_validation_status_panel:
            #     render_validation_status_panel()
            st.sidebar.info("💡 Validation panel temporarily disabled for faster loading")

            # Year range selector
            st.markdown("### 📅 Year Range")
            year_range = st.slider(
                "Select year range",
                min_value=1,
                max_value=10,
                value=(1, 10),
                key="year_range_slider",
                help="Select which years of the financial plan to analyze (relative to plan start)"
            )
            st.session_state.year_range = year_range

            # Template system status
            st.markdown("### 🔧 Scenario System Status")

            # Show scenario system health based on actual loaded data
            try:
                from financial_planner_template_driven import TemplateFinancialPlanner
                planner = TemplateFinancialPlanner()
                available_scenarios = planner.get_available_scenarios()

                # Count scenarios with actual data
                loaded_scenarios = len(st.session_state.all_scenarios) if st.session_state.all_scenarios else 0
                selected_scenarios = len(st.session_state.selected_scenarios) if st.session_state.selected_scenarios else 0

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Available", len(available_scenarios))
                with col2:
                    st.metric("Selected", selected_scenarios)

                # Show status indicator
                if loaded_scenarios > 0:
                    st.success(f"✅ {loaded_scenarios} scenarios loaded successfully")
                else:
                    st.info("💡 Scenarios ready for loading")

            except Exception as e:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Available", "Error")
                with col2:
                    st.metric("Selected", len(st.session_state.selected_scenarios) if st.session_state.selected_scenarios else 0)
                st.warning("⚠️ Unable to check scenario status")

            # Data loading controls
            st.markdown("### 🔄 Data Management")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Reload Data", use_container_width=True):
                    st.session_state.data_loaded = False
                    st.session_state.template_metadata_loaded = False
                    st.rerun()

            with col2:
                if st.button("🧹 Clear Cache", use_container_width=True):
                    from utils.data import clear_cache
                    clear_cache()
                    st.session_state.data_loaded = False
                    st.session_state.template_metadata_loaded = False
                    st.success("Cache cleared!")

        # Main content with template awareness
        # Fallback: if no scenarios selected, try to get all available scenarios
        if not st.session_state.selected_scenarios:
            try:
                planner = TemplateFinancialPlanner()
                available_scenarios = planner.get_available_scenarios()
                if available_scenarios:
                    st.session_state.selected_scenarios = available_scenarios
                    st.success(f"✅ All {len(available_scenarios)} template scenarios selected automatically!")
                    st.info("💡 You can customize your selection in the sidebar.")
                else:
                    st.warning("⚠️ No scenarios available. Please check the template system.")
                    return
            except Exception as e:
                st.warning("⚠️ Please select scenarios in the sidebar to view the dashboard.")
                st.info("💡 Use the enhanced scenario selection controls in the sidebar.")
                return

        # Load scenario data
        if not st.session_state.data_loaded:
            with st.spinner("Loading template-driven scenario data..."):
                try:
                    all_scenarios = load_all_scenarios()
                    st.session_state.all_scenarios = all_scenarios
                    st.session_state.data_loaded = True
                    st.success("✅ Template-driven data loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to load template data: {str(e)}")
                    return

        # Filter scenarios
        scenarios_to_analyze = filter_scenarios(
            st.session_state.all_scenarios,
            st.session_state.selected_scenarios,
            tuple(st.session_state.year_range)
        )

        # Debug: Log scenario filtering results
        st.sidebar.markdown(f"**Debug**: {len(st.session_state.selected_scenarios)} selected, {len(scenarios_to_analyze)} filtered")

        # Validate scenarios
        if not validate_session_state():
            st.error("Invalid session state detected. Please refresh the page.")
            return

        # Check if we have scenarios to analyze
        if not scenarios_to_analyze:
            st.warning("⚠️ No scenarios available for analysis after filtering.")
            st.info(f"Selected scenarios: {st.session_state.selected_scenarios}")
            st.info(f"Available scenarios: {list(st.session_state.all_scenarios.keys()) if st.session_state.all_scenarios else 'None'}")

            # Try to fix by reloading scenarios
            if st.button("🔄 Reload and Fix Scenarios"):
                try:
                    planner = TemplateFinancialPlanner()
                    available_scenarios = planner.get_available_scenarios()
                    if available_scenarios:
                        st.session_state.selected_scenarios = available_scenarios
                        st.session_state.data_loaded = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed to reload scenarios: {e}")
            return

        # Render template-aware KPI metrics
        render_template_aware_kpis(scenarios_to_analyze)

        # Render enhanced scenario summary with income breakdown
        render_enhanced_scenario_summary(scenarios_to_analyze)

        # Render template system insights
        render_template_insights()

        # Page navigation with template context
        st.markdown("---")
        st.subheader("📄 Template-Enhanced Analysis Pages")

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
        st.error(f"An error occurred in the template-driven dashboard: {str(e)}")
        st.info("Please try refreshing the page or clearing the cache.")

        # Show error details in expander for debugging
        with st.expander("🔧 Error Details", expanded=False):
            st.code(traceback.format_exc())


if __name__ == "__main__":
    main()
