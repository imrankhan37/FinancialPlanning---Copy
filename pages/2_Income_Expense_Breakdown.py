"""
Income & Expense Breakdown Page
Hierarchical drill-down analysis of income and expense components.
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


def render_income_expense_page(scenarios_to_analyze=None) -> None:
    """Render the income and expense breakdown page."""
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">💰 Income & Expense Analysis</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Detailed breakdown of income sources, expense categories, and cash flow patterns with drill-down capabilities.</p>
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


def render_income_breakdown(scenarios: Dict[str, Any]) -> None:
    """Render income breakdown analysis."""
    
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
        st.info(f"📊 Analyzing {len(scenario_names)} scenarios: {', '.join(scenario_names)}")
        # Show multi-scenario analysis
        render_multi_scenario_income_analysis(scenarios)
    
    # Scenario selector for detailed comparison
    st.markdown("### Scenario Comparison Selector")
    selected_scenarios = st.multiselect(
        "Choose scenarios to compare in detail:",
        options=scenario_names,
        default=scenario_names[:2] if len(scenario_names) >= 2 else scenario_names,
        max_selections=2,
        help="Select up to 2 scenarios for detailed side-by-side comparison",
        key="income_comparison_selector"
    )
    
    if len(selected_scenarios) == 2:
        st.markdown("### Detailed Side-by-Side Comparison")
        comparison_scenarios = {name: scenarios[name] for name in selected_scenarios}
        render_comparison_income_analysis(comparison_scenarios)
    elif len(selected_scenarios) == 1:
        st.markdown("### Single Scenario Analysis")
        single_scenario = {name: scenarios[name] for name in selected_scenarios}
        render_single_scenario_income_analysis(single_scenario)


def render_income_metrics(scenarios: Dict[str, Any], component: str) -> None:
    """Render income metrics for a specific component."""
    
    # Calculate metrics for the component
    component_data = []
    
    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            values = []
            for point in scenario.data_points:
                if component == "Salary":
                    # Use _equiv field if available, otherwise use base field
                    if hasattr(point, 'gross_salary_gbp_equiv') and point.gross_salary_gbp_equiv > 0:
                        value = point.gross_salary_gbp_equiv
                    elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                        value = point.gross_salary_gbp
                    elif hasattr(point, 'gross_salary_usd') and point.gross_salary_usd > 0:
                        value = point.gross_salary_usd / 1.26
                    else:
                        value = 0
                elif component == "Bonus":
                    # Use _equiv field if available, otherwise use base field
                    if hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0:
                        value = point.gross_bonus_gbp_equiv
                    elif hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0:
                        value = point.gross_bonus_gbp
                    elif hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0:
                        value = point.gross_bonus_usd / 1.26
                    else:
                        value = 0
                elif component == "RSU":
                    # Use _equiv field if available, otherwise use base field
                    if hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0:
                        value = point.vested_rsu_gbp_equiv
                    elif hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0:
                        value = point.vested_rsu_gbp
                    elif hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0:
                        value = point.vested_rsu_usd / 1.26
                    else:
                        value = 0
                else:
                    value = 0
                    values.append(value)
            avg_value = np.mean(values) if values else 0
            total_value = sum(values)
            component_data.append({
                'scenario': scenario_name,
                'avg': avg_value,
                'total': total_value
            })
    
    if component_data:
        best_avg = max(component_data, key=lambda x: x['avg'])
        best_total = max(component_data, key=lambda x: x['total'])
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; margin: 0.5rem 0; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4>{component} Analysis</h4>
            <p><strong>Best Avg:</strong> {format_currency(best_avg['avg'])}<br>
            <strong>Best Total:</strong> {format_currency(best_total['total'])}</p>
        </div>
        """, unsafe_allow_html=True)


