"""
Time Series Analysis Page
Comprehensive analysis of net worth, income, and savings trajectories over time.
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


def render_time_series_page(scenarios_to_analyze: Optional[Dict[str, Any]] = None) -> None:
    """
    Render the time series analysis page.
    
    Args:
        scenarios_to_analyze: Dictionary of scenarios to analyze (optional)
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


def render_net_worth_analysis(scenarios: Dict[str, Any]) -> None:
    """Render net worth trajectory analysis."""
    try:
        st.markdown("### 💰 Net Worth Trajectory")
        st.markdown("Track net worth growth over time across all scenarios.")
        
        # Prepare data for plotting
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    net_worth = 0
                    if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0:
                        net_worth = point.net_worth_gbp_equiv
                    elif hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0:
                        net_worth = point.net_worth_gbp
                    elif hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0:
                        net_worth = point.net_worth_usd / 1.26
                    
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


def render_income_analysis(scenarios: Dict[str, Any]) -> None:
    """Render income trajectory analysis."""
    try:
        st.markdown("### 💵 Income Trajectory")
        st.markdown("Track income growth over time across all scenarios.")
        
        # Prepare data for plotting
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    income = 0
                    if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0:
                        income = point.gross_income_gbp_equiv
                    elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                        income = point.gross_salary_gbp
                    elif hasattr(point, 'gross_salary_usd') and point.gross_salary_usd > 0:
                        income = point.gross_salary_usd / 1.26
                    elif hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0:
                        income = point.total_gross_usd / 1.26
                    
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


def render_savings_analysis(scenarios: Dict[str, Any]) -> None:
    """Render savings trajectory analysis."""
    try:
        st.markdown("### 💎 Savings Trajectory")
        st.markdown("Track savings growth over time across all scenarios.")
        
        # Prepare data for plotting
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    savings = 0
                    if hasattr(point, 'annual_savings_gbp_equiv') and point.annual_savings_gbp_equiv > 0:
                        savings = point.annual_savings_gbp_equiv
                    elif hasattr(point, 'annual_savings_gbp') and point.annual_savings_gbp > 0:
                        savings = point.annual_savings_gbp
                    elif hasattr(point, 'annual_savings_usd') and point.annual_savings_usd > 0:
                        savings = point.annual_savings_usd / 1.26
                    
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
                title='Savings Trajectory Over Time',
                labels={'Savings': 'Savings (£)', 'Year': 'Year'},
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


