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

# Import simplified utilities (expensive metadata functions removed for performance)


def render_time_series_page(scenarios_to_analyze: Optional[Dict[str, UnifiedFinancialScenario]] = None) -> None:
    """
    Render the time series analysis page using unified models with template metadata.

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
        st.markdown("Comprehensive analysis of financial metrics over time across all scenarios with template insights.")

        # Use simplified metadata to avoid expensive operations
        enriched_metadata = {}  # Simplified for performance
        validation_status = {}

        # Render Performance Metrics first (moved to top)
        render_performance_metrics(scenarios_to_analyze, enriched_metadata, validation_status)

        # Render different analysis sections with template metadata
        render_net_worth_analysis(scenarios_to_analyze, enriched_metadata)
        render_income_analysis(scenarios_to_analyze, enriched_metadata)
        render_savings_analysis(scenarios_to_analyze, enriched_metadata)

    except Exception as e:
        st.error(f"Error rendering time series page: {str(e)}")
        st.info("Please refresh the page and try again.")


def get_scenario_template_metadata(scenario_name: str, enriched_metadata: Dict) -> Dict[str, str]:
    """Get simplified template metadata for a scenario to include in tooltips."""
    # Since we're using simplified metadata, create basic metadata from scenario name
    if not enriched_metadata:  # Handle empty metadata
        # Extract basic info from scenario name patterns
        phase_type = "Multi-Phase" if "year" in scenario_name.lower() else "Single-Phase"

        # Determine location/jurisdiction from name
        if "dubai" in scenario_name.lower():
            tax_system = "Tax-Free (UAE)"
            location = "Dubai"
        elif "seattle" in scenario_name.lower() or "new_york" in scenario_name.lower():
            tax_system = "US Federal + State"
            location = "US"
        elif "uk" in scenario_name.lower():
            tax_system = "UK Income Tax + NI"
            location = "UK"
        else:
            tax_system = "Unknown"
            location = "Unknown"

        # Create simplified template summary
        templates_text = f"Location: {location}"
        if "tech" in scenario_name.lower():
            templates_text += ", Profile: Tech Graduate"
        if "local_home" in scenario_name.lower():
            templates_text += ", Housing: Local Purchase"
        elif "uk_home" in scenario_name.lower():
            templates_text += ", Housing: UK Purchase"

        return {
            'Phase': phase_type,
            'Templates': templates_text,
            'Tax System': tax_system
        }

    # Original logic for full metadata (kept for backward compatibility)
    scenario_meta = {}
    for scenario_id, meta in enriched_metadata.items():
        if meta.get('name', scenario_id) == scenario_name:
            scenario_meta = meta
            break

    if not scenario_meta or 'error' in scenario_meta:
        return {'Phase': 'Unknown', 'Templates': 'Unknown', 'Tax System': 'Unknown'}

    # Extract key template information
    phase_type = scenario_meta.get('phase_type', 'Unknown')
    composition = scenario_meta.get('template_composition', {})

    # Create template summary
    template_summary = []
    if composition.get('salary'):
        template_summary.append(f"Salary: {composition['salary']}")
    if composition.get('housing'):
        template_summary.append(f"Housing: {composition['housing']}")
    if composition.get('investments'):
        template_summary.append(f"Investment: {composition['investments']}")

    templates_text = ', '.join(template_summary) if template_summary else 'Unknown'

    return {
        'Phase': phase_type,
        'Templates': templates_text,
        'Tax System': scenario_meta.get('configuration_summary', {}).get('tax_system', 'Unknown')
    }


def render_net_worth_analysis(scenarios: Dict[str, UnifiedFinancialScenario], enriched_metadata: Dict) -> None:
    """Render net worth trajectory analysis with template metadata tooltips."""
    try:
        st.markdown("### 💰 Net Worth Trajectory")
        st.markdown("Track net worth growth over time across all scenarios with template composition details.")

        # Prepare data for plotting with template metadata
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                template_meta = get_scenario_template_metadata(scenario_name, enriched_metadata)

                for i, point in enumerate(scenario.data_points, 1):
                    # Use unified net worth property
                    net_worth = point.net_worth_gbp

                    plot_data.append({
                        'Year': i,
                        'Net Worth': net_worth,
                        'Scenario': scenario_name,
                        'Phase': template_meta['Phase'],
                        'Templates': template_meta['Templates'],
                        'Tax System': template_meta['Tax System'],
                        'Hover Text': f"{scenario_name}<br>Phase: {template_meta['Phase']}<br>Templates: {template_meta['Templates']}<br>Tax: {template_meta['Tax System']}"
                    })

        if plot_data:
            df = pd.DataFrame(plot_data)

            # Create interactive plot with enhanced tooltips
            fig = px.line(
                df,
                x='Year',
                y='Net Worth',
                color='Scenario',
                title='Net Worth Trajectory Over Time (Template-Enhanced)',
                labels={'Net Worth': 'Net Worth (£)', 'Year': 'Year'},
                hover_data={
                    'Phase': True,
                    'Templates': True,
                    'Tax System': True,
                    'Net Worth': ':,.0f'
                }
            )

            # Customize hover template to include template information
            fig.update_traces(
                hovertemplate="<b>%{fullData.name}</b><br>" +
                             "Year: %{x}<br>" +
                             "Net Worth: £%{y:,.0f}<br>" +
                             "Phase: %{customdata[0]}<br>" +
                             "Templates: %{customdata[1]}<br>" +
                             "Tax System: %{customdata[2]}<br>" +
                             "<extra></extra>",
                customdata=df[['Phase', 'Templates', 'Tax System']].values
            )

            fig.update_layout(
                height=600,
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # Template composition legend
            with st.expander("🧩 Template Composition Legend", expanded=False):
                unique_scenarios = df['Scenario'].unique()
                for scenario in unique_scenarios:
                    scenario_data = df[df['Scenario'] == scenario].iloc[0]
                    st.markdown(f"**{scenario}**")
                    st.markdown(f"• Phase: {scenario_data['Phase']}")
                    st.markdown(f"• Templates: {scenario_data['Templates']}")
                    st.markdown(f"• Tax System: {scenario_data['Tax System']}")
                    st.markdown("---")
        else:
            st.warning("No data available for net worth analysis.")

    except Exception as e:
        st.error(f"Error rendering net worth analysis: {str(e)}")


def render_income_analysis(scenarios: Dict[str, UnifiedFinancialScenario], enriched_metadata: Dict) -> None:
    """Render income breakdown analysis by scenario with component details."""
    try:
        st.markdown("### 💼 Income Breakdown Analysis")
        st.markdown("Analyze income components (salary, bonus, RSU) across different scenarios over time.")

        # Prepare comprehensive income data
        plot_data = []
        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                template_meta = get_scenario_template_metadata(scenario_name, enriched_metadata)

                for i, point in enumerate(scenario.data_points, 1):
                    # Extract individual income components
                    salary = point.income.salary.gbp_value
                    bonus = point.income.bonus.gbp_value
                    rsu_vested = point.income.rsu_vested.gbp_value
                    other_income = point.income.other_income.gbp_value
                    total_income = point.income.total_gbp

                    plot_data.append({
                        'Year': i,
                        'Scenario': scenario_name,
                        'Salary': salary,
                        'Bonus': bonus,
                        'RSU Vested': rsu_vested,
                        'Other Income': other_income,
                        'Total Income': total_income,
                        'Phase': template_meta['Phase'],
                        'Location': template_meta['Templates'].split('Location: ')[1].split(',')[0] if 'Location: ' in template_meta['Templates'] else 'Unknown'
                    })

        if plot_data:
            df = pd.DataFrame(plot_data)

            # Create tabs for different views
            tab1, tab2 = st.tabs(["📈 Total Income Trajectory", "🧩 Income Components Breakdown"])

            with tab1:
                # Total income trajectory by scenario
                fig_total = px.line(
                    df,
                    x='Year',
                    y='Total Income',
                    color='Scenario',
                    title='Total Income Trajectory by Scenario',
                    labels={'Total Income': 'Total Income (£)', 'Year': 'Year'},
                    hover_data={
                        'Phase': True,
                        'Location': True,
                        'Total Income': ':,.0f'
                    }
                )

                fig_total.update_traces(
                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                 "Year: %{x}<br>" +
                                 "Total Income: £%{y:,.0f}<br>" +
                                 "Phase: %{customdata[0]}<br>" +
                                 "Location: %{customdata[1]}<br>" +
                                 "<extra></extra>",
                    customdata=df[['Phase', 'Location']].values
                )

                fig_total.update_layout(height=500)
                st.plotly_chart(fig_total, use_container_width=True)

            with tab2:
                # Income components breakdown
                # Melt the dataframe to show income components
                df_melted = df.melt(
                    id_vars=['Year', 'Scenario', 'Phase', 'Location'],
                    value_vars=['Salary', 'Bonus', 'RSU Vested', 'Other Income'],
                    var_name='Income Component',
                    value_name='Amount'
                )

                # Create stacked bar chart for income components
                fig_components = px.bar(
                    df_melted,
                    x='Year',
                    y='Amount',
                    color='Income Component',
                    facet_col='Scenario',
                    facet_col_wrap=2,
                    title='Income Components Breakdown by Scenario',
                    labels={'Amount': 'Income (£)', 'Year': 'Year'},
                    hover_data={'Amount': ':,.0f'}
                )

                fig_components.update_traces(
                    hovertemplate="<b>%{fullData.name}</b><br>" +
                                 "Year: %{x}<br>" +
                                 "Amount: £%{y:,.0f}<br>" +
                                 "<extra></extra>"
                )

                fig_components.update_layout(height=600)
                st.plotly_chart(fig_components, use_container_width=True)

            # Scenario-based income analysis
            with st.expander("📊 Income Analysis by Scenario", expanded=False):
                # Calculate summary statistics for each scenario
                scenario_summary = df.groupby(['Scenario', 'Location', 'Phase']).agg({
                    'Salary': ['mean', 'max'],
                    'Bonus': ['mean', 'max'],
                    'RSU Vested': ['mean', 'max'],
                    'Total Income': ['mean', 'max']
                }).round(0)

                scenario_summary.columns = [f'{col[1].title()} {col[0].replace("_", " ").title()}' for col in scenario_summary.columns]
                st.dataframe(scenario_summary, use_container_width=True)

                # Show income composition percentages
                st.markdown("**Average Income Composition by Scenario:**")
                for scenario in df['Scenario'].unique():
                    scenario_data = df[df['Scenario'] == scenario]
                    avg_salary = scenario_data['Salary'].mean()
                    avg_bonus = scenario_data['Bonus'].mean()
                    avg_rsu = scenario_data['RSU Vested'].mean()
                    avg_other = scenario_data['Other Income'].mean()
                    avg_total = scenario_data['Total Income'].mean()

                    if avg_total > 0:
                        st.markdown(f"**{scenario}:**")
                        st.markdown(f"• Salary: {(avg_salary/avg_total)*100:.1f}% (£{avg_salary:,.0f})")
                        st.markdown(f"• Bonus: {(avg_bonus/avg_total)*100:.1f}% (£{avg_bonus:,.0f})")
                        st.markdown(f"• RSU: {(avg_rsu/avg_total)*100:.1f}% (£{avg_rsu:,.0f})")
                        if avg_other > 0:
                            st.markdown(f"• Other: {(avg_other/avg_total)*100:.1f}% (£{avg_other:,.0f})")
                        st.markdown("---")
        else:
            st.warning("No data available for income analysis.")

    except Exception as e:
        st.error(f"Error rendering income analysis: {str(e)}")


def render_savings_analysis(scenarios: Dict[str, UnifiedFinancialScenario], enriched_metadata: Dict) -> None:
    """Render savings analysis with investment template insights and scenario filtering."""
    try:
        st.markdown("### 💰 Savings & Investment Analysis")
        st.markdown("Track savings patterns and investment strategies for individual scenarios.")

        # Add scenario filter on the page
        if not scenarios:
            st.warning("No scenarios available for savings analysis.")
            return

        scenario_names = list(scenarios.keys())

        # Create columns for the filter
        col1, col2 = st.columns([2, 1])

        with col1:
            selected_scenario = st.selectbox(
                "Select scenario to analyze:",
                options=scenario_names,
                index=0,
                help="Choose which scenario to display in the savings analysis"
            )

        with col2:
            st.metric("Available Scenarios", len(scenario_names))

        # Filter to only the selected scenario
        filtered_scenarios = {selected_scenario: scenarios[selected_scenario]}

        plot_data = []
        for scenario_name, scenario in filtered_scenarios.items():
            if scenario.data_points:
                template_meta = get_scenario_template_metadata(scenario_name, enriched_metadata)

                for i, point in enumerate(scenario.data_points, 1):
                    # Calculate annual savings (net income - expenses)
                    net_income = point.income.total_gbp - point.tax.total_gbp
                    annual_savings = net_income - point.expenses.total_gbp

                    investment_template = 'Unknown'
                    if 'Investment: ' in template_meta['Templates']:
                        investment_template = template_meta['Templates'].split('Investment: ')[1].split(',')[0]

                    plot_data.append({
                        'Year': i,
                        'Annual Savings': annual_savings,
                        'Scenario': scenario_name,
                        'Phase': template_meta['Phase'],
                        'Investment Template': investment_template,
                        'Tax System': template_meta['Tax System']
                    })

        if plot_data:
            df = pd.DataFrame(plot_data)

            # Create savings analysis chart for selected scenario
            fig = px.bar(
                df,
                x='Year',
                y='Annual Savings',
                title=f'Annual Savings Analysis - {selected_scenario}',
                labels={'Annual Savings': 'Annual Savings (£)', 'Year': 'Year'},
                hover_data={
                    'Phase': True,
                    'Investment Template': True,
                    'Tax System': True,
                    'Annual Savings': ':,.0f'
                },
                color_discrete_sequence=['#1f77b4']  # Single color since it's one scenario
            )

            # Enhanced hover template
            fig.update_traces(
                hovertemplate="<b>" + selected_scenario + "</b><br>" +
                             "Year: %{x}<br>" +
                             "Savings: £%{y:,.0f}<br>" +
                             "Phase: %{customdata[0]}<br>" +
                             "Investment: %{customdata[1]}<br>" +
                             "Tax System: %{customdata[2]}<br>" +
                             "<extra></extra>",
                customdata=df[['Phase', 'Investment Template', 'Tax System']].values
            )

            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

            # Scenario details and savings insights
            with st.expander(f"🎯 Savings Details for {selected_scenario}", expanded=False):
                # Calculate key metrics for the selected scenario
                total_savings = df['Annual Savings'].sum()
                avg_savings = df['Annual Savings'].mean()
                max_savings = df['Annual Savings'].max()
                min_savings = df['Annual Savings'].min()

                # Display key metrics
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Savings", format_currency(total_savings))

                with col2:
                    st.metric("Average Annual", format_currency(avg_savings))

                with col3:
                    st.metric("Best Year", format_currency(max_savings))

                with col4:
                    st.metric("Worst Year", format_currency(min_savings))

                # Show scenario details
                st.markdown("**Scenario Configuration:**")
                if not df.empty:
                    phase = df['Phase'].iloc[0]
                    investment_template = df['Investment Template'].iloc[0]
                    tax_system = df['Tax System'].iloc[0]

                    st.markdown(f"• **Phase Type**: {phase}")
                    st.markdown(f"• **Investment Strategy**: {investment_template}")
                    st.markdown(f"• **Tax System**: {tax_system}")

                # Year-by-year breakdown
                st.markdown("**Year-by-Year Savings:**")
                yearly_data = df[['Year', 'Annual Savings']].copy()
                yearly_data['Annual Savings'] = yearly_data['Annual Savings'].apply(format_currency)
                st.dataframe(yearly_data, use_container_width=True)
        else:
            st.warning("No data available for savings analysis.")

    except Exception as e:
        st.error(f"Error rendering savings analysis: {str(e)}")


def render_performance_metrics(scenarios: Dict[str, UnifiedFinancialScenario], enriched_metadata: Dict, validation_status: Dict) -> None:
    """Render performance metrics with template validation insights."""
    try:
        st.markdown("### 📊 Template-Enhanced Performance Metrics")

        if not scenarios:
            st.warning("No scenarios available for analysis.")
            return

        # Calculate template-aware metrics
        total_scenarios = len(scenarios)

        # Count valid scenarios
        valid_scenarios = 0
        for scenario_name in scenarios.keys():
            for scenario_id, meta in enriched_metadata.items():
                if meta.get('name', scenario_id) == scenario_name:
                    if validation_status.get(scenario_id, {}).get('valid', False):
                        valid_scenarios += 1
                    break

        # Template composition analysis
        template_types = {}
        phase_types = {}

        for scenario_name in scenarios.keys():
            for scenario_id, meta in enriched_metadata.items():
                if meta.get('name', scenario_id) == scenario_name and 'error' not in meta:
                    # Count template types
                    for template_type in meta.get('template_types', []):
                        template_types[template_type] = template_types.get(template_type, 0) + 1

                    # Count phase types
                    phase = meta.get('phase_type', 'Unknown')
                    phase_types[phase] = phase_types.get(phase, 0) + 1
                    break

        # Display metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Scenarios", total_scenarios)

        with col2:
            st.metric("Valid Templates", valid_scenarios)

        with col3:
            st.metric("Template Types", len(template_types))

        with col4:
            validation_rate = (valid_scenarios / max(total_scenarios, 1)) * 100
            st.metric("Validation Rate", f"{validation_rate:.0f}%")

        # Template composition breakdown
        if template_types or phase_types:
            with st.expander("🧩 Template Composition Breakdown", expanded=False):
                col1, col2 = st.columns(2)

                with col1:
                    if template_types:
                        st.markdown("**Template Types:**")
                        for template_type, count in template_types.items():
                            st.markdown(f"• {template_type.replace('_', ' ').title()}: {count}")

                with col2:
                    if phase_types:
                        st.markdown("**Phase Types:**")
                        for phase_type, count in phase_types.items():
                            st.markdown(f"• {phase_type}: {count}")

    except Exception as e:
        st.error(f"Error rendering performance metrics: {str(e)}")


def main() -> None:
    """Main function to render the time series analysis page."""
    render_time_series_page()


if __name__ == "__main__":
    main()