def render_income_table(scenarios: Dict[str, Any]) -> None:
    """Render detailed income table."""
    
    income_data = []
    
    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            # Calculate income metrics
            total_salary = 0
            total_bonus = 0
            total_rsu = 0
            
            for point in scenario.data_points:
                # Salary
                if hasattr(point, 'gross_salary_gbp_equiv') and point.gross_salary_gbp_equiv > 0:
                    salary = point.gross_salary_gbp_equiv
                elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                    salary = point.gross_salary_gbp
                elif hasattr(point, 'gross_salary_usd') and point.gross_salary_usd > 0:
                    salary = point.gross_salary_usd / 1.26
                else:
                    salary = 0
                total_salary += salary
                
                # Bonus
                if hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0:
                    bonus = point.gross_bonus_gbp_equiv
                elif hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0:
                    bonus = point.gross_bonus_gbp
                elif hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0:
                    bonus = point.gross_bonus_usd / 1.26
                else:
                    bonus = 0
                total_bonus += bonus
                
                # RSU
                if hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0:
                    rsu = point.vested_rsu_gbp_equiv
                elif hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0:
                    rsu = point.vested_rsu_gbp
                elif hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0:
                    rsu = point.vested_rsu_usd / 1.26
                else:
                    rsu = 0
                total_rsu += rsu
            
            total_income = total_salary + total_bonus + total_rsu
            
            income_data.append({
                'Scenario': scenario_name,
                'Total Salary': format_currency(total_salary),
                'Total Bonus': format_currency(total_bonus),
                'Total RSU': format_currency(total_rsu),
                'Total Income': format_currency(total_income),
                'Salary %': f"{(total_salary / max(1, total_income)) * 100:.1f}%",
                'Bonus %': f"{(total_bonus / max(1, total_income)) * 100:.1f}%",
                'RSU %': f"{(total_rsu / max(1, total_income)) * 100:.1f}%"
            })
    
    if income_data:
        df = pd.DataFrame(income_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_expense_breakdown(scenarios: Dict[str, Any]) -> None:
    """Render expense breakdown analysis."""
    
    st.markdown("### 💸 Expense Analysis")
    st.markdown("Detailed breakdown of expenses across all scenarios.")
    
    # Debug: Check what data is available
    debug_info = []
    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            for i, point in enumerate(scenario.data_points[:3]):  # Check first 3 points
                debug_info.append({
                    'Scenario': scenario_name,
                    'Year': point.year,
                    'Total Expenses GBP Equiv': getattr(point, 'total_expenses_gbp_equiv', 0),
                    'Total Expenses GBP': getattr(point, 'total_expenses_gbp', 0),
                    'Total Expenses USD': getattr(point, 'total_expenses_usd', 0),
                    'Income Tax GBP Equiv': getattr(point, 'income_tax_gbp_equiv', 0),
                    'Income Tax GBP': getattr(point, 'income_tax_gbp', 0),
                    'Income Tax USD': getattr(point, 'income_tax_usd', 0)
                })
    
    if debug_info:
        st.markdown("#### 🔍 Debug: Expense Data Available")
        debug_df = pd.DataFrame(debug_info)
        st.dataframe(debug_df, use_container_width=True)
    
    # Continue with normal expense analysis
    if len(scenarios) == 1:
        render_single_scenario_expense_analysis(scenarios)
    elif len(scenarios) == 2:
        render_comparison_expense_analysis(scenarios)
    else:
        render_multi_scenario_expense_analysis(scenarios)


def render_expense_metrics(scenarios: Dict[str, Any], component: str) -> None:
    """Render expense metrics for a specific component."""
    
    # Calculate metrics for the component
    component_data = []
    
    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            values = []
            for point in scenario.data_points:
                if component == "Housing":
                    # Estimate housing as 30% of total expenses
                    if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0:
                        total_expenses = point.total_expenses_gbp_equiv
                    elif hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0:
                        total_expenses = point.total_expenses_gbp
                    elif hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0:
                        total_expenses = point.total_expenses_usd / 1.26
                    else:
                        total_expenses = 0
                    value = total_expenses * 0.3
                elif component == "Taxes":
                    if hasattr(point, 'income_tax_gbp_equiv') and point.income_tax_gbp_equiv > 0:
                        value = point.income_tax_gbp_equiv
                    elif hasattr(point, 'income_tax_gbp') and point.income_tax_gbp > 0:
                        value = point.income_tax_gbp
                    elif hasattr(point, 'income_tax_usd') and point.income_tax_usd > 0:
                        value = point.income_tax_usd / 1.26
                    else:
                        value = 0
                elif component == "Personal":
                    # Estimate personal expenses as 20% of total expenses
                    if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0:
                        total_expenses = point.total_expenses_gbp_equiv
                    elif hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0:
                        total_expenses = point.total_expenses_gbp
                    elif hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0:
                        total_expenses = point.total_expenses_usd / 1.26
                    else:
                        total_expenses = 0
                    value = total_expenses * 0.2
        else:
            value = 0
            values.append(value)
            avg_value = np.mean(values) if values else 0
            total_value = sum(values)
            component_data.append({
                'scenario': scenario_name,
                'avg': avg_value,
                'total': total_value
            })
    
    if component_data:
        lowest_avg = min(component_data, key=lambda x: x['avg'])
        lowest_total = min(component_data, key=lambda x: x['total'])
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5rem; border-radius: 15px; margin: 0.5rem 0; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h4>{component} Analysis</h4>
            <p><strong>Lowest Avg:</strong> {format_currency(lowest_avg['avg'])}<br>
            <strong>Lowest Total:</strong> {format_currency(lowest_total['total'])}</p>
        </div>
        """, unsafe_allow_html=True)


def render_expense_table(scenarios: Dict[str, Any]) -> None:
    """Render detailed expense table."""
    
    expense_data = []
    
    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            # Calculate expense metrics
            total_expenses = 0
            total_taxes = 0
            
            for point in scenario.data_points:
                # Total expenses
                if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0:
                    expenses = point.total_expenses_gbp_equiv
                elif hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0:
                    expenses = point.total_expenses_gbp
                elif hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0:
                    expenses = point.total_expenses_usd / 1.26
                else:
                    expenses = 0
                total_expenses += expenses
                
                # Taxes
                if hasattr(point, 'income_tax_gbp_equiv') and point.income_tax_gbp_equiv > 0:
                    taxes = point.income_tax_gbp_equiv
                elif hasattr(point, 'income_tax_gbp') and point.income_tax_gbp > 0:
                    taxes = point.income_tax_gbp
                elif hasattr(point, 'income_tax_usd') and point.income_tax_usd > 0:
                    taxes = point.income_tax_usd / 1.26
                else:
                    taxes = 0
                total_taxes += taxes
            
            expense_data.append({
                    'Scenario': scenario_name,
                'Total Expenses': format_currency(total_expenses),
                'Total Taxes': format_currency(total_taxes),
                'Tax Burden %': f"{(total_taxes / max(1, total_expenses)) * 100:.1f}%"
            })
    
    if expense_data:
        df = pd.DataFrame(expense_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def render_cash_flow_analysis(scenarios: Dict[str, Any]) -> None:
    """Render cash flow analysis with enhanced styling."""
    try:
        # Load component styles
        load_component_styles(["enhanced_tables"])
        
        st.markdown("### 📈 Cash Flow Analysis")
        st.markdown("Analysis of net cash flow and cash flow ratios across scenarios.")
        
        # CSS already loaded via load_component_styles(["enhanced_tables"])
        
        # Formatting functions
        def format_currency(val):
            return f'£{val:,.0f}'
        
        def format_percentage(val):
            return f'{val:.1f}%'
        
        cash_flow_data = []
        
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                total_income = 0
                total_expenses = 0
                total_cash_flow = 0
                
                for point in scenario.data_points:
                    # Income
                    if hasattr(point, 'gross_salary_gbp_equiv') and point.gross_salary_gbp_equiv > 0:
                        salary = point.gross_salary_gbp_equiv
                    elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                        salary = point.gross_salary_gbp
                    elif hasattr(point, 'gross_salary_usd') and point.gross_salary_usd > 0:
                        salary = point.gross_salary_usd / 1.26
                    else:
                        salary = 0
                    
                    if hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0:
                        bonus = point.gross_bonus_gbp_equiv
                    elif hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0:
                        bonus = point.gross_bonus_gbp
                    elif hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0:
                        bonus = point.gross_bonus_usd / 1.26
                    else:
                        bonus = 0
                    
                    if hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0:
                        rsu = point.vested_rsu_gbp_equiv
                    elif hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0:
                        rsu = point.vested_rsu_gbp
                    elif hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0:
                        rsu = point.vested_rsu_usd / 1.26
                    else:
                        rsu = 0
                    
                    income = salary + bonus + rsu
                    total_income += income
                    
                    # Expenses
                    if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0:
                        expenses = point.total_expenses_gbp_equiv
                    elif hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0:
                        expenses = point.total_expenses_gbp
                    elif hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0:
                        expenses = point.total_expenses_usd / 1.26
                    else:
                        expenses = 0
                    
                    total_expenses += expenses
                    total_cash_flow += (income - expenses)
                
                cash_flow_ratio = (total_cash_flow / max(1, total_income)) * 100
                
                cash_flow_data.append({
                    'Scenario': scenario_name,
                    'Total Income': format_currency(total_income),
                    'Total Expenses': format_currency(total_expenses),
                    'Net Cash Flow': format_currency(total_cash_flow),
                    'Cash Flow Ratio': f"{cash_flow_ratio:.1f}%"
                })
        
        if cash_flow_data:
            # Enhanced table presentation with pandas Styler
            st.markdown('<div class="cash-flow-header">💰 Cash Flow Summary</div>', unsafe_allow_html=True)
            
            # Create clean dataframe for styling
            df = pd.DataFrame(cash_flow_data)
            
            # Convert currency strings to numeric for styling
            df['Net Cash Flow Numeric'] = df['Net Cash Flow'].str.replace('£', '').str.replace(',', '').astype(float)
            df['Cash Flow Ratio Numeric'] = df['Cash Flow Ratio'].str.replace('%', '').astype(float)
            
            # Apply pandas Styler with proper formatting - use raw numeric data for styling
            styled_df = df.style\
                .background_gradient(
                    subset=['Net Cash Flow Numeric'],
                    cmap='RdYlGn',
                    vmin=df['Net Cash Flow Numeric'].min(),
                    vmax=df['Net Cash Flow Numeric'].max()
                )\
                .background_gradient(
                    subset=['Cash Flow Ratio Numeric'],
                    cmap='RdYlGn',
                    vmin=df['Cash Flow Ratio Numeric'].min(),
                    vmax=df['Cash Flow Ratio Numeric'].max()
                )\
                .apply(lambda x: ['background-color: #e8f5e8' if i == df['Net Cash Flow Numeric'].idxmax() else '' for i in range(len(x))], subset=['Net Cash Flow Numeric'])\
                .apply(lambda x: ['background-color: #e8f5e8' if i == df['Cash Flow Ratio Numeric'].idxmax() else '' for i in range(len(x))], subset=['Cash Flow Ratio Numeric'])\
                .hide(axis='index')\
                .hide(axis='columns', subset=['Net Cash Flow Numeric', 'Cash Flow Ratio Numeric'])
            
            # Style the dataframe with custom CSS
            st.markdown('<div class="enhanced-table">', unsafe_allow_html=True)
            st.dataframe(
                styled_df, 
                use_container_width=True,
                column_config={
                    "Scenario": st.column_config.TextColumn("Scenario", width="medium"),
                    "Total Income": st.column_config.TextColumn("Total Income", width="medium"),
                    "Total Expenses": st.column_config.TextColumn("Total Expenses", width="medium"),
                    "Net Cash Flow": st.column_config.TextColumn("Net Cash Flow", width="medium"),
                    "Cash Flow Ratio": st.column_config.TextColumn("Cash Flow Ratio", width="medium")
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred while rendering cash flow analysis: {e}")


def render_detailed_tables(scenarios: Dict[str, Any]) -> None:
    """Render detailed data tables."""
    
    st.markdown("### Detailed Data Tables")
    st.markdown("Comprehensive tables showing all financial data for selected scenarios.")
    
    # Year-by-year breakdown
    st.markdown("#### Year-by-Year Breakdown")
    
    year_data = []
    
    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            for point in scenario.data_points:
                # Income components
                if hasattr(point, 'gross_salary_gbp_equiv') and point.gross_salary_gbp_equiv > 0:
                    income = point.gross_salary_gbp_equiv
                elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                    income = point.gross_salary_gbp
                elif hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0:
                    income = point.total_gross_usd / 1.26
                else:
                    income = 0
                
                if hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0:
                    bonus = point.gross_bonus_gbp_equiv
                elif hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0:
                    bonus = point.gross_bonus_gbp
                elif hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0:
                    bonus = point.gross_bonus_usd / 1.26
                else:
                    bonus = 0
                
                if hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0:
                    rsu = point.vested_rsu_gbp_equiv
                elif hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0:
                    rsu = point.vested_rsu_gbp
                elif hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0:
                    rsu = point.vested_rsu_usd / 1.26
                else:
                    rsu = 0
                
                # Expense components
                if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0:
                    expenses = point.total_expenses_gbp_equiv
                elif hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0:
                    expenses = point.total_expenses_gbp
                elif hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0:
                    expenses = point.total_expenses_usd / 1.26
                else:
                    expenses = 0
                
                if hasattr(point, 'income_tax_gbp_equiv') and point.income_tax_gbp_equiv > 0:
                    taxes = point.income_tax_gbp_equiv
                elif hasattr(point, 'income_tax_gbp') and point.income_tax_gbp > 0:
                    taxes = point.income_tax_gbp
                elif hasattr(point, 'income_tax_usd') and point.income_tax_usd > 0:
                    taxes = point.income_tax_usd / 1.26
                else:
                    taxes = 0
                
                # Net worth
                if hasattr(point, 'net_worth_gbp_equiv') and point.net_worth_gbp_equiv > 0:
                    net_worth = point.net_worth_gbp_equiv
                elif hasattr(point, 'net_worth_gbp') and point.net_worth_gbp > 0:
                    net_worth = point.net_worth_gbp
                elif hasattr(point, 'net_worth_usd') and point.net_worth_usd > 0:
                    net_worth = point.net_worth_usd / 1.26
                else:
                    net_worth = 0
                
                year_data.append({
                    'Scenario': scenario_name,
                    'Year': point.year,
                    'Income (£)': income,
                    'Bonus (£)': bonus,
                    'RSU (£)': rsu,
                    'Expenses (£)': expenses,
                    'Taxes (£)': taxes,
                    'Net Worth (£)': net_worth
                })
    
    if year_data:
        df = pd.DataFrame(year_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Detailed Data (CSV)",
            data=csv,
            file_name="detailed_financial_data.csv",
            mime="text/csv"
        )


def create_individual_income_component_chart(scenarios: Dict[str, Any], component: str) -> go.Figure:
    """Create chart for individual income component."""
    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = [point.year for point in scenario.data_points]
        
        if component == "Salary Only":
            # Handle international scenario salary
            values = []
            for point in scenario.data_points:
                value = point.gross_income_gbp_equiv if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0 else (
                    point.gross_salary_gbp if hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0 else (
                        point.total_gross_usd / 1.26 if hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0 else 0
                    )
                )
                values.append(value)
            title = "Salary Progression"
        elif component == "Bonus Only":
            # Handle international scenario bonus
            values = []
            for point in scenario.data_points:
                value = point.gross_bonus_gbp_equiv if hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0 else (
                    point.gross_bonus_gbp if hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0 else (
                        point.gross_bonus_usd / 1.26 if hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0 else 0
                    )
                )
                values.append(value)
            title = "Bonus Progression"
        elif component == "RSU Only":
            # Handle international scenario RSU
            values = []
            for point in scenario.data_points:
                value = point.vested_rsu_gbp_equiv if hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0 else (
                    point.vested_rsu_gbp if hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0 else (
                        point.vested_rsu_usd / 1.26 if hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0 else 0
                    )
                )
                values.append(value)
            title = "RSU Progression"
        else:
            values = []
            title = "Income Progression"
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=scenario_name,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>{scenario_name}</b><br>Year: %{{x}}<br>{component}: £%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=f"{component} (£)",
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_individual_expense_component_chart(scenarios: Dict[str, Any], component: str) -> go.Figure:
    """Create chart for individual expense component."""
    
    fig = go.Figure()
    
    colors = ['#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
    
    for i, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = [point.year for point in scenario.data_points]
        
        if component == "Housing Only":
            values = [point.total_expenses_gbp * 0.3 for point in scenario.data_points if hasattr(point, 'total_expenses_gbp')]
            title = "Housing Expenses"
        elif component == "Taxes Only":
            values = [point.income_tax_gbp for point in scenario.data_points if hasattr(point, 'income_tax_gbp')]
            title = "Tax Expenses"
        elif component == "Personal Only":
            values = [point.total_expenses_gbp * 0.2 for point in scenario.data_points if hasattr(point, 'total_expenses_gbp')]
            title = "Personal Expenses"
        elif component == "Other Only":
            values = [point.total_expenses_gbp * 0.5 for point in scenario.data_points if hasattr(point, 'total_expenses_gbp')]
            title = "Other Expenses"
        else:
            values = []
            title = "Expense Progression"
        
        # Use negative values for expenses
        values = [-v for v in values]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=values,
            mode='lines+markers',
            name=scenario_name,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>{scenario_name}</b><br>Year: %{{x}}<br>{component}: £%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Year",
        yaxis_title=f"{component} (£)",
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_cash_flow_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create cash flow chart."""
    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = [point.year for point in scenario.data_points]
        cash_flows = []
        
        for point in scenario.data_points:
            # Handle international scenario income - check _equiv first for international scenarios
            income = 0
            if hasattr(point, 'gross_income_gbp_equiv') and point.gross_income_gbp_equiv > 0:
                income += point.gross_income_gbp_equiv
            elif hasattr(point, 'gross_salary_gbp') and point.gross_salary_gbp > 0:
                income += point.gross_salary_gbp
            elif hasattr(point, 'total_gross_usd') and point.total_gross_usd > 0:
                income += point.total_gross_usd / 1.26
            
            # Add bonus and RSU if available
            if hasattr(point, 'gross_bonus_gbp') and point.gross_bonus_gbp > 0:
                income += point.gross_bonus_gbp
            elif hasattr(point, 'gross_bonus_gbp_equiv') and point.gross_bonus_gbp_equiv > 0:
                income += point.gross_bonus_gbp_equiv
            elif hasattr(point, 'gross_bonus_usd') and point.gross_bonus_usd > 0:
                income += point.gross_bonus_usd / 1.26
            
            if hasattr(point, 'vested_rsu_gbp') and point.vested_rsu_gbp > 0:
                income += point.vested_rsu_gbp
            elif hasattr(point, 'vested_rsu_gbp_equiv') and point.vested_rsu_gbp_equiv > 0:
                income += point.vested_rsu_gbp_equiv
            elif hasattr(point, 'vested_rsu_usd') and point.vested_rsu_usd > 0:
                income += point.vested_rsu_usd / 1.26
            
            # Handle international scenario expenses
            expenses = 0
            if hasattr(point, 'total_expenses_gbp_equiv') and point.total_expenses_gbp_equiv > 0:
                expenses += point.total_expenses_gbp_equiv
            elif hasattr(point, 'total_expenses_gbp') and point.total_expenses_gbp > 0:
                expenses += point.total_expenses_gbp
            elif hasattr(point, 'total_expenses_usd') and point.total_expenses_usd > 0:
                expenses += point.total_expenses_usd / 1.26
            
            cash_flow = income - expenses
            cash_flows.append(cash_flow)
        
        # Use different colors for positive and negative cash flows
        colors_positive = ['#2ca02c', '#1f77b4', '#9467bd']
        colors_negative = ['#d62728', '#ff7f0e', '#8c564b']
        
        color = colors_positive[i % len(colors_positive)] if cash_flows[-1] > 0 else colors_negative[i % len(colors_negative)]
        
        fig.add_trace(go.Scatter(
            x=years,
            y=cash_flows,
            mode='lines+markers',
            name=scenario_name,
            line=dict(color=color, width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>{scenario_name}</b><br>Year: %{{x}}<br>Cash Flow: £%{{y:,.0f}}<extra></extra>'
        ))
    
    # Add horizontal line at zero
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="Cash Flow Analysis",
        xaxis_title="Year",
        yaxis_title="Cash Flow (£)",
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_income_comparison_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create a side-by-side income comparison chart with stacked bars and common axes."""
    
    scenario_names = list(scenarios.keys())
    scenario1, scenario2 = scenario_names[0], scenario_names[1]
    
    # Create figure with subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"{scenario1} Income", f"{scenario2} Income"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
        horizontal_spacing=0.1
    )
    
    # Define colors for income components
    colors = {
        'salary': '#1f77b4',  # Blue
        'bonus': '#ff7f0e',   # Orange
        'rsu': '#2ca02c'      # Green
    }
    
    # Prepare data for both scenarios
    for col_idx, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = []
        salary_data = []
        bonus_data = []
        rsu_data = []
        
        for data_point in scenario.data_points:
            years.append(data_point.year)
            
            # Salary
            if hasattr(data_point, 'gross_salary_gbp_equiv') and data_point.gross_salary_gbp_equiv > 0:
                salary = data_point.gross_salary_gbp_equiv
            elif hasattr(data_point, 'gross_salary_gbp') and data_point.gross_salary_gbp > 0:
                salary = data_point.gross_salary_gbp
            elif hasattr(data_point, 'gross_salary_usd') and data_point.gross_salary_usd > 0:
                salary = data_point.gross_salary_usd / 1.26
            else:
                salary = 0
            salary_data.append(salary)
            
            # Bonus
            if hasattr(data_point, 'gross_bonus_gbp_equiv') and data_point.gross_bonus_gbp_equiv > 0:
                bonus = data_point.gross_bonus_gbp_equiv
            elif hasattr(data_point, 'gross_bonus_gbp') and data_point.gross_bonus_gbp > 0:
                bonus = data_point.gross_bonus_gbp
            elif hasattr(data_point, 'gross_bonus_usd') and data_point.gross_bonus_usd > 0:
                bonus = data_point.gross_bonus_usd / 1.26
            else:
                bonus = 0
            bonus_data.append(bonus)
            
            # RSU
            if hasattr(data_point, 'vested_rsu_gbp_equiv') and data_point.vested_rsu_gbp_equiv > 0:
                rsu = data_point.vested_rsu_gbp_equiv
            elif hasattr(data_point, 'vested_rsu_gbp') and data_point.vested_rsu_gbp > 0:
                rsu = data_point.vested_rsu_gbp
            elif hasattr(data_point, 'vested_rsu_usd') and data_point.vested_rsu_usd > 0:
                rsu = data_point.vested_rsu_usd / 1.26
            else:
                rsu = 0
            rsu_data.append(rsu)
        
        # Add stacked bar traces for each income component
        fig.add_trace(go.Bar(
            name="Salary",
            x=years,
            y=salary_data,
            marker_color=colors['salary'],
            opacity=0.8,
            showlegend=(col_idx == 0),  # Only show legend for first subplot
            xaxis=f'x{col_idx + 1}',
            yaxis=f'y{col_idx + 1}'
        ), row=1, col=col_idx + 1)
        
        fig.add_trace(go.Bar(
            name="Bonus",
            x=years,
            y=bonus_data,
            marker_color=colors['bonus'],
            opacity=0.8,
            showlegend=(col_idx == 0),  # Only show legend for first subplot
            xaxis=f'x{col_idx + 1}',
            yaxis=f'y{col_idx + 1}'
        ), row=1, col=col_idx + 1)
        
        fig.add_trace(go.Bar(
            name="RSU",
            x=years,
            y=rsu_data,
            marker_color=colors['rsu'],
            opacity=0.8,
            showlegend=(col_idx == 0),  # Only show legend for first subplot
            xaxis=f'x{col_idx + 1}',
            yaxis=f'y{col_idx + 1}'
        ), row=1, col=col_idx + 1)
    
    # Update layout for stacked bars with common axes
    fig.update_layout(
        title="Income Comparison: Side-by-Side Analysis",
        barmode='stack',  # Stack the bars
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    # Update axes to have common ranges
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=1, col=2)
    fig.update_yaxes(title_text="Income (£)", row=1, col=1)
    fig.update_yaxes(title_text="Income (£)", row=1, col=2)
    
    # Ensure both y-axes have the same range for better comparison
    all_y_values = []
    for trace in fig.data:
        if trace.y is not None:
            all_y_values.extend(trace.y)
    
    if all_y_values:
        y_max = max(all_y_values) * 1.1
        fig.update_yaxes(range=[0, y_max], row=1, col=1)
        fig.update_yaxes(range=[0, y_max], row=1, col=2)
    
    return fig


def create_expense_comparison_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create a side-by-side expense comparison chart with stacked bars and common axes."""
    
    scenario_names = list(scenarios.keys())
    scenario1, scenario2 = scenario_names[0], scenario_names[1]
    
    # Create figure with subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(f"{scenario1} Expenses", f"{scenario2} Expenses"),
        specs=[[{"type": "bar"}, {"type": "bar"}]],
        horizontal_spacing=0.1
    )
    
    # Define colors for expense components
    colors = {
        'housing': '#ff7f0e',  # Orange
        'taxes': '#d62728',    # Red
        'living': '#2ca02c'    # Green
    }
    
    # Prepare data for both scenarios
    for col_idx, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = []
        housing_data = []
        taxes_data = []
        living_data = []
        
        for data_point in scenario.data_points:
            years.append(data_point.year)
            
            # Housing (30% of total expenses)
            if hasattr(data_point, 'total_expenses_gbp_equiv') and data_point.total_expenses_gbp_equiv > 0:
                total_expenses = data_point.total_expenses_gbp_equiv
            elif hasattr(data_point, 'total_expenses_gbp') and data_point.total_expenses_gbp > 0:
                total_expenses = data_point.total_expenses_gbp
            elif hasattr(data_point, 'total_expenses_usd') and data_point.total_expenses_usd > 0:
                total_expenses = data_point.total_expenses_usd / 1.26
            else:
                total_expenses = 0
            housing_data.append(total_expenses * 0.3)
            
            # Taxes
            if hasattr(data_point, 'income_tax_gbp_equiv') and data_point.income_tax_gbp_equiv > 0:
                taxes = data_point.income_tax_gbp_equiv
            elif hasattr(data_point, 'income_tax_gbp') and data_point.income_tax_gbp > 0:
                taxes = data_point.income_tax_gbp
            elif hasattr(data_point, 'income_tax_usd') and data_point.income_tax_usd > 0:
                taxes = data_point.income_tax_usd / 1.26
            else:
                taxes = 0
            taxes_data.append(taxes)
            
            # Living costs (70% of remaining expenses)
            living_data.append((total_expenses - taxes) * 0.7)
        
        # Add stacked bar traces for each expense component
        fig.add_trace(go.Bar(
            name="Housing",
            x=years,
            y=housing_data,
            marker_color=colors['housing'],
            opacity=0.8,
            showlegend=(col_idx == 0),  # Only show legend for first subplot
            xaxis=f'x{col_idx + 1}',
            yaxis=f'y{col_idx + 1}'
        ), row=1, col=col_idx + 1)
        
        fig.add_trace(go.Bar(
            name="Taxes",
            x=years,
            y=taxes_data,
            marker_color=colors['taxes'],
            opacity=0.8,
            showlegend=(col_idx == 0),  # Only show legend for first subplot
            xaxis=f'x{col_idx + 1}',
            yaxis=f'y{col_idx + 1}'
        ), row=1, col=col_idx + 1)
        
        fig.add_trace(go.Bar(
            name="Living",
            x=years,
            y=living_data,
            marker_color=colors['living'],
            opacity=0.8,
            showlegend=(col_idx == 0),  # Only show legend for first subplot
            xaxis=f'x{col_idx + 1}',
            yaxis=f'y{col_idx + 1}'
        ), row=1, col=col_idx + 1)
    
    # Update layout for stacked bars with common axes
    fig.update_layout(
        title="Expense Comparison: Side-by-Side Analysis",
        barmode='stack',  # Stack the bars
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    # Update axes to have common ranges
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_xaxes(title_text="Year", row=1, col=2)
    fig.update_yaxes(title_text="Expenses (£)", row=1, col=1)
    fig.update_yaxes(title_text="Expenses (£)", row=1, col=2)
    
    # Ensure both y-axes have the same range for better comparison
    all_y_values = []
    for trace in fig.data:
        if trace.y is not None:
            all_y_values.extend(trace.y)
    
    if all_y_values:
        y_max = max(all_y_values) * 1.1
        fig.update_yaxes(range=[0, y_max], row=1, col=1)
        fig.update_yaxes(range=[0, y_max], row=1, col=2)
    
    return fig


def calculate_yoy_income_metrics(scenarios: Dict[str, Any]) -> Dict[str, float]:
    """Calculate year-over-year income metrics for comparison."""
    
    metrics = {}
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points or len(scenario.data_points) < 2:
            continue
        
        # Calculate total income for each year
        yearly_income = []
        for data_point in scenario.data_points:
            total_income = (
                (data_point.salary_gbp if hasattr(data_point, 'salary_gbp') else 0) +
                (data_point.bonus_gbp if hasattr(data_point, 'bonus_gbp') else 0) +
                (data_point.rsu_gbp if hasattr(data_point, 'rsu_gbp') else 0)
            )
            yearly_income.append(total_income)
        
        # Calculate YoY differences
        if len(yearly_income) >= 2:
            yoy_diff = ((yearly_income[-1] - yearly_income[0]) / max(1, yearly_income[0])) * 100
            metrics[f'{scenario_name}_total_income_diff'] = yoy_diff
    
    # Calculate average differences
    total_income_diffs = [v for k, v in metrics.items() if 'total_income_diff' in k]
    salary_diffs = [v for k, v in metrics.items() if 'salary_diff' in k]
    bonus_diffs = [v for k, v in metrics.items() if 'bonus_diff' in k]
    rsu_diffs = [v for k, v in metrics.items() if 'rsu_diff' in k]
    
    return {
        'total_income_diff': np.mean(total_income_diffs) if total_income_diffs else 0,
        'salary_diff': np.mean(salary_diffs) if salary_diffs else 0,
        'bonus_diff': np.mean(bonus_diffs) if bonus_diffs else 0,
        'rsu_diff': np.mean(rsu_diffs) if rsu_diffs else 0
    }


def calculate_yoy_expense_metrics(scenarios: Dict[str, Any]) -> Dict[str, float]:
    """Calculate year-over-year expense metrics for comparison."""
    
    metrics = {}
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points or len(scenario.data_points) < 2:
            continue
        
        # Calculate total expenses for each year
        yearly_expenses = []
        for data_point in scenario.data_points:
            total_expenses = (
                (data_point.total_expenses_gbp_equiv if hasattr(data_point, 'total_expenses_gbp_equiv') and data_point.total_expenses_gbp_equiv > 0 else 0) +
                (data_point.total_expenses_gbp if hasattr(data_point, 'total_expenses_gbp') and data_point.total_expenses_gbp > 0 else 0) +
                (data_point.total_expenses_usd / 1.26 if hasattr(data_point, 'total_expenses_usd') and data_point.total_expenses_usd > 0 else 0)
            )
            yearly_expenses.append(total_expenses)
        
        # Calculate YoY differences
        if len(yearly_expenses) >= 2:
            yoy_diff = ((yearly_expenses[-1] - yearly_expenses[0]) / max(1, yearly_expenses[0])) * 100
            metrics[f'{scenario_name}_total_expense_diff'] = yoy_diff
    
    # Calculate average differences
    total_expense_diffs = [v for k, v in metrics.items() if 'total_expense_diff' in k]
    housing_diffs = [v for k, v in metrics.items() if 'housing_diff' in k]
    tax_diffs = [v for k, v in metrics.items() if 'tax_diff' in k]
    living_diffs = [v for k, v in metrics.items() if 'living_diff' in k]
    
    return {
        'total_expense_diff': np.mean(total_expense_diffs) if total_expense_diffs else 0,
        'housing_diff': np.mean(housing_diffs) if housing_diffs else 0,
        'tax_diff': np.mean(tax_diffs) if tax_diffs else 0,
        'living_diff': np.mean(living_diffs) if living_diffs else 0
    }


def create_income_comparison_table(scenarios: Dict[str, Any]) -> pd.DataFrame:
    """Create a detailed income comparison table."""
    
    comparison_data = []
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points:
            continue
        
        for data_point in scenario.data_points:
            # Salary
            if hasattr(data_point, 'gross_salary_gbp_equiv') and data_point.gross_salary_gbp_equiv > 0:
                salary = data_point.gross_salary_gbp_equiv
            elif hasattr(data_point, 'gross_salary_gbp') and data_point.gross_salary_gbp > 0:
                salary = data_point.gross_salary_gbp
            elif hasattr(data_point, 'gross_salary_usd') and data_point.gross_salary_usd > 0:
                salary = data_point.gross_salary_usd / 1.26
            else:
                salary = 0
            
            # Bonus
            if hasattr(data_point, 'gross_bonus_gbp_equiv') and data_point.gross_bonus_gbp_equiv > 0:
                bonus = data_point.gross_bonus_gbp_equiv
            elif hasattr(data_point, 'gross_bonus_gbp') and data_point.gross_bonus_gbp > 0:
                bonus = data_point.gross_bonus_gbp
            elif hasattr(data_point, 'gross_bonus_usd') and data_point.gross_bonus_usd > 0:
                bonus = data_point.gross_bonus_usd / 1.26
            else:
                bonus = 0
            
            # RSU
            if hasattr(data_point, 'vested_rsu_gbp_equiv') and data_point.vested_rsu_gbp_equiv > 0:
                rsu = data_point.vested_rsu_gbp_equiv
            elif hasattr(data_point, 'vested_rsu_gbp') and data_point.vested_rsu_gbp > 0:
                rsu = data_point.vested_rsu_gbp
            elif hasattr(data_point, 'vested_rsu_usd') and data_point.vested_rsu_usd > 0:
                rsu = data_point.vested_rsu_usd / 1.26
            else:
                rsu = 0
            
            comparison_data.append({
                    'Scenario': scenario_name,
                'Year': data_point.year,
                'Salary (£)': salary,
                'Bonus (£)': bonus,
                'RSU (£)': rsu,
                'Total Income (£)': salary + bonus + rsu
            })
    
    return pd.DataFrame(comparison_data)


def create_expense_comparison_table(scenarios: Dict[str, Any]) -> pd.DataFrame:
    """Create a detailed expense comparison table."""
    
    comparison_data = []
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points:
            continue
        
        for data_point in scenario.data_points:
            # Total expenses
            if hasattr(data_point, 'total_expenses_gbp_equiv') and data_point.total_expenses_gbp_equiv > 0:
                expenses = data_point.total_expenses_gbp_equiv
            elif hasattr(data_point, 'total_expenses_gbp') and data_point.total_expenses_gbp > 0:
                expenses = data_point.total_expenses_gbp
            elif hasattr(data_point, 'total_expenses_usd') and data_point.total_expenses_usd > 0:
                expenses = data_point.total_expenses_usd / 1.26
            else:
                expenses = 0
            
            # Taxes
            if hasattr(data_point, 'income_tax_gbp_equiv') and data_point.income_tax_gbp_equiv > 0:
                taxes = data_point.income_tax_gbp_equiv
            elif hasattr(data_point, 'income_tax_gbp') and data_point.income_tax_gbp > 0:
                taxes = data_point.income_tax_gbp
            elif hasattr(data_point, 'income_tax_usd') and data_point.income_tax_usd > 0:
                taxes = data_point.income_tax_usd / 1.26
            else:
                taxes = 0
            
            # Other expenses
            other_expenses = expenses - taxes
            
            comparison_data.append({
                'Scenario': scenario_name,
                'Year': data_point.year,
                'Total Expenses (£)': expenses,
                'Taxes (£)': taxes,
                'Other Expenses (£)': other_expenses,
                'Tax %': f"{(taxes / max(1, expenses)) * 100:.1f}%",
                'Other %': f"{(other_expenses / max(1, expenses)) * 100:.1f}%"
            })
    
    return pd.DataFrame(comparison_data)


def generate_income_insights(scenarios: Dict[str, Any], yoy_metrics: Dict[str, float]) -> List[str]:
    """Generate insights based on income comparison."""
    
    insights = []
    
    # Compare total income growth
    if yoy_metrics['total_income_diff'] > 10:
        insights.append("📈 Strong income growth observed across scenarios")
    elif yoy_metrics['total_income_diff'] > 5:
        insights.append("✅ Moderate income growth with good potential")
    elif yoy_metrics['total_income_diff'] > 0:
        insights.append("⚠️ Slow income growth - consider optimization")
    else:
        insights.append("⚠️ Income decline detected - review strategy")
    
    # Compare component performance
    if yoy_metrics['salary_diff'] > yoy_metrics['bonus_diff']:
        insights.append("💰 Salary growth outperforms bonus growth")
    else:
        insights.append("🎁 Bonus growth leads income components")
    
    if yoy_metrics['rsu_diff'] > 0:
        insights.append("📈 RSU component shows positive growth")
    
    # Scenario comparison
    scenario_names = list(scenarios.keys())
    if len(scenario_names) == 2:
        insights.append(f"🔄 Comparing {scenario_names[0]} vs {scenario_names[1]} for detailed analysis")
    
    return insights


def generate_expense_insights(scenarios: Dict[str, Any], yoy_metrics: Dict[str, float]) -> List[str]:
    """Generate insights based on expense comparison."""
    
    insights = []
    
    # Compare total expense growth
    if yoy_metrics['total_expense_diff'] > 10:
        insights.append("📈 Strong expense growth observed across scenarios")
    elif yoy_metrics['total_expense_diff'] > 5:
        insights.append("✅ Moderate expense growth with good potential")
    elif yoy_metrics['total_expense_diff'] > 0:
        insights.append("⚠️ Slow expense growth - consider optimization")
    else:
        insights.append("⚠️ Expense decline detected - review strategy")
    
    # Compare component performance
    if yoy_metrics['housing_diff'] > yoy_metrics['tax_diff']:
        insights.append("🏠 Housing costs growth outperforms tax growth")
    else:
        insights.append("💰 Tax costs growth leads expense components")
    
    if yoy_metrics['living_diff'] > 0:
        insights.append("📈 Living costs show positive growth")
    
    # Scenario comparison
    scenario_names = list(scenarios.keys())
    if len(scenario_names) == 2:
        insights.append(f"🔄 Comparing {scenario_names[0]} vs {scenario_names[1]} for detailed analysis")
    
    return insights


def render_single_scenario_income_analysis(scenarios: Dict[str, Any]) -> None:
    """Render single scenario income analysis."""
    
    scenario_name = list(scenarios.keys())[0]
    scenario = scenarios[scenario_name]
    
    # Create single scenario chart
    with st.spinner("Creating single scenario chart..."):
        fig = create_single_scenario_income_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"single_income_{scenario_name}_{uuid.uuid4()}")
    
    # Score cards for single scenario
    st.markdown("### Income Performance Metrics")
    metrics = calculate_single_scenario_income_metrics(scenarios)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['total_income']:,.0f}</div>
            <div class="metric-label">Total Income</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['avg_salary']:,.0f}</div>
            <div class="metric-label">Avg Salary</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['avg_bonus']:,.0f}</div>
            <div class="metric-label">Avg Bonus</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['avg_rsu']:,.0f}</div>
            <div class="metric-label">Avg RSU</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed table
    st.markdown("### Detailed Income Breakdown")
    comparison_df = create_income_comparison_table(scenarios)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)


