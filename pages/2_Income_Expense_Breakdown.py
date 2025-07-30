"""
Income & Expense Breakdown Page
Hierarchical drill-down analysis of income and expense components using unified models.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import uuid
from plotly.subplots import make_subplots
import plotly.express as px
from utils.data import load_all_scenarios, filter_scenarios, calculate_key_metrics
from utils.charts import create_stacked_income_analysis, create_stacked_expense_analysis
from components.utils import format_currency, format_percentage, get_scenario_color
from utils.formatting import extract_numeric_from_currency, extract_numeric_from_percentage
from utils.css_loader import load_component_styles

# Import unified models
from models.unified_financial_data import UnifiedFinancialScenario


def render_income_expense_page(scenarios_to_analyze: Optional[Dict[str, UnifiedFinancialScenario]] = None) -> None:
    """Render the income and expense breakdown page using unified models."""
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">💰 Income & Expense Analysis</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Detailed breakdown of income sources, expense categories, and cash flow patterns with drill-down capabilities using unified models.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Use provided scenarios or fall back to session state
    if scenarios_to_analyze is None:
        # Initialize session state if not exists
        if 'selected_scenarios' not in st.session_state:
            st.session_state.selected_scenarios = []
        if 'year_range' not in st.session_state:
            st.session_state.year_range = [1, 10]
        
        # Check if scenarios are selected
        if not st.session_state.selected_scenarios:
            st.warning("⚠️ Please select scenarios in the sidebar to view the income & expense breakdown.")
            st.info("💡 Use the scenario selection controls in the sidebar to choose which scenarios to analyze.")
            return
        
        # Load scenario data
        with st.spinner("Loading scenario data..."):
            all_scenarios = load_all_scenarios()
            filtered_scenarios = filter_scenarios(
                all_scenarios,
                st.session_state.selected_scenarios,
                st.session_state.year_range
            )
        
        # Show selected scenarios info
        st.info(f"📊 Analyzing {len(st.session_state.selected_scenarios)} scenario(s): {', '.join(st.session_state.selected_scenarios)}")
    else:
        filtered_scenarios = scenarios_to_analyze
        st.info(f"📊 Analyzing {len(scenarios_to_analyze)} scenario(s): {', '.join(list(scenarios_to_analyze.keys()))}")
    
    # Main content with enhanced tabs
    st.markdown("---")
    st.subheader("📊 Analysis Sections")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Income Analysis",
        "💸 Expense Analysis",
        "📈 Cash Flow Analysis",
        "📋 Detailed Tables"
    ])
    
    with tab1:
        render_income_breakdown(filtered_scenarios)
    
    with tab2:
        render_expense_breakdown(filtered_scenarios)
    
    with tab3:
        render_cash_flow_analysis(filtered_scenarios)
    
    with tab4:
        render_detailed_tables(filtered_scenarios)


def render_income_breakdown(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render income breakdown analysis using unified models."""
    
    st.markdown("### 📊 Income Analysis")
    
    # Get scenario names
    scenario_names = list(scenarios.keys())
    
    if len(scenario_names) == 1:
        st.info(f"📊 Analyzing 1 scenario: {scenario_names[0]}")
        # Show single scenario analysis
        render_single_scenario_income_analysis(scenarios)
    elif len(scenario_names) == 2:
        st.info(f"📊 Analyzing 2 scenario(s): {', '.join(scenario_names)}")
        # Show comparison analysis
        render_comparison_income_analysis(scenarios)
    else:
        st.info(f"📊 Analyzing {len(scenario_names)} scenario(s): {', '.join(scenario_names)}")
        # Show multi-scenario analysis
        render_multi_scenario_income_analysis(scenarios)
    
    # Income metrics
    render_income_metrics(scenarios, "income")
    
    # Income table
    render_income_table(scenarios)