def render_performance_metrics(scenarios_to_analyze):
    """Render performance metrics table with enhanced styling."""
    try:
        # Load component styles
        load_component_styles(["enhanced_tables", "metric_highlights"])
        
        if not scenarios_to_analyze:
            st.warning("No scenarios selected for analysis.")
            return
        
        st.markdown("### 📊 Performance Metrics")
        st.markdown("Comprehensive analysis of key performance indicators across all scenarios.")
        
       
        
        # Calculate comprehensive metrics
        metrics_data = []
        
        for scenario_name, scenario in scenarios_to_analyze.items():
            if scenario.data_points:
                # Calculate final net worth
                final_net_worth = 0
                initial_net_worth = 0
                total_savings = 0
                total_tax_paid = 0
                total_income = 0
                
                for i, point in enumerate(scenario.data_points):
                    # Net worth calculation
                    net_worth = 0
                    if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0:
                        net_worth = point.net_worth_gbp_equiv
                    elif hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0:
                        net_worth = point.net_worth_gbp
                    elif hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0:
                        net_worth = point.net_worth_usd / 1.26
                    
                    if i == 0:
                        initial_net_worth = net_worth
                    final_net_worth = net_worth
                    
                    # Savings calculation
                    savings = 0
                    if hasattr(point, 'annual_savings_gbp_equiv') and point.annual_savings_gbp_equiv > 0:
                        savings = point.annual_savings_gbp_equiv
                    elif hasattr(point, 'annual_savings_gbp') and point.annual_savings_gbp > 0:
                        savings = point.annual_savings_gbp
                    elif hasattr(point, 'annual_savings_usd') and point.annual_savings_usd > 0:
                        savings = point.annual_savings_usd / 1.26
                    total_savings += savings
                    
                    # Tax calculation
                    tax = 0
                    if hasattr(point, 'total_tax_gbp_equiv') and point.total_tax_gbp_equiv > 0:
                        tax = point.total_tax_gbp_equiv
                    elif hasattr(point, 'total_tax_gbp') and point.total_tax_gbp > 0:
                        tax = point.total_tax_gbp
                    elif hasattr(point, 'total_tax_usd') and point.total_tax_usd > 0:
                        tax = point.total_tax_usd / 1.26
                    total_tax_paid += tax
                    
                    # Income calculation
                    income = 0
                    if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0:
                        income = point.gross_income_gbp_equiv
                    elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                        income = point.gross_salary_gbp
                    elif hasattr(point, 'gross_salary_usd') and point.gross_salary_usd > 0:
                        income = point.gross_salary_usd / 1.26
                    elif hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0:
                        income = point.total_gross_usd / 1.26
                    total_income += income
                
                # Calculate derived metrics
                net_worth_growth = safe_divide((final_net_worth - initial_net_worth), initial_net_worth) * 100
                avg_annual_savings = safe_divide(total_savings, len(scenario.data_points))
                savings_rate = safe_divide(total_savings, total_income) * 100
                avg_annual_income = safe_divide(total_income, len(scenario.data_points))
                
                metrics_data.append({
                    'Scenario': scenario_name,
                    'Final Net Worth': format_currency(final_net_worth),
                    'Net Worth Growth': format_percentage(net_worth_growth),
                    'Avg Annual Savings': format_currency(avg_annual_savings),
                    'Savings Rate': format_percentage(savings_rate),
                    'Total Savings': format_currency(total_savings),
                    'Total Tax Paid': format_currency(total_tax_paid),
                    'Avg Annual Income': format_currency(avg_annual_income)
                })
        
        if metrics_data:
            # Enhanced table presentation with pandas Styler
            
            # Create clean dataframe for styling
            df = pd.DataFrame(metrics_data)
            
            # Convert currency and percentage strings to numeric for styling
            df['Final Net Worth Numeric'] = df['Final Net Worth'].apply(extract_numeric_from_currency)
            df['Net Worth Growth Numeric'] = df['Net Worth Growth'].str.replace('%', '').astype(float)
            df['Avg Annual Savings Numeric'] = df['Avg Annual Savings'].apply(extract_numeric_from_currency)
            df['Savings Rate Numeric'] = df['Savings Rate'].str.replace('%', '').astype(float)
            
            # Apply pandas Styler with proper formatting - use raw numeric data for styling
            styled_df = df.style\
                .background_gradient(
                    subset=['Final Net Worth Numeric'],
                    cmap='RdYlGn',
                    vmin=df['Final Net Worth Numeric'].min(),
                    vmax=df['Final Net Worth Numeric'].max()
                )\
                .background_gradient(
                    subset=['Net Worth Growth Numeric'],
                    cmap='RdYlGn',
                    vmin=df['Net Worth Growth Numeric'].min(),
                    vmax=df['Net Worth Growth Numeric'].max()
                )\
                .background_gradient(
                    subset=['Avg Annual Savings Numeric'],
                    cmap='RdYlGn',
                    vmin=df['Avg Annual Savings Numeric'].min(),
                    vmax=df['Avg Annual Savings Numeric'].max()
                )\
                .background_gradient(
                    subset=['Savings Rate Numeric'],
                    cmap='RdYlGn',
                    vmin=df['Savings Rate Numeric'].min(),
                    vmax=df['Savings Rate Numeric'].max()
                )\
                .apply(lambda x: ['background-color: #e8f5e8' if i == df['Final Net Worth Numeric'].idxmax() else '' for i in range(len(x))], subset=['Final Net Worth Numeric'])\
                .apply(lambda x: ['background-color: #e8f5e8' if i == df['Net Worth Growth Numeric'].idxmax() else '' for i in range(len(x))], subset=['Net Worth Growth Numeric'])\
                .apply(lambda x: ['background-color: #e8f5e8' if i == df['Avg Annual Savings Numeric'].idxmax() else '' for i in range(len(x))], subset=['Avg Annual Savings Numeric'])\
                .apply(lambda x: ['background-color: #e8f5e8' if i == df['Savings Rate Numeric'].idxmax() else '' for i in range(len(x))], subset=['Savings Rate Numeric'])\
                .hide(axis='index')\
                .hide(axis='columns', subset=['Final Net Worth Numeric', 'Net Worth Growth Numeric', 'Avg Annual Savings Numeric', 'Savings Rate Numeric'])
            
            # Performance insights with enhanced styling
            best_net_worth = max(metrics_data, key=lambda x: extract_numeric_from_currency(x['Final Net Worth']))
            best_growth = max(metrics_data, key=lambda x: float(x['Net Worth Growth'].replace('%', '')))
            best_savings_rate = max(metrics_data, key=lambda x: float(x['Savings Rate'].replace('%', '')))
            
            st.markdown("### 🏆 Top Performers")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-highlight">
                    🏆 <strong>Highest Net Worth</strong><br>
                    <span style="font-size: 1.5rem; font-weight: bold;">{best_net_worth['Scenario']}</span><br>
                    <span style="font-size: 1.2rem;">{best_net_worth['Final Net Worth']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-highlight-blue">
                    📈 <strong>Best Growth Rate</strong><br>
                    <span style="font-size: 1.5rem; font-weight: bold;">{best_growth['Scenario']}</span><br>
                    <span style="font-size: 1.2rem;">{best_growth['Net Worth Growth']}</span>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-highlight-purple">
                    💰 <strong>Best Savings Rate</strong><br>
                    <span style="font-size: 1.5rem; font-weight: bold;">{best_savings_rate['Scenario']}</span><br>
                    <span style="font-size: 1.2rem;">{best_savings_rate['Savings Rate']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No performance metrics available for the selected scenarios.")

                  
        # Style the dataframe with custom CSS
        st.markdown('<div class="enhanced-table">', unsafe_allow_html=True)
        st.dataframe(
            styled_df, 
            use_container_width=True,
            column_config={
                "Scenario": st.column_config.TextColumn("Scenario", width="medium"),
                "Final Net Worth": st.column_config.TextColumn("Final Net Worth", width="medium"),
                "Net Worth Growth": st.column_config.TextColumn("Net Worth Growth", width="medium"),
                "Avg Annual Savings": st.column_config.TextColumn("Avg Annual Savings", width="medium"),
                "Total Savings": st.column_config.TextColumn("Total Savings", width="medium"),
                "Total Tax Paid": st.column_config.TextColumn("Total Tax Paid", width="medium"),
                "Avg Annual Income": st.column_config.TextColumn("Avg Annual Income", width="medium")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error rendering performance metrics: {str(e)}")


# Main page function
def main() -> None:
    """
    Main function for standalone execution of the time series analysis page.
    """
    try:
        render_time_series_page()
    except Exception as e:
        st.error(f"Error in time series analysis: {str(e)}")


if __name__ == "__main__":
    main() 