def render_comparison_income_analysis(scenarios: Dict[str, Any]) -> None:
    """Render side-by-side comparison income analysis."""
    
    scenario_names = list(scenarios.keys())
    scenario_key = "_".join(scenario_names)
    
    # Create side-by-side comparison charts
    with st.spinner("Creating comparison charts..."):
        fig_income = create_income_comparison_chart(scenarios)
        st.plotly_chart(fig_income, use_container_width=True, config={'displayModeBar': True}, key=f"comparison_income_{scenario_key}_{uuid.uuid4()}")
    
    # Calculate YoY metrics for insights
    yoy_metrics = calculate_yoy_income_metrics(scenarios)
    
    # Detailed comparison table
    st.markdown("### Detailed Income Comparison")
    comparison_df = create_income_comparison_table(scenarios)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Insights
    st.markdown("### Key Insights")
    insights = generate_income_insights(scenarios, yoy_metrics)
    for insight in insights:
        if insight.startswith("✅"):
            st.success(insight)
        elif insight.startswith("⚠️"):
            st.warning(insight)
        elif insight.startswith("📈"):
            st.info(insight)
        else:
            st.info(insight)


def render_multi_scenario_income_analysis(scenarios: Dict[str, Any]) -> None:
    """Render multi-scenario income analysis."""
    
    scenario_names = list(scenarios.keys())
    scenario_key = "_".join(scenario_names[:3])  # Use first 3 scenario names for key
    
    # Create multi-scenario chart
    with st.spinner("Creating multi-scenario chart..."):
        fig = create_multi_scenario_income_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"multi_income_{scenario_key}_{uuid.uuid4()}")
    
    # Summary metrics
    st.markdown("### Income Summary Across Scenarios")
    summary_metrics = calculate_multi_scenario_income_summary(scenarios)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary_metrics['scenario_count']}</div>
            <div class="metric-label">Scenarios Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{summary_metrics['avg_total_income']:,.0f}</div>
            <div class="metric-label">Avg Total Income</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary_metrics['income_growth_range']:+.1f}%</div>
            <div class="metric-label">Income Growth Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed table
    st.markdown("### Detailed Income Comparison")
    comparison_df = create_income_comparison_table(scenarios)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)