def render_income_metrics(scenarios: Dict[str, UnifiedFinancialScenario], component: str) -> None:
    """Render income metrics using unified models."""
    try:
        st.markdown("#### 📊 Income Metrics")
        
        # Calculate metrics using unified structure
        metrics_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                # Calculate income metrics using unified structure
                total_income = sum(point.gross_income_gbp for point in scenario.data_points)
                avg_income = total_income / len(scenario.data_points)
                max_income = max(point.gross_income_gbp for point in scenario.data_points)
                min_income = min(point.gross_income_gbp for point in scenario.data_points)
                
                # Calculate income components using unified structure
                total_salary = sum(point.income.salary.gbp_value for point in scenario.data_points)
                total_bonus = sum(point.income.bonus.gbp_value for point in scenario.data_points)
                total_rsu = sum(point.income.rsu_vested.gbp_value for point in scenario.data_points)
                
                metrics_data.append({
                    'Scenario': scenario_name,
                    'Total Income': total_income,
                    'Avg Annual Income': avg_income,
                    'Max Income': max_income,
                    'Min Income': min_income,
                    'Total Salary': total_salary,
                    'Total Bonus': total_bonus,
                    'Total RSU': total_rsu
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            
            # Format currency columns
            currency_columns = ['Total Income', 'Avg Annual Income', 'Max Income', 'Min Income', 
                              'Total Salary', 'Total Bonus', 'Total RSU']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No income metrics available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering income metrics: {str(e)}")


def render_income_table(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render income table using unified models."""
    try:
        st.markdown("#### 📋 Income Breakdown Table")
        
        # Prepare data for table using unified structure
        table_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for point in scenario.data_points:
                    table_data.append({
                        'Scenario': scenario_name,
                        'Year': point.year,
                        'Age': point.age,
                        'Salary': point.income.salary.gbp_value,
                        'Bonus': point.income.bonus.gbp_value,
                        'RSU Vested': point.income.rsu_vested.gbp_value,
                        'Other Income': point.income.other_income.gbp_value,
                        'Total Income': point.gross_income_gbp,
                        'Jurisdiction': point.jurisdiction.value,
                        'Phase': point.phase.value
                    })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Format currency columns
            currency_columns = ['Salary', 'Bonus', 'RSU Vested', 'Other Income', 'Total Income']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No income data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering income table: {str(e)}")


def render_expense_breakdown(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render expense breakdown analysis using unified models."""
    
    st.markdown("### 💸 Expense Analysis")
    
    # Get scenario names
    scenario_names = list(scenarios.keys())
    
    if len(scenario_names) == 1:
        st.info(f"📊 Analyzing 1 scenario: {scenario_names[0]}")
        # Show single scenario analysis
        render_single_scenario_expense_analysis(scenarios)
    elif len(scenario_names) == 2:
        st.info(f"📊 Analyzing 2 scenario(s): {', '.join(scenario_names)}")
        # Show comparison analysis
        render_comparison_expense_analysis(scenarios)
    else:
        st.info(f"📊 Analyzing {len(scenario_names)} scenario(s): {', '.join(scenario_names)}")
        # Show multi-scenario analysis
        render_multi_scenario_expense_analysis(scenarios)
    
    # Expense metrics
    render_expense_metrics(scenarios, "expense")
    
    # Expense table
    render_expense_table(scenarios)


def render_expense_metrics(scenarios: Dict[str, UnifiedFinancialScenario], component: str) -> None:
    """Render expense metrics using unified models."""
    try:
        st.markdown("#### 📊 Expense Metrics")
        
        # Calculate metrics using unified structure
        metrics_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                # Calculate expense metrics using unified structure
                total_expenses = sum(point.total_expenses_gbp for point in scenario.data_points)
                avg_expenses = total_expenses / len(scenario.data_points)
                max_expenses = max(point.total_expenses_gbp for point in scenario.data_points)
                min_expenses = min(point.total_expenses_gbp for point in scenario.data_points)
                
                # Calculate expense components using unified structure
                total_housing = sum(point.expenses.housing.gbp_value for point in scenario.data_points)
                total_living = sum(point.expenses.living.gbp_value for point in scenario.data_points)
                total_taxes = sum(point.expenses.taxes.gbp_value for point in scenario.data_points)
                total_investments = sum(point.expenses.investments.gbp_value for point in scenario.data_points)
                total_other = sum(point.expenses.other.gbp_value for point in scenario.data_points)
                
                metrics_data.append({
                    'Scenario': scenario_name,
                    'Total Expenses': total_expenses,
                    'Avg Annual Expenses': avg_expenses,
                    'Max Expenses': max_expenses,
                    'Min Expenses': min_expenses,
                    'Total Housing': total_housing,
                    'Total Living': total_living,
                    'Total Taxes': total_taxes,
                    'Total Investments': total_investments,
                    'Total Other': total_other
                })
        
        if metrics_data:
            df = pd.DataFrame(metrics_data)
            
            # Format currency columns
            currency_columns = ['Total Expenses', 'Avg Annual Expenses', 'Max Expenses', 'Min Expenses',
                              'Total Housing', 'Total Living', 'Total Taxes', 'Total Investments', 'Total Other']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No expense metrics available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering expense metrics: {str(e)}")


def render_expense_table(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render expense table using unified models."""
    try:
        st.markdown("#### 📋 Expense Breakdown Table")
        
        # Prepare data for table using unified structure
        table_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for point in scenario.data_points:
                    table_data.append({
                        'Scenario': scenario_name,
                        'Year': point.year,
                        'Age': point.age,
                        'Housing': point.expenses.housing.gbp_value,
                        'Living': point.expenses.living.gbp_value,
                        'Taxes': point.expenses.taxes.gbp_value,
                        'Investments': point.expenses.investments.gbp_value,
                        'Other': point.expenses.other.gbp_value,
                        'Total Expenses': point.total_expenses_gbp,
                        'Jurisdiction': point.jurisdiction.value,
                        'Phase': point.phase.value
                    })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Format currency columns
            currency_columns = ['Housing', 'Living', 'Taxes', 'Investments', 'Other', 'Total Expenses']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No expense data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering expense table: {str(e)}")


def render_cash_flow_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render cash flow analysis using unified models."""
    try:
        st.markdown("### 📈 Cash Flow Analysis")
        st.markdown("Analysis of income vs expenses and resulting cash flow patterns.")
        
        # Create cash flow chart
        fig = create_cash_flow_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Cash flow insights
        st.markdown("#### 💡 Cash Flow Insights")
        
        # Calculate cash flow metrics using unified structure
        cash_flow_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for point in scenario.data_points:
                    cash_flow = point.annual_savings_gbp  # Income - Expenses
                    cash_flow_data.append({
                        'Scenario': scenario_name,
                        'Year': point.year,
                        'Income': point.gross_income_gbp,
                        'Expenses': point.total_expenses_gbp,
                        'Cash Flow': cash_flow,
                        'Cash Flow %': (cash_flow / point.gross_income_gbp * 100) if point.gross_income_gbp > 0 else 0
                    })
        
        if cash_flow_data:
            df = pd.DataFrame(cash_flow_data)
            
            # Format currency columns
            currency_columns = ['Income', 'Expenses', 'Cash Flow']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            # Format percentage column
            df['Cash Flow %'] = df['Cash Flow %'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No cash flow data available for the selected scenarios.")
    
    except Exception as e:
        st.error(f"Error rendering cash flow analysis: {str(e)}")


def render_detailed_tables(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render detailed tables using unified models."""
    try:
        st.markdown("### 📋 Detailed Data Tables")
        
        # Create comparison tables
        income_comparison = create_income_comparison_table(scenarios)
        expense_comparison = create_expense_comparison_table(scenarios)
        
        # Display tables
        st.markdown("#### 💰 Income Comparison")
        st.dataframe(income_comparison, use_container_width=True)
        
        st.markdown("#### 💸 Expense Comparison")
        st.dataframe(expense_comparison, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering detailed tables: {str(e)}")


def create_cash_flow_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create cash flow chart using unified models."""
    try:
        # Prepare data using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    plot_data.append({
                        'Year': i,
                        'Income': point.gross_income_gbp,
                        'Expenses': point.total_expenses_gbp,
                        'Cash Flow': point.annual_savings_gbp,
                        'Scenario': scenario_name
                    })
        
        if not plot_data:
            return go.Figure()
        
        df = pd.DataFrame(plot_data)
        
        # Create subplot
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Income vs Expenses', 'Cash Flow'),
            vertical_spacing=0.1
        )
        
        # Add traces for each scenario
        for scenario_name in df['Scenario'].unique():
            scenario_data = df[df['Scenario'] == scenario_name]
            
            # Income vs Expenses
            fig.add_trace(
                go.Scatter(
                    x=scenario_data['Year'],
                    y=scenario_data['Income'],
                    mode='lines+markers',
                    name=f'{scenario_name} - Income',
                    line=dict(color=get_scenario_color(scenario_name)),
                    showlegend=True
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=scenario_data['Year'],
                    y=scenario_data['Expenses'],
                    mode='lines+markers',
                    name=f'{scenario_name} - Expenses',
                    line=dict(color=get_scenario_color(scenario_name), dash='dash'),
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Cash Flow
            fig.add_trace(
                go.Scatter(
                    x=scenario_data['Year'],
                    y=scenario_data['Cash Flow'],
                    mode='lines+markers',
                    name=f'{scenario_name} - Cash Flow',
                    line=dict(color=get_scenario_color(scenario_name)),
                    showlegend=False
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title='Cash Flow Analysis',
            height=600,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Update axes
        fig.update_xaxes(title_text="Year", row=1, col=1)
        fig.update_yaxes(title_text="Amount (£)", row=1, col=1)
        fig.update_xaxes(title_text="Year", row=2, col=1)
        fig.update_yaxes(title_text="Cash Flow (£)", row=2, col=1)
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating cash flow chart: {str(e)}")
        return go.Figure()


def create_income_comparison_table(scenarios: Dict[str, UnifiedFinancialScenario]) -> pd.DataFrame:
    """Create income comparison table using unified models."""
    try:
        # Prepare data using unified structure
        table_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for point in scenario.data_points:
                    table_data.append({
                        'Scenario': scenario_name,
                        'Year': point.year,
                        'Salary': point.income.salary.gbp_value,
                        'Bonus': point.income.bonus.gbp_value,
                        'RSU': point.income.rsu_vested.gbp_value,
                        'Other': point.income.other_income.gbp_value,
                        'Total': point.gross_income_gbp,
                        'Jurisdiction': point.jurisdiction.value
                    })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Format currency columns
            currency_columns = ['Salary', 'Bonus', 'RSU', 'Other', 'Total']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            return df
        else:
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error creating income comparison table: {str(e)}")
        return pd.DataFrame()


def create_expense_comparison_table(scenarios: Dict[str, UnifiedFinancialScenario]) -> pd.DataFrame:
    """Create expense comparison table using unified models."""
    try:
        # Prepare data using unified structure
        table_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for point in scenario.data_points:
                    table_data.append({
                        'Scenario': scenario_name,
                        'Year': point.year,
                        'Housing': point.expenses.housing.gbp_value,
                        'Living': point.expenses.living.gbp_value,
                        'Taxes': point.expenses.taxes.gbp_value,
                        'Investments': point.expenses.investments.gbp_value,
                        'Other': point.expenses.other.gbp_value,
                        'Total': point.total_expenses_gbp,
                        'Jurisdiction': point.jurisdiction.value
                    })
        
        if table_data:
            df = pd.DataFrame(table_data)
            
            # Format currency columns
            currency_columns = ['Housing', 'Living', 'Taxes', 'Investments', 'Other', 'Total']
            for col in currency_columns:
                df[col] = df[col].apply(format_currency)
            
            return df
        else:
            return pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error creating expense comparison table: {str(e)}")
        return pd.DataFrame()


def render_single_scenario_income_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render single scenario income analysis using unified models."""
    try:
        st.markdown("#### 📊 Single Scenario Income Analysis")
        
        # Get the single scenario
        scenario_name = list(scenarios.keys())[0]
        scenario = scenarios[scenario_name]
        
        if not scenario.data_points:
            st.warning("No data points available for analysis.")
            return
        
        # Create income chart
        fig = create_single_scenario_income_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Calculate and display metrics
        metrics = calculate_single_scenario_income_metrics(scenarios)
        
        st.markdown("#### 📈 Income Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Income",
                value=format_currency(metrics['total_income']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Avg Annual Income",
                value=format_currency(metrics['avg_income']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Income Growth Rate",
                value=f"{metrics['growth_rate']:.1f}%",
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering single scenario income analysis: {str(e)}")


def render_comparison_income_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render comparison income analysis using unified models."""
    try:
        st.markdown("#### 📊 Comparison Income Analysis")
        
        # Create comparison chart
        fig = create_income_comparison_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Calculate comparison metrics
        summary = calculate_multi_scenario_income_summary(scenarios)
        
        st.markdown("#### 📈 Comparison Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Best Total Income",
                value=format_currency(summary['best_total_income']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Best Avg Income",
                value=format_currency(summary['best_avg_income']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Best Growth Rate",
                value=f"{summary['best_growth_rate']:.1f}%",
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering comparison income analysis: {str(e)}")


def render_multi_scenario_income_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render multi-scenario income analysis using unified models."""
    try:
        st.markdown("#### 📊 Multi-Scenario Income Analysis")
        
        # Create multi-scenario chart
        fig = create_multi_scenario_income_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Calculate summary metrics
        summary = calculate_multi_scenario_income_summary(scenarios)
        
        st.markdown("#### 📈 Summary Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Scenarios",
                value=str(summary['total_scenarios']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Best Total Income",
                value=format_currency(summary['best_total_income']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Best Growth Rate",
                value=f"{summary['best_growth_rate']:.1f}%",
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering multi-scenario income analysis: {str(e)}")


def render_single_scenario_expense_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render single scenario expense analysis using unified models."""
    try:
        st.markdown("#### 📊 Single Scenario Expense Analysis")
        
        # Get the single scenario
        scenario_name = list(scenarios.keys())[0]
        scenario = scenarios[scenario_name]
        
        if not scenario.data_points:
            st.warning("No data points available for analysis.")
            return
        
        # Create expense chart
        fig = create_single_scenario_expense_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Calculate and display metrics
        metrics = calculate_single_scenario_expense_metrics(scenarios)
        
        st.markdown("#### 📈 Expense Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Expenses",
                value=format_currency(metrics['total_expenses']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Avg Annual Expenses",
                value=format_currency(metrics['avg_expenses']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Expense Growth Rate",
                value=f"{metrics['growth_rate']:.1f}%",
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering single scenario expense analysis: {str(e)}")


def render_comparison_expense_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render comparison expense analysis using unified models."""
    try:
        st.markdown("#### 📊 Comparison Expense Analysis")
        
        # Create comparison chart
        fig = create_expense_comparison_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Calculate comparison metrics
        summary = calculate_multi_scenario_expense_summary(scenarios)
        
        st.markdown("#### 📈 Comparison Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Lowest Total Expenses",
                value=format_currency(summary['lowest_total_expenses']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Lowest Avg Expenses",
                value=format_currency(summary['lowest_avg_expenses']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Best Expense Control",
                value=f"{summary['best_expense_control']:.1f}%",
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering comparison expense analysis: {str(e)}")


def render_multi_scenario_expense_analysis(scenarios: Dict[str, UnifiedFinancialScenario]) -> None:
    """Render multi-scenario expense analysis using unified models."""
    try:
        st.markdown("#### 📊 Multi-Scenario Expense Analysis")
        
        # Create multi-scenario chart
        fig = create_multi_scenario_expense_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        # Calculate summary metrics
        summary = calculate_multi_scenario_expense_summary(scenarios)
        
        st.markdown("#### 📈 Summary Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Scenarios",
                value=str(summary['total_scenarios']),
                delta=None
            )
        
        with col2:
            st.metric(
                label="Lowest Total Expenses",
                value=format_currency(summary['lowest_total_expenses']),
                delta=None
            )
        
        with col3:
            st.metric(
                label="Best Expense Control",
                value=f"{summary['best_expense_control']:.1f}%",
                delta=None
            )
    
    except Exception as e:
        st.error(f"Error rendering multi-scenario expense analysis: {str(e)}")


def create_single_scenario_income_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create single scenario income chart using unified models."""
    try:
        # Get the single scenario
        scenario_name = list(scenarios.keys())[0]
        scenario = scenarios[scenario_name]
        
        if not scenario.data_points:
            return go.Figure()
        
        # Prepare data using unified structure
        years = [point.year for point in scenario.data_points]
        salary = [point.income.salary.gbp_value for point in scenario.data_points]
        bonus = [point.income.bonus.gbp_value for point in scenario.data_points]
        rsu = [point.income.rsu_vested.gbp_value for point in scenario.data_points]
        other = [point.income.other_income.gbp_value for point in scenario.data_points]
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=years,
            y=salary,
            name='Salary',
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=bonus,
            name='Bonus',
            marker_color='#ff7f0e'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=rsu,
            name='RSU',
            marker_color='#2ca02c'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=other,
            name='Other',
            marker_color='#d62728'
        ))
        
        fig.update_layout(
            title=f'Income Breakdown - {scenario_name}',
            barmode='stack',
            height=500,
            showlegend=True
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating single scenario income chart: {str(e)}")
        return go.Figure()


def create_multi_scenario_income_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create multi-scenario income chart using unified models."""
    try:
        # Prepare data using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    plot_data.append({
                        'Year': i,
                        'Total Income': point.gross_income_gbp,
                        'Scenario': scenario_name
                    })
        
        if not plot_data:
            return go.Figure()
        
        df = pd.DataFrame(plot_data)
        
        # Create line chart
        fig = px.line(
            df,
            x='Year',
            y='Total Income',
            color='Scenario',
            title='Income Comparison Across Scenarios',
            labels={'Total Income': 'Total Income (£)', 'Year': 'Year'}
        )
        
        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating multi-scenario income chart: {str(e)}")
        return go.Figure()


def create_single_scenario_expense_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create single scenario expense chart using unified models."""
    try:
        # Get the single scenario
        scenario_name = list(scenarios.keys())[0]
        scenario = scenarios[scenario_name]
        
        if not scenario.data_points:
            return go.Figure()
        
        # Prepare data using unified structure
        years = [point.year for point in scenario.data_points]
        housing = [point.expenses.housing.gbp_value for point in scenario.data_points]
        living = [point.expenses.living.gbp_value for point in scenario.data_points]
        taxes = [point.expenses.taxes.gbp_value for point in scenario.data_points]
        investments = [point.expenses.investments.gbp_value for point in scenario.data_points]
        other = [point.expenses.other.gbp_value for point in scenario.data_points]
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=years,
            y=housing,
            name='Housing',
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=living,
            name='Living',
            marker_color='#ff7f0e'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=taxes,
            name='Taxes',
            marker_color='#2ca02c'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=investments,
            name='Investments',
            marker_color='#d62728'
        ))
        
        fig.add_trace(go.Bar(
            x=years,
            y=other,
            name='Other',
            marker_color='#9467bd'
        ))
        
        fig.update_layout(
            title=f'Expense Breakdown - {scenario_name}',
            barmode='stack',
            height=500,
            showlegend=True
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating single scenario expense chart: {str(e)}")
        return go.Figure()


def create_multi_scenario_expense_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create multi-scenario expense chart using unified models."""
    try:
        # Prepare data using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    plot_data.append({
                        'Year': i,
                        'Total Expenses': point.total_expenses_gbp,
                        'Scenario': scenario_name
                    })
        
        if not plot_data:
            return go.Figure()
        
        df = pd.DataFrame(plot_data)
        
        # Create line chart
        fig = px.line(
            df,
            x='Year',
            y='Total Expenses',
            color='Scenario',
            title='Expense Comparison Across Scenarios',
            labels={'Total Expenses': 'Total Expenses (£)', 'Year': 'Year'}
        )
        
        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating multi-scenario expense chart: {str(e)}")
        return go.Figure()


def calculate_single_scenario_income_metrics(scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, float]:
    """Calculate single scenario income metrics using unified models."""
    try:
        # Get the single scenario
        scenario_name = list(scenarios.keys())[0]
        scenario = scenarios[scenario_name]
        
        if not scenario.data_points:
            return {
                'total_income': 0.0,
                'avg_income': 0.0,
                'growth_rate': 0.0
            }
        
        # Calculate metrics using unified structure
        total_income = sum(point.gross_income_gbp for point in scenario.data_points)
        avg_income = total_income / len(scenario.data_points)
        
        # Calculate growth rate
        if len(scenario.data_points) >= 2:
            initial_income = scenario.data_points[0].gross_income_gbp
            final_income = scenario.data_points[-1].gross_income_gbp
            
            if initial_income > 0:
                growth_rate = ((final_income - initial_income) / initial_income) * 100
            else:
                growth_rate = 0.0
        else:
            growth_rate = 0.0
        
        return {
            'total_income': total_income,
            'avg_income': avg_income,
            'growth_rate': growth_rate
        }
    
    except Exception as e:
        st.error(f"Error calculating single scenario income metrics: {str(e)}")
        return {
            'total_income': 0.0,
            'avg_income': 0.0,
            'growth_rate': 0.0
        }


def calculate_single_scenario_expense_metrics(scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, float]:
    """Calculate single scenario expense metrics using unified models."""
    try:
        # Get the single scenario
        scenario_name = list(scenarios.keys())[0]
        scenario = scenarios[scenario_name]
        
        if not scenario.data_points:
            return {
                'total_expenses': 0.0,
                'avg_expenses': 0.0,
                'growth_rate': 0.0
            }
        
        # Calculate metrics using unified structure
        total_expenses = sum(point.total_expenses_gbp for point in scenario.data_points)
        avg_expenses = total_expenses / len(scenario.data_points)
        
        # Calculate growth rate
        if len(scenario.data_points) >= 2:
            initial_expenses = scenario.data_points[0].total_expenses_gbp
            final_expenses = scenario.data_points[-1].total_expenses_gbp
            
            if initial_expenses > 0:
                growth_rate = ((final_expenses - initial_expenses) / initial_expenses) * 100
            else:
                growth_rate = 0.0
        else:
            growth_rate = 0.0
        
        return {
            'total_expenses': total_expenses,
            'avg_expenses': avg_expenses,
            'growth_rate': growth_rate
        }
    
    except Exception as e:
        st.error(f"Error calculating single scenario expense metrics: {str(e)}")
        return {
            'total_expenses': 0.0,
            'avg_expenses': 0.0,
            'growth_rate': 0.0
        }


def calculate_multi_scenario_income_summary(scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, float]:
    """Calculate multi-scenario income summary using unified models."""
    try:
        if not scenarios:
            return {
                'total_scenarios': 0,
                'best_total_income': 0.0,
                'best_avg_income': 0.0,
                'best_growth_rate': 0.0
            }
        
        # Calculate metrics for each scenario
        scenario_metrics = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                total_income = sum(point.gross_income_gbp for point in scenario.data_points)
                avg_income = total_income / len(scenario.data_points)
                
                # Calculate growth rate
                if len(scenario.data_points) >= 2:
                    initial_income = scenario.data_points[0].gross_income_gbp
                    final_income = scenario.data_points[-1].gross_income_gbp
                    
                    if initial_income > 0:
                        growth_rate = ((final_income - initial_income) / initial_income) * 100
                    else:
                        growth_rate = 0.0
                else:
                    growth_rate = 0.0
                
                scenario_metrics.append({
                    'name': scenario_name,
                    'total_income': total_income,
                    'avg_income': avg_income,
                    'growth_rate': growth_rate
                })
        
        if not scenario_metrics:
            return {
                'total_scenarios': 0,
                'best_total_income': 0.0,
                'best_avg_income': 0.0,
                'best_growth_rate': 0.0
            }
        
        # Find best performers
        best_total_income = max(scenario_metrics, key=lambda x: x['total_income'])
        best_avg_income = max(scenario_metrics, key=lambda x: x['avg_income'])
        best_growth_rate = max(scenario_metrics, key=lambda x: x['growth_rate'])
        
        return {
            'total_scenarios': len(scenarios),
            'best_total_income': best_total_income['total_income'],
            'best_avg_income': best_avg_income['avg_income'],
            'best_growth_rate': best_growth_rate['growth_rate']
        }
    
    except Exception as e:
        st.error(f"Error calculating multi-scenario income summary: {str(e)}")
        return {
            'total_scenarios': 0,
            'best_total_income': 0.0,
            'best_avg_income': 0.0,
            'best_growth_rate': 0.0
        }


def calculate_multi_scenario_expense_summary(scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, float]:
    """Calculate multi-scenario expense summary using unified models."""
    try:
        if not scenarios:
            return {
                'total_scenarios': 0,
                'lowest_total_expenses': 0.0,
                'lowest_avg_expenses': 0.0,
                'best_expense_control': 0.0
            }
        
        # Calculate metrics for each scenario
        scenario_metrics = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                total_expenses = sum(point.total_expenses_gbp for point in scenario.data_points)
                avg_expenses = total_expenses / len(scenario.data_points)
                
                # Calculate expense control (lower is better)
                if len(scenario.data_points) >= 2:
                    initial_expenses = scenario.data_points[0].total_expenses_gbp
                    final_expenses = scenario.data_points[-1].total_expenses_gbp
                    
                    if initial_expenses > 0:
                        expense_control = ((initial_expenses - final_expenses) / initial_expenses) * 100
                    else:
                        expense_control = 0.0
                else:
                    expense_control = 0.0
                
                scenario_metrics.append({
                    'name': scenario_name,
                    'total_expenses': total_expenses,
                    'avg_expenses': avg_expenses,
                    'expense_control': expense_control
                })
        
        if not scenario_metrics:
            return {
                'total_scenarios': 0,
                'lowest_total_expenses': 0.0,
                'lowest_avg_expenses': 0.0,
                'best_expense_control': 0.0
            }
        
        # Find best performers (lowest expenses, best control)
        lowest_total_expenses = min(scenario_metrics, key=lambda x: x['total_expenses'])
        lowest_avg_expenses = min(scenario_metrics, key=lambda x: x['avg_expenses'])
        best_expense_control = max(scenario_metrics, key=lambda x: x['expense_control'])
        
        return {
            'total_scenarios': len(scenarios),
            'lowest_total_expenses': lowest_total_expenses['total_expenses'],
            'lowest_avg_expenses': lowest_avg_expenses['avg_expenses'],
            'best_expense_control': best_expense_control['expense_control']
        }
    
    except Exception as e:
        st.error(f"Error calculating multi-scenario expense summary: {str(e)}")
        return {
            'total_scenarios': 0,
            'lowest_total_expenses': 0.0,
            'lowest_avg_expenses': 0.0,
            'best_expense_control': 0.0
        }


def create_income_comparison_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create income comparison chart using unified models."""
    try:
        # Prepare data using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    plot_data.append({
                        'Year': i,
                        'Total Income': point.gross_income_gbp,
                        'Scenario': scenario_name
                    })
        
        if not plot_data:
            return go.Figure()
        
        df = pd.DataFrame(plot_data)
        
        # Create line chart
        fig = px.line(
            df,
            x='Year',
            y='Total Income',
            color='Scenario',
            title='Income Comparison',
            labels={'Total Income': 'Total Income (£)', 'Year': 'Year'}
        )
        
        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating income comparison chart: {str(e)}")
        return go.Figure()


def create_expense_comparison_chart(scenarios: Dict[str, UnifiedFinancialScenario]) -> go.Figure:
    """Create expense comparison chart using unified models."""
    try:
        # Prepare data using unified structure
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                for i, point in enumerate(scenario.data_points, 1):
                    plot_data.append({
                        'Year': i,
                        'Total Expenses': point.total_expenses_gbp,
                        'Scenario': scenario_name
                    })
        
        if not plot_data:
            return go.Figure()
        
        df = pd.DataFrame(plot_data)
        
        # Create line chart
        fig = px.line(
            df,
            x='Year',
            y='Total Expenses',
            color='Scenario',
            title='Expense Comparison',
            labels={'Total Expenses': 'Total Expenses (£)', 'Year': 'Year'}
        )
        
        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    except Exception as e:
        st.error(f"Error creating expense comparison chart: {str(e)}")
        return go.Figure()


def main() -> None:
    """Main function to render the income and expense breakdown page."""
    render_income_expense_page()


if __name__ == "__main__":
    main() 