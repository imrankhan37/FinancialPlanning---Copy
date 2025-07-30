"""
Time Series Analysis Page
Comprehensive analysis of net worth, income, and savings trajectories over time using unified models.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
import uuid

# Import utilities
from utils.validation import validate_scenario_data, safe_divide, validate_dataframe
from utils.formatting import format_currency, format_percentage, format_number, extract_numeric_from_currency
from utils.css_loader import load_component_styles
from constants import ERROR_MESSAGES, SUCCESS_MESSAGES

# Import unified models
from models.unified_financial_data import UnifiedFinancialScenario


def render_time_series_page(scenarios_to_analyze: Optional[Dict[str, UnifiedFinancialScenario]] = None) -> None:
    """
    Render the time series analysis page using unified models.
    
    Args:
        scenarios_to_analyze: Dictionary of scenarios to analyze with unified structure (optional)
    """
    try:
        # Initialize session state if needed
        if 'selected_scenarios' not in st.session_state:
            st.session_state.selected_scenarios = []
        if 'year_range' not in st.session_state:
            st.session_state.year_range = [1, 10]
        
        # Use provided scenarios or get from session state
        if scenarios_to_analyze is None:
            from utils.data import load_all_scenarios, filter_scenarios
            all_scenarios = load_all_scenarios()
            scenarios_to_analyze = filter_scenarios(
                all_scenarios,
                st.session_state.selected_scenarios,
                st.session_state.year_range
            )
        
        # Validate scenario data
        if not validate_scenario_data(scenarios_to_analyze):
            st.error("Invalid scenario data provided.")
            return
        
        st.markdown("## 📈 Time Series Analysis")
        st.markdown("Comprehensive analysis of financial metrics over time across all scenarios.")
        
        # Render Performance Metrics first (moved to top)
        render_performance_metrics(scenarios_to_analyze)
        
        # Render different analysis sections
        render_net_worth_analysis(scenarios_to_analyze)
        render_income_analysis(scenarios_to_analyze)
        render_savings_analysis(scenarios_to_analyze)
        
    except Exception as e:
        st.error(f"Error rendering time series page: {str(e)}")
        st.info("Please refresh the page and try again.")


def render_net_worth_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render net worth trajectory analysis using unified models."""
    try:
        st.markdown("### 💰 Net Worth Trajectory")
        st.markdown("Track net worth growth over time across all scenarios.")
        
        # Prepare data for plotting using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    # Use unified net worth property
                    net_worth = point.net_worth_gbp
                    
                    plot_data.append({
                        'Year': i,
                        'Net Worth': net_worth,
                        'Scenario': scenario_name
                    })
        
        if plot_data:
            df = pd.DataFrame(plot_data)
            
            # Create interactive plot
            fig = px.line(
                df, 
                x='Year', 
                y='Net Worth', 
                color='Scenario',
                title='Net Worth Trajectory Over Time',
                labels={'Net Worth': 'Net Worth (£)', 'Year': 'Year'},
                template='plotly_white'
            )
            
            fig.update_layout(
                height=500,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"net_worth_chart_{uuid.uuid4()}")
            
            # Summary statistics
            st.markdown("#### 📊 Net Worth Summary")
            summary_stats = df.groupby('Scenario')['Net Worth'].agg(['max', 'min', 'mean']).round(0)
            summary_stats.columns = ['Max Net Worth', 'Min Net Worth', 'Avg Net Worth']
            summary_stats = summary_stats.map(lambda x: format_currency(x))
            st.dataframe(summary_stats, use_container_width=True)
        else:
            st.warning("No net worth data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering net worth analysis: {str(e)}")


def render_income_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render income trajectory analysis using unified models."""
    try:
        st.markdown("### 💵 Income Trajectory")
        st.markdown("Track income growth over time across all scenarios.")
        
        # Prepare data for plotting using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    # Use unified gross income property
                    income = point.gross_income_gbp
                    
                    plot_data.append({
                        'Year': i,
                        'Income': income,
                        'Scenario': scenario_name
                    })
        
        if plot_data:
            df = pd.DataFrame(plot_data)
            
            # Create interactive plot
            fig = px.line(
                df, 
                x='Year', 
                y='Income', 
                color='Scenario',
                title='Income Trajectory Over Time',
                labels={'Income': 'Income (£)', 'Year': 'Year'},
                template='plotly_white'
            )
            
            fig.update_layout(
                height=500,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"income_chart_{uuid.uuid4()}")
            
            # Summary statistics
            st.markdown("#### 📊 Income Summary")
            summary_stats = df.groupby('Scenario')['Income'].agg(['max', 'min', 'mean']).round(0)
            summary_stats.columns = ['Max Income', 'Min Income', 'Avg Income']
            summary_stats = summary_stats.map(lambda x: format_currency(x))
            st.dataframe(summary_stats, use_container_width=True)
        else:
            st.warning("No income data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering income analysis: {str(e)}")


def render_savings_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render savings trajectory analysis using unified models."""
    try:
        st.markdown("### 💎 Savings Trajectory")
        st.markdown("Track savings growth over time across all scenarios.")
        
        # Prepare data for plotting using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    # Use unified annual savings property
                    savings = point.annual_savings_gbp
                    
                    plot_data.append({
                        'Year': i,
                        'Savings': savings,
                        'Scenario': scenario_name
                    })
        
        if plot_data:
            df = pd.DataFrame(plot_data)
            
            # Create interactive plot
            fig = px.line(
                df, 
                x='Year', 
                y='Savings', 
                color='Scenario',
                title='Annual Savings Trajectory Over Time',
                labels={'Savings': 'Annual Savings (£)', 'Year': 'Year'},
                template='plotly_white'
            )
            
            fig.update_layout(
                height=500,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"savings_chart_{uuid.uuid4()}")
            
            # Summary statistics
            st.markdown("#### 📊 Savings Summary")
            summary_stats = df.groupby('Scenario')['Savings'].agg(['max', 'min', 'mean']).round(0)
            summary_stats.columns = ['Max Savings', 'Min Savings', 'Avg Savings']
            summary_stats = summary_stats.map(lambda x: format_currency(x))
            st.dataframe(summary_stats, use_container_width=True)
        else:
            st.warning("No savings data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering savings analysis: {str(e)}")


def render_performance_metrics(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render performance metrics using unified models."""
    try:
        st.markdown("### 📊 Performance Metrics")
        st.markdown("Key performance indicators across all selected scenarios.")
        
        if not scenarios:
            st.warning("No scenarios selected for analysis.")
            return
        
        # Calculate metrics using unified structure
        metrics_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                # Use unified methods for calculations
                final_net_worth = scenario.get_final_net_worth_gbp()
                avg_savings = scenario.get_average_annual_savings_gbp()
                total_tax = scenario.get_total_tax_burden_gbp()
                growth_rate = scenario.get_net_worth_growth_rate()
                
                metrics_data.append({
                    'Scenario': scenario_name,
                    'Final Net Worth': final_net_worth,
                    'Avg Annual Savings': avg_savings,
                    'Total Tax Burden': total_tax,
                    'Growth Rate (%)': growth_rate
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            
            # Format currency columns
            currency_columns = ['Final Net Worth', 'Avg Annual Savings', 'Total Tax Burden']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            # Format percentage column
            df['Growth Rate (%)'] = df['Growth Rate (%)'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No performance data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering performance metrics: {str(e)}")


def main() -> None:
    """Main function to render the time series analysis page."""
    render_time_series_page()


if __name__ == "__main__":
    main() 