def create_single_scenario_income_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create a single scenario income chart."""
    
    scenario_name = list(scenarios.keys())[0]
    scenario = scenarios[scenario_name]
    
    if not scenario.data_points:
        return go.Figure()
    
    years = []
    salary_data = []
    bonus_data = []
    rsu_data = []
    
    for data_point in scenario.data_points:
        years.append(data_point.year)
        
        # Salary
        if hasattr(data_point, 'gross_salary_gbp_equiv') and data_point.gross_salary_gbp_equiv > 0:
            salary = data_point.gross_salary_gbp_equiv
        elif hasattr(data_point, 'gross_salary_gbp') and data_point.gross_salary_gbp > 0:
            salary = data_point.gross_salary_gbp
        elif hasattr(data_point, 'gross_salary_usd') and data_point.gross_salary_usd > 0:
            salary = data_point.gross_salary_usd / 1.26
        else:
            salary = 0
        salary_data.append(salary)
        
        # Bonus
        if hasattr(data_point, 'gross_bonus_gbp_equiv') and data_point.gross_bonus_gbp_equiv > 0:
            bonus = data_point.gross_bonus_gbp_equiv
        elif hasattr(data_point, 'gross_bonus_gbp') and data_point.gross_bonus_gbp > 0:
            bonus = data_point.gross_bonus_gbp
        elif hasattr(data_point, 'gross_bonus_usd') and data_point.gross_bonus_usd > 0:
            bonus = data_point.gross_bonus_usd / 1.26
        else:
            bonus = 0
        bonus_data.append(bonus)
        
        # RSU
        if hasattr(data_point, 'vested_rsu_gbp_equiv') and data_point.vested_rsu_gbp_equiv > 0:
            rsu = data_point.vested_rsu_gbp_equiv
        elif hasattr(data_point, 'vested_rsu_gbp') and data_point.vested_rsu_gbp > 0:
            rsu = data_point.vested_rsu_gbp
        elif hasattr(data_point, 'vested_rsu_usd') and data_point.vested_rsu_usd > 0:
            rsu = data_point.vested_rsu_usd / 1.26
        else:
            rsu = 0
        rsu_data.append(rsu)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="Salary",
        x=years,
        y=salary_data,
        marker_color='#1f77b4',
        opacity=0.8
    ))
    
    fig.add_trace(go.Bar(
        name="Bonus",
        x=years,
        y=bonus_data,
        marker_color='#ff7f0e',
        opacity=0.8
    ))
    
    fig.add_trace(go.Bar(
        name="RSU",
        x=years,
        y=rsu_data,
        marker_color='#2ca02c',
        opacity=0.8
    ))
    
    fig.update_layout(
        title=f"Income Breakdown: {scenario_name}",
        xaxis_title="Year",
        yaxis_title="Income (£)",
        barmode='stack',
        height=500
    )
    
    return fig


def calculate_single_scenario_income_metrics(scenarios: Dict[str, Any]) -> Dict[str, float]:
    """Calculate income metrics for a single scenario."""
    
    scenario_name = list(scenarios.keys())[0]
    scenario = scenarios[scenario_name]
    
    if not scenario.data_points:
        return {
            'total_income': 0,
            'avg_salary': 0,
            'avg_bonus': 0,
            'avg_rsu': 0
        }
    
    total_salary = 0
    total_bonus = 0
    total_rsu = 0
    
    for data_point in scenario.data_points:
        # Salary
        if hasattr(data_point, 'gross_salary_gbp_equiv') and data_point.gross_salary_gbp_equiv > 0:
            salary = data_point.gross_salary_gbp_equiv
        elif hasattr(data_point, 'gross_salary_gbp') and data_point.gross_salary_gbp > 0:
            salary = data_point.gross_salary_gbp
        elif hasattr(data_point, 'gross_salary_usd') and data_point.gross_salary_usd > 0:
            salary = data_point.gross_salary_usd / 1.26
        else:
            salary = 0
        total_salary += salary
        
        # Bonus
        if hasattr(data_point, 'gross_bonus_gbp_equiv') and data_point.gross_bonus_gbp_equiv > 0:
            bonus = data_point.gross_bonus_gbp_equiv
        elif hasattr(data_point, 'gross_bonus_gbp') and data_point.gross_bonus_gbp > 0:
            bonus = data_point.gross_bonus_gbp
        elif hasattr(data_point, 'gross_bonus_usd') and data_point.gross_bonus_usd > 0:
            bonus = data_point.gross_bonus_usd / 1.26
        else:
            bonus = 0
        total_bonus += bonus
        
        # RSU
        if hasattr(data_point, 'vested_rsu_gbp_equiv') and data_point.vested_rsu_gbp_equiv > 0:
            rsu = data_point.vested_rsu_gbp_equiv
        elif hasattr(data_point, 'vested_rsu_gbp') and data_point.vested_rsu_gbp > 0:
            rsu = data_point.vested_rsu_gbp
        elif hasattr(data_point, 'vested_rsu_usd') and data_point.vested_rsu_usd > 0:
            rsu = data_point.vested_rsu_usd / 1.26
        else:
            rsu = 0
        total_rsu += rsu
    
    num_years = len(scenario.data_points)
    
    return {
        'total_income': total_salary + total_bonus + total_rsu,
        'avg_salary': total_salary / num_years if num_years > 0 else 0,
        'avg_bonus': total_bonus / num_years if num_years > 0 else 0,
        'avg_rsu': total_rsu / num_years if num_years > 0 else 0
    }


def create_multi_scenario_income_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create a multi-scenario income comparison chart."""
    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = []
        total_income_data = []
        
        for data_point in scenario.data_points:
            years.append(data_point.year)
            
            # Salary
            if hasattr(data_point, 'gross_salary_gbp_equiv') and data_point.gross_salary_gbp_equiv > 0:
                salary = data_point.gross_salary_gbp_equiv
            elif hasattr(data_point, 'gross_salary_gbp') and data_point.gross_salary_gbp > 0:
                salary = data_point.gross_salary_gbp
            elif hasattr(data_point, 'gross_salary_usd') and data_point.gross_salary_usd > 0:
                salary = data_point.gross_salary_usd / 1.26
            else:
                salary = 0
            
            # Bonus
            if hasattr(data_point, 'gross_bonus_gbp_equiv') and data_point.gross_bonus_gbp_equiv > 0:
                bonus = data_point.gross_bonus_gbp_equiv
            elif hasattr(data_point, 'gross_bonus_gbp') and data_point.gross_bonus_gbp > 0:
                bonus = data_point.gross_bonus_gbp
            elif hasattr(data_point, 'gross_bonus_usd') and data_point.gross_bonus_usd > 0:
                bonus = data_point.gross_bonus_usd / 1.26
            else:
                bonus = 0
            
            # RSU
            if hasattr(data_point, 'vested_rsu_gbp_equiv') and data_point.vested_rsu_gbp_equiv > 0:
                rsu = data_point.vested_rsu_gbp_equiv
            elif hasattr(data_point, 'vested_rsu_gbp') and data_point.vested_rsu_gbp > 0:
                rsu = data_point.vested_rsu_gbp
            elif hasattr(data_point, 'vested_rsu_usd') and data_point.vested_rsu_usd > 0:
                rsu = data_point.vested_rsu_usd / 1.26
            else:
                rsu = 0
            
            total_income = salary + bonus + rsu
            total_income_data.append(total_income)
        
        fig.add_trace(go.Scatter(
            name=scenario_name,
            x=years,
            y=total_income_data,
            mode='lines+markers',
            line=dict(color=colors[i % len(colors)]),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Total Income Comparison Across Scenarios",
        xaxis_title="Year",
        yaxis_title="Total Income (£)",
        height=500,
        showlegend=True
    )
    
    return fig


def calculate_multi_scenario_income_summary(scenarios: Dict[str, Any]) -> Dict[str, float]:
    """Calculate summary metrics for multiple scenarios."""
    
    scenario_count = len(scenarios)
    total_incomes = []
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points:
            continue
        
        total_income = 0
        for data_point in scenario.data_points:
            # Salary
            if hasattr(data_point, 'gross_salary_gbp_equiv') and data_point.gross_salary_gbp_equiv > 0:
                salary = data_point.gross_salary_gbp_equiv
            elif hasattr(data_point, 'gross_salary_gbp') and data_point.gross_salary_gbp > 0:
                salary = data_point.gross_salary_gbp
            elif hasattr(data_point, 'gross_salary_usd') and data_point.gross_salary_usd > 0:
                salary = data_point.gross_salary_usd / 1.26
            else:
                salary = 0
            
            # Bonus
            if hasattr(data_point, 'gross_bonus_gbp_equiv') and data_point.gross_bonus_gbp_equiv > 0:
                bonus = data_point.gross_bonus_gbp_equiv
            elif hasattr(data_point, 'gross_bonus_gbp') and data_point.gross_bonus_gbp > 0:
                bonus = data_point.gross_bonus_gbp
            elif hasattr(data_point, 'gross_bonus_usd') and data_point.gross_bonus_usd > 0:
                bonus = data_point.gross_bonus_usd / 1.26
            else:
                bonus = 0
            
            # RSU
            if hasattr(data_point, 'vested_rsu_gbp_equiv') and data_point.vested_rsu_gbp_equiv > 0:
                rsu = data_point.vested_rsu_gbp_equiv
            elif hasattr(data_point, 'vested_rsu_gbp') and data_point.vested_rsu_gbp > 0:
                rsu = data_point.vested_rsu_gbp
            elif hasattr(data_point, 'vested_rsu_usd') and data_point.vested_rsu_usd > 0:
                rsu = data_point.vested_rsu_usd / 1.26
            else:
                rsu = 0
            
            total_income += salary + bonus + rsu
        
        total_incomes.append(total_income)
    
    if not total_incomes:
        return {
            'scenario_count': scenario_count,
            'avg_total_income': 0,
            'income_growth_range': 0
        }
    
    return {
        'scenario_count': scenario_count,
        'avg_total_income': np.mean(total_incomes),
        'income_growth_range': (max(total_incomes) - min(total_incomes)) / max(1, min(total_incomes)) * 100
    }


def render_single_scenario_expense_analysis(scenarios: Dict[str, Any]) -> None:
    """Render single scenario expense analysis."""
    
    scenario_name = list(scenarios.keys())[0]
    scenario = scenarios[scenario_name]
    
    # Create single scenario chart
    with st.spinner("Creating single scenario chart..."):
        fig = create_single_scenario_expense_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"single_expense_{scenario_name}_{uuid.uuid4()}")
    
    # Score cards for single scenario
    st.markdown("### Expense Performance Metrics")
    metrics = calculate_single_scenario_expense_metrics(scenarios)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['total_expenses']:,.0f}</div>
            <div class="metric-label">Total Expenses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['avg_housing']:,.0f}</div>
            <div class="metric-label">Avg Housing</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['avg_taxes']:,.0f}</div>
            <div class="metric-label">Avg Taxes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{metrics['avg_living']:,.0f}</div>
            <div class="metric-label">Avg Living Costs</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed table
    st.markdown("### Detailed Expense Breakdown")
    comparison_df = create_expense_comparison_table(scenarios)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)


def render_comparison_expense_analysis(scenarios: Dict[str, Any]) -> None:
    """Render side-by-side comparison expense analysis."""
    
    scenario_names = list(scenarios.keys())
    scenario_key = "_".join(scenario_names)
    
    # Create side-by-side comparison charts
    with st.spinner("Creating comparison charts..."):
        fig_expense = create_expense_comparison_chart(scenarios)
        st.plotly_chart(fig_expense, use_container_width=True, config={'displayModeBar': True}, key=f"comparison_expense_{scenario_key}_{uuid.uuid4()}")
    
    # Calculate YoY metrics for insights
    yoy_metrics = calculate_yoy_expense_metrics(scenarios)
    
    # Detailed comparison table
    st.markdown("### Detailed Expense Comparison")
    comparison_df = create_expense_comparison_table(scenarios)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Insights
    st.markdown("### Key Insights")
    insights = generate_expense_insights(scenarios, yoy_metrics)
    for insight in insights:
        if insight.startswith("✅"):
            st.success(insight)
        elif insight.startswith("⚠️"):
            st.warning(insight)
        elif insight.startswith("📈"):
            st.info(insight)
        else:
            st.info(insight)


def render_multi_scenario_expense_analysis(scenarios: Dict[str, Any]) -> None:
    """Render multi-scenario expense analysis."""
    
    scenario_names = list(scenarios.keys())
    scenario_key = "_".join(scenario_names[:3])  # Use first 3 scenario names for key
    
    # Create multi-scenario chart
    with st.spinner("Creating multi-scenario chart..."):
        fig = create_multi_scenario_expense_chart(scenarios)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True}, key=f"multi_expense_{scenario_key}_{uuid.uuid4()}")
    
    # Summary metrics
    st.markdown("### Expense Summary Across Scenarios")
    summary_metrics = calculate_multi_scenario_expense_summary(scenarios)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary_metrics['scenario_count']}</div>
            <div class="metric-label">Scenarios Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">£{summary_metrics['avg_total_expenses']:,.0f}</div>
            <div class="metric-label">Avg Total Expenses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{summary_metrics['expense_growth_range']:+.1f}%</div>
            <div class="metric-label">Expense Growth Range</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed table
    st.markdown("### Detailed Expense Comparison")
    comparison_df = create_expense_comparison_table(scenarios)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)


def create_single_scenario_expense_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create a single scenario expense chart."""
    
    scenario_name = list(scenarios.keys())[0]
    scenario = scenarios[scenario_name]
    
    if not scenario.data_points:
        return go.Figure()
    
    years = []
    housing_data = []
    taxes_data = []
    living_data = []
    
    for data_point in scenario.data_points:
        years.append(data_point.year)
        
        # Total expenses
        if hasattr(data_point, 'total_expenses_gbp_equiv') and data_point.total_expenses_gbp_equiv > 0:
            total_expenses = data_point.total_expenses_gbp_equiv
        elif hasattr(data_point, 'total_expenses_gbp') and data_point.total_expenses_gbp > 0:
            total_expenses = data_point.total_expenses_gbp
        elif hasattr(data_point, 'total_expenses_usd') and data_point.total_expenses_usd > 0:
            total_expenses = data_point.total_expenses_usd / 1.26
        else:
            total_expenses = 0
        
        # Taxes
        if hasattr(data_point, 'income_tax_gbp_equiv') and data_point.income_tax_gbp_equiv > 0:
            taxes = data_point.income_tax_gbp_equiv
        elif hasattr(data_point, 'income_tax_gbp') and data_point.income_tax_gbp > 0:
            taxes = data_point.income_tax_gbp
        elif hasattr(data_point, 'income_tax_usd') and data_point.income_tax_usd > 0:
            taxes = data_point.income_tax_usd / 1.26
        else:
            taxes = 0
        
        # Housing (30% of total expenses)
        housing = total_expenses * 0.3
        housing_data.append(housing)
        
        # Taxes
        taxes_data.append(taxes)
        
        # Living costs (70% of remaining expenses)
        living = (total_expenses - taxes) * 0.7
        living_data.append(living)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name="Housing",
        x=years,
        y=housing_data,
        marker_color='#ff7f0e',
        opacity=0.8
    ))
    
    fig.add_trace(go.Bar(
        name="Taxes",
        x=years,
        y=taxes_data,
        marker_color='#d62728',
        opacity=0.8
    ))
    
    fig.add_trace(go.Bar(
        name="Living Costs",
        x=years,
        y=living_data,
        marker_color='#2ca02c',
        opacity=0.8
    ))
    
    fig.update_layout(
        title=f"Expense Breakdown: {scenario_name}",
        xaxis_title="Year",
        yaxis_title="Expenses (£)",
        barmode='stack',
        height=500
    )
    
    return fig


def calculate_single_scenario_expense_metrics(scenarios: Dict[str, Any]) -> Dict[str, float]:
    """Calculate expense metrics for a single scenario."""
    
    scenario_name = list(scenarios.keys())[0]
    scenario = scenarios[scenario_name]
    
    if not scenario.data_points:
        return {
            'total_expenses': 0,
            'avg_housing': 0,
            'avg_taxes': 0,
            'avg_living': 0
        }
    
    total_housing = sum(data_point.total_expenses_gbp * 0.3 if hasattr(data_point, 'total_expenses_gbp') else 0 for data_point in scenario.data_points)
    total_taxes = sum(data_point.income_tax_gbp if hasattr(data_point, 'income_tax_gbp') else 0 for data_point in scenario.data_points)
    total_living = sum((data_point.total_expenses_gbp - data_point.income_tax_gbp) * 0.7 if hasattr(data_point, 'total_expenses_gbp') else 0 for data_point in scenario.data_points)
    
    num_years = len(scenario.data_points)
    
    return {
        'total_expenses': total_housing + total_taxes + total_living,
        'avg_housing': total_housing / num_years if num_years > 0 else 0,
        'avg_taxes': total_taxes / num_years if num_years > 0 else 0,
        'avg_living': total_living / num_years if num_years > 0 else 0
    }


def create_multi_scenario_expense_chart(scenarios: Dict[str, Any]) -> go.Figure:
    """Create a multi-scenario expense comparison chart."""
    
    fig = go.Figure()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    for i, (scenario_name, scenario) in enumerate(scenarios.items()):
        if not scenario.data_points:
            continue
        
        years = []
        total_expense_data = []
        
        for data_point in scenario.data_points:
            years.append(data_point.year)
            
            # Total expenses
            if hasattr(data_point, 'total_expenses_gbp_equiv') and data_point.total_expenses_gbp_equiv > 0:
                expenses = data_point.total_expenses_gbp_equiv
            elif hasattr(data_point, 'total_expenses_gbp') and data_point.total_expenses_gbp > 0:
                expenses = data_point.total_expenses_gbp
            elif hasattr(data_point, 'total_expenses_usd') and data_point.total_expenses_usd > 0:
                expenses = data_point.total_expenses_usd / 1.26
            else:
                expenses = 0
            
            total_expense_data.append(expenses)
        
        fig.add_trace(go.Scatter(
            name=scenario_name,
            x=years,
            y=total_expense_data,
            mode='lines+markers',
            line=dict(color=colors[i % len(colors)]),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Total Expenses Comparison Across Scenarios",
        xaxis_title="Year",
        yaxis_title="Total Expenses (£)",
        height=500,
        showlegend=True
    )
    
    return fig


def calculate_multi_scenario_expense_summary(scenarios: Dict[str, Any]) -> Dict[str, float]:
    """Calculate summary metrics for multiple scenarios."""
    
    scenario_count = len(scenarios)
    total_expenses = []
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points:
            continue
        
        total_expense = sum(
            (data_point.total_expenses_gbp_equiv if hasattr(data_point, 'total_expenses_gbp_equiv') and data_point.total_expenses_gbp_equiv > 0 else 0) +
            (data_point.total_expenses_gbp if hasattr(data_point, 'total_expenses_gbp') and data_point.total_expenses_gbp > 0 else 0) +
            (data_point.total_expenses_usd / 1.26 if hasattr(data_point, 'total_expenses_usd') and data_point.total_expenses_usd > 0 else 0)
            for data_point in scenario.data_points
        )
        total_expenses.append(total_expense)
    
    if not total_expenses:
        return {
            'scenario_count': scenario_count,
            'avg_total_expenses': 0,
            'expense_growth_range': 0
        }
    
    return {
        'scenario_count': scenario_count,
        'avg_total_expenses': np.mean(total_expenses),
        'expense_growth_range': (max(total_expenses) - min(total_expenses)) / max(1, min(total_expenses)) * 100
    }


# Main page function
def main() -> None:
    """Main function for the income and expense breakdown page."""
    render_income_expense_page()


if __name__ == "__main__":
    main() 