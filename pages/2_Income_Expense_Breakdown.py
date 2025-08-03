"""
Income and Expense Breakdown Analysis Page
Detailed breakdown of income sources, expense categories, and tax calculations using unified models.
Enhanced with template insights, calculation explanations, and parameter sensitivity analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional
import numpy as np

# Import utilities
from utils.validation import validate_scenario_data, safe_divide, validate_dataframe
from utils.formatting import format_currency, format_percentage, format_number, extract_numeric_from_currency
from utils.css_loader import load_component_styles
from constants import ERROR_MESSAGES, SUCCESS_MESSAGES

# Import unified models
from models.unified_financial_data import UnifiedFinancialScenario

# Import simplified utilities (expensive metadata functions removed for performance)


def render_income_expense_page(scenarios_to_analyze: Optional[Dict[str, UnifiedFinancialScenario]] = None) -> None:
    """
    Render the income and expense breakdown page using unified models with template insights.

    Args:
        scenarios_to_analyze: Dictionary of scenarios to analyze with unified structure (optional)
    """
    try:
        # Load component styles
        load_component_styles()

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

        # Use simplified metadata to avoid expensive operations
        enriched_metadata = {}  # Simplified for performance
        validation_status = {}
        config_summary = {}

        st.markdown("## 💰 Income & Expense Breakdown Analysis")
        st.markdown("Detailed analysis of income sources, expense categories, and tax calculations with template-driven insights.")

        # Template System Overview
        render_template_system_overview(scenarios_to_analyze, enriched_metadata, validation_status)

        # Render different analysis sections with template insights
        render_income_breakdown_analysis(scenarios_to_analyze, enriched_metadata, config_summary)
        render_expense_breakdown_analysis(scenarios_to_analyze, enriched_metadata, config_summary)
        render_tax_analysis(scenarios_to_analyze, enriched_metadata, config_summary)
        render_template_parameter_sensitivity(scenarios_to_analyze, enriched_metadata, config_summary)

    except Exception as e:
        st.error(f"Error rendering income expense page: {str(e)}")
        st.info("Please refresh the page and try again.")


def render_template_system_overview(scenarios: Dict[str, UnifiedFinancialScenario],
                                   enriched_metadata: Dict, validation_status: Dict) -> None:
    """Render template system overview with validation insights."""
    try:
        st.markdown("### 🔧 Template System Overview")

        if not scenarios:
            st.warning("No scenarios available for template analysis.")
            return

        # Template composition analysis
        template_compositions = {}
        validation_issues = []

        for scenario_name in scenarios.keys():
            for scenario_id, meta in enriched_metadata.items():
                if meta.get('name', scenario_id) == scenario_name:
                    if 'error' not in meta:
                        composition = meta.get('template_composition', {})
                        for template_type, template_name in composition.items():
                            if template_type not in template_compositions:
                                template_compositions[template_type] = {}
                            template_compositions[template_type][template_name] = template_compositions[template_type].get(template_name, 0) + 1

                    # Check validation status
                    if not validation_status.get(scenario_id, {}).get('valid', False):
                        validation_issues.append({
                            'scenario': scenario_name,
                            'issue': validation_status.get(scenario_id, {}).get('message', 'Unknown validation issue')
                        })
                    break

        # Display template composition
        if template_compositions:
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📋 Template Distribution")
                for template_type, templates in template_compositions.items():
                    st.markdown(f"**{template_type.replace('_', ' ').title()}:**")
                    for template_name, count in templates.items():
                        st.markdown(f"• {template_name}: {count} scenario(s)")

            with col2:
                st.markdown("#### ✅ Validation Status")
                total_scenarios = len(scenarios)
                valid_scenarios = total_scenarios - len(validation_issues)

                st.metric("Total Scenarios", total_scenarios)
                st.metric("Valid Scenarios", valid_scenarios)

                if validation_issues:
                    with st.expander("⚠️ Validation Issues", expanded=False):
                        for issue in validation_issues:
                            st.markdown(f"• **{issue['scenario']}**: {issue['issue']}")

        # Template calculation explanations
        with st.expander("🧮 Template Calculation Methods", expanded=False):
            st.markdown("### How Templates Drive Calculations")
            st.markdown("**Salary Templates**: Define progression patterns, bonuses, RSU schedules")
            st.markdown("**Housing Templates**: Calculate mortgage payments, property appreciation, costs")
            st.markdown("**Investment Templates**: Determine allocation strategies and growth rates")
            st.markdown("**Tax Templates**: Apply jurisdiction-specific tax rules and calculations")
            st.markdown("**Life Event Templates**: Model major life changes and their financial impact")

    except Exception as e:
        st.error(f"Error rendering template system overview: {str(e)}")


def render_income_breakdown_analysis(scenarios: Dict[str, UnifiedFinancialScenario],
                                   enriched_metadata: Dict, config_summary: Dict) -> None:
    """Render detailed income breakdown analysis with template insights."""
    try:
        st.markdown("### 💼 Income Breakdown Analysis")
        st.markdown("Detailed analysis of income sources and their template-driven calculations.")

        # Prepare income data with template context
        income_data = []
        template_insights = {}

        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                # Get template metadata
                template_meta = _get_scenario_template_info(scenario_name, enriched_metadata)
                config_info = config_summary.get(scenario_name, {})

                # Store template insights
                template_insights[scenario_name] = {
                    'salary_template': template_meta.get('salary', 'Unknown'),
                    'progression_type': config_info.get('key_parameters', {}).get('salary_progression', 'Unknown'),
                    'bonus_structure': config_info.get('key_parameters', {}).get('bonus_structure', 'Unknown'),
                    'rsu_schedule': config_info.get('key_parameters', {}).get('rsu_schedule', 'Unknown')
                }

                for i, point in enumerate(scenario.data_points, 1):
                    income_breakdown = point.income

                    income_data.append({
                        'Year': i,
                        'Scenario': scenario_name,
                        'Base Salary': income_breakdown.base_salary.gbp_value,
                        'Bonus': income_breakdown.bonus.gbp_value,
                        'RSU Vested': income_breakdown.rsu_vested.gbp_value,
                        'Other Income': income_breakdown.other_income.gbp_value,
                        'Total Income': income_breakdown.total_gbp,
                        'Salary Template': template_meta.get('salary', 'Unknown'),
                        'Phase': template_meta.get('phase', 'Unknown')
                    })

        if income_data:
            df = pd.DataFrame(income_data)

            # Income composition charts
            col1, col2 = st.columns(2)

            with col1:
                # Stacked area chart for income components
                fig = go.Figure()

                scenarios = df['Scenario'].unique()
                for scenario in scenarios:
                    scenario_data = df[df['Scenario'] == scenario]

                    fig.add_trace(go.Scatter(
                    x=scenario_data['Year'],
                        y=scenario_data['Base Salary'],
                        stackgroup='one',
                        name=f'{scenario} - Base Salary',
                        hovertemplate=f"<b>{scenario}</b><br>Year: %{{x}}<br>Base Salary: £%{{y:,.0f}}<extra></extra>"
                    ))

                    fig.add_trace(go.Scatter(
                    x=scenario_data['Year'],
                        y=scenario_data['Bonus'],
                        stackgroup='one',
                        name=f'{scenario} - Bonus',
                        hovertemplate=f"<b>{scenario}</b><br>Year: %{{x}}<br>Bonus: £%{{y:,.0f}}<extra></extra>"
                    ))

                    fig.add_trace(go.Scatter(
                    x=scenario_data['Year'],
                        y=scenario_data['RSU Vested'],
                        stackgroup='one',
                        name=f'{scenario} - RSU',
                        hovertemplate=f"<b>{scenario}</b><br>Year: %{{x}}<br>RSU: £%{{y:,.0f}}<extra></extra>"
                    ))

        fig.update_layout(
                    title="Income Components Over Time",
                    xaxis_title="Year",
                    yaxis_title="Income (£)",
                    height=400
                )

            st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Income growth rate analysis
                growth_data = []
                for scenario in df['Scenario'].unique():
                    scenario_data = df[df['Scenario'] == scenario].sort_values('Year')
                    if len(scenario_data) > 1:
                        for i in range(1, len(scenario_data)):
                            prev_income = scenario_data.iloc[i-1]['Total Income']
                            curr_income = scenario_data.iloc[i]['Total Income']
                            growth_rate = ((curr_income - prev_income) / prev_income) * 100 if prev_income > 0 else 0

                            growth_data.append({
                                'Year': scenario_data.iloc[i]['Year'],
                                'Scenario': scenario,
                                'Growth Rate': growth_rate,
                                'Salary Template': scenario_data.iloc[i]['Salary Template']
                            })

                if growth_data:
                    growth_df = pd.DataFrame(growth_data)
                    fig = px.line(
                        growth_df,
                        x='Year',
                        y='Growth Rate',
                        color='Scenario',
                        title='Income Growth Rate by Template',
                        labels={'Growth Rate': 'Growth Rate (%)'},
                        hover_data=['Salary Template']
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

            # Template-driven income insights
            with st.expander("🔍 Template-Driven Income Insights", expanded=False):
                for scenario_name, insights in template_insights.items():
                    st.markdown(f"**{scenario_name}**")
                    st.markdown(f"• Salary Template: {insights['salary_template']}")
                    st.markdown(f"• Progression Type: {insights['progression_type']}")
                    st.markdown(f"• Bonus Structure: {insights['bonus_structure']}")
                    st.markdown(f"• RSU Schedule: {insights['rsu_schedule']}")

                    # Calculate scenario-specific metrics
                    scenario_data = df[df['Scenario'] == scenario_name]
                    if not scenario_data.empty:
                        avg_growth = scenario_data['Total Income'].pct_change().mean() * 100
                        total_rsu = scenario_data['RSU Vested'].sum()
                        total_bonus = scenario_data['Bonus'].sum()

                        st.markdown(f"• Average Annual Growth: {avg_growth:.1f}%")
                        st.markdown(f"• Total RSU Value: £{total_rsu:,.0f}")
                        st.markdown(f"• Total Bonus Value: £{total_bonus:,.0f}")
                    st.markdown("---")
        else:
            st.warning("No income data available for analysis.")

    except Exception as e:
        st.error(f"Error rendering income breakdown analysis: {str(e)}")


def render_expense_breakdown_analysis(scenarios: Dict[str, UnifiedFinancialScenario],
                                    enriched_metadata: Dict, config_summary: Dict) -> None:
    """Render detailed expense breakdown analysis with template insights."""
    try:
        st.markdown("### 🏠 Expense Breakdown Analysis")
        st.markdown("Detailed analysis of expense categories and their template-driven calculations.")

        # Prepare expense data with template context
        expense_data = []
        housing_insights = {}

        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                template_meta = _get_scenario_template_info(scenario_name, enriched_metadata)
                config_info = config_summary.get(scenario_name, {})

                # Store housing template insights
                housing_insights[scenario_name] = {
                    'housing_template': template_meta.get('housing', 'Unknown'),
                    'housing_strategy': config_info.get('key_parameters', {}).get('housing_strategy', 'Unknown'),
                    'location': config_info.get('key_parameters', {}).get('location', 'Unknown')
                }

                for i, point in enumerate(scenario.data_points, 1):
                    expenses = point.expenses

                    expense_data.append({
                        'Year': i,
                        'Scenario': scenario_name,
                        'Housing': expenses.housing.gbp_value,
                        'Living': expenses.living.gbp_value,
                        'Transportation': expenses.transportation.gbp_value,
                        'Healthcare': expenses.healthcare.gbp_value,
                        'Other': expenses.other.gbp_value,
                        'Total Expenses': expenses.total_gbp,
                        'Housing Template': template_meta.get('housing', 'Unknown'),
                        'Phase': template_meta.get('phase', 'Unknown')
                    })

        if expense_data:
            df = pd.DataFrame(expense_data)

            # Expense composition analysis
            col1, col2 = st.columns(2)

            with col1:
                # Expense composition pie chart for latest year
                latest_year = df['Year'].max()
                latest_data = df[df['Year'] == latest_year]

                expense_categories = ['Housing', 'Living', 'Transportation', 'Healthcare', 'Other']
                avg_expenses = {cat: latest_data[cat].mean() for cat in expense_categories}

                fig = px.pie(
                    values=list(avg_expenses.values()),
                    names=list(avg_expenses.keys()),
                    title=f"Average Expense Composition (Year {latest_year})"
                )
                fig.update_traces(
                    hovertemplate="<b>%{label}</b><br>Amount: £%{value:,.0f}<br>Percentage: %{percent}<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Housing costs by template
                housing_by_template = df.groupby(['Housing Template', 'Year'])['Housing'].mean().reset_index()

                fig = px.line(
                    housing_by_template,
                    x='Year',
                    y='Housing',
                    color='Housing Template',
                    title='Housing Costs by Template',
                    labels={'Housing': 'Housing Costs (£)'}
                )
                fig.update_traces(
                    hovertemplate="<b>%{fullData.name}</b><br>Year: %{x}<br>Housing: £%{y:,.0f}<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)

            # Expense efficiency analysis
            st.markdown("#### 📈 Expense Efficiency Analysis")

            # Calculate expense ratios
            expense_ratios = []
            for scenario_name, scenario in scenarios.items():
                if scenario.data_points:
                    for i, point in enumerate(scenario.data_points, 1):
                        total_income = point.income.total_gbp
                        total_expenses = point.expenses.total_gbp
                        housing_ratio = (point.expenses.housing.gbp_value / total_income) * 100 if total_income > 0 else 0

                        expense_ratios.append({
                            'Year': i,
                            'Scenario': scenario_name,
                            'Housing Ratio': housing_ratio,
                            'Total Expense Ratio': (total_expenses / total_income) * 100 if total_income > 0 else 0,
                            'Housing Template': housing_insights[scenario_name]['housing_template']
                        })

            if expense_ratios:
                ratio_df = pd.DataFrame(expense_ratios)

                fig = px.scatter(
                    ratio_df,
                    x='Housing Ratio',
                    y='Total Expense Ratio',
                    color='Scenario',
                    size='Year',
                    title='Expense Efficiency: Housing vs Total Expense Ratios',
                    labels={
                        'Housing Ratio': 'Housing Ratio (% of Income)',
                        'Total Expense Ratio': 'Total Expense Ratio (% of Income)'
                    },
                    hover_data=['Year', 'Housing Template']
                )

                # Add reference lines
                fig.add_hline(y=50, line_dash="dash", line_color="red",
                             annotation_text="50% Expense Threshold")
                fig.add_vline(x=30, line_dash="dash", line_color="orange",
                             annotation_text="30% Housing Threshold")

                st.plotly_chart(fig, use_container_width=True)

            # Housing template insights
            with st.expander("🏠 Housing Template Insights", expanded=False):
                for scenario_name, insights in housing_insights.items():
                    st.markdown(f"**{scenario_name}**")
                    st.markdown(f"• Housing Template: {insights['housing_template']}")
                    st.markdown(f"• Housing Strategy: {insights['housing_strategy']}")
                    st.markdown(f"• Location: {insights['location']}")

                    # Calculate housing-specific metrics
                    scenario_data = df[df['Scenario'] == scenario_name]
                    if not scenario_data.empty:
                        avg_housing = scenario_data['Housing'].mean()
                        housing_growth = scenario_data['Housing'].pct_change().mean() * 100

                        st.markdown(f"• Average Annual Housing Cost: £{avg_housing:,.0f}")
                        st.markdown(f"• Average Housing Cost Growth: {housing_growth:.1f}%")
                    st.markdown("---")
        else:
            st.warning("No expense data available for analysis.")

    except Exception as e:
        st.error(f"Error rendering expense breakdown analysis: {str(e)}")


def render_tax_analysis(scenarios: Dict[str, UnifiedFinancialScenario],
                       enriched_metadata: Dict, config_summary: Dict) -> None:
    """Render detailed tax analysis with template insights."""
    try:
        st.markdown("### 🧾 Tax Analysis")
        st.markdown("Comprehensive tax analysis across different jurisdictions and template configurations.")

        # Prepare tax data with template context
        tax_data = []
        tax_insights = {}

        for scenario_name, scenario in scenarios.items():
            if scenario.data_points:
                template_meta = _get_scenario_template_info(scenario_name, enriched_metadata)
                config_info = config_summary.get(scenario_name, {})

                # Store tax system insights
                tax_insights[scenario_name] = {
                    'tax_system': config_info.get('tax_system', 'Unknown'),
                    'jurisdiction': template_meta.get('jurisdiction', 'Unknown'),
                    'location': config_info.get('key_parameters', {}).get('location', 'Unknown')
                }

                for i, point in enumerate(scenario.data_points, 1):
                    tax_breakdown = point.tax
                    total_income = point.income.total_gbp

                    effective_rate = (tax_breakdown.total_gbp / total_income) * 100 if total_income > 0 else 0

                    tax_data.append({
                        'Year': i,
                        'Scenario': scenario_name,
                        'Income Tax': tax_breakdown.income_tax.gbp_value,
                        'Social Security': tax_breakdown.social_security.gbp_value,
                        'Other Tax': tax_breakdown.other_tax.gbp_value,
                        'Total Tax': tax_breakdown.total_gbp,
                        'Total Income': total_income,
                        'Effective Tax Rate': effective_rate,
                        'Tax System': tax_insights[scenario_name]['tax_system'],
                        'Jurisdiction': tax_insights[scenario_name]['jurisdiction']
                    })

        if tax_data:
            df = pd.DataFrame(tax_data)

            # Tax analysis charts
            col1, col2 = st.columns(2)

            with col1:
                # Effective tax rates by jurisdiction
                fig = px.box(
                    df,
                    x='Jurisdiction',
                    y='Effective Tax Rate',
                    color='Tax System',
                    title='Effective Tax Rates by Jurisdiction',
                    labels={'Effective Tax Rate': 'Effective Tax Rate (%)'}
                )
                fig.update_traces(
                    hovertemplate="<b>%{fullData.name}</b><br>Jurisdiction: %{x}<br>Tax Rate: %{y:.1f}%<extra></extra>"
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Tax burden over time
                fig = px.line(
                    df,
                    x='Year',
                    y='Total Tax',
                    color='Scenario',
                    title='Tax Burden Over Time',
                    labels={'Total Tax': 'Total Tax (£)'},
                    hover_data=['Tax System', 'Effective Tax Rate']
                )
                st.plotly_chart(fig, use_container_width=True)

            # Tax efficiency comparison
            st.markdown("#### ⚖️ Tax Efficiency Comparison")

            # Calculate tax efficiency metrics
            tax_efficiency = df.groupby(['Tax System', 'Jurisdiction']).agg({
                'Effective Tax Rate': ['mean', 'std'],
                'Total Tax': 'sum',
                'Total Income': 'sum'
            }).round(2)

            tax_efficiency.columns = ['Avg Tax Rate (%)', 'Tax Rate Std (%)', 'Total Tax (£)', 'Total Income (£)']
            tax_efficiency['Tax Efficiency Score'] = (
                100 - tax_efficiency['Avg Tax Rate (%)'] +
                (10 / (tax_efficiency['Tax Rate Std (%)'] + 1))
            ).round(1)

            st.dataframe(tax_efficiency, use_container_width=True)

            # Tax system insights
            with st.expander("🌍 Tax System Insights", expanded=False):
                for scenario_name, insights in tax_insights.items():
                    st.markdown(f"**{scenario_name}**")
                    st.markdown(f"• Tax System: {insights['tax_system']}")
                    st.markdown(f"• Jurisdiction: {insights['jurisdiction']}")
                    st.markdown(f"• Location: {insights['location']}")

                    # Calculate tax-specific metrics
                    scenario_data = df[df['Scenario'] == scenario_name]
                    if not scenario_data.empty:
                        avg_rate = scenario_data['Effective Tax Rate'].mean()
                        total_tax = scenario_data['Total Tax'].sum()

                        st.markdown(f"• Average Effective Rate: {avg_rate:.1f}%")
                        st.markdown(f"• Total Tax Burden: £{total_tax:,.0f}")
                    st.markdown("---")
        else:
            st.warning("No tax data available for analysis.")

    except Exception as e:
        st.error(f"Error rendering tax analysis: {str(e)}")


def render_template_parameter_sensitivity(scenarios: Dict[str, UnifiedFinancialScenario],
                                        enriched_metadata: Dict, config_summary: Dict) -> None:
    """Render template parameter sensitivity analysis."""
    try:
        st.markdown("### 🎚️ Template Parameter Sensitivity Analysis")
        st.markdown("Analyze how different template parameters affect financial outcomes.")

        if not scenarios:
            st.warning("No scenarios available for sensitivity analysis.")
            return

        # Extract parameter variations
        parameter_variations = {}
        outcome_metrics = {}

        for scenario_name, scenario in scenarios.items():
            config_info = config_summary.get(scenario_name, {})
            key_params = config_info.get('key_parameters', {})

            # Store parameters for comparison
            parameter_variations[scenario_name] = key_params

            # Calculate outcome metrics
            if scenario.data_points:
                final_net_worth = scenario.get_final_net_worth_gbp()
                avg_savings = scenario.get_average_annual_savings_gbp()
                total_tax = sum(point.tax.total_gbp for point in scenario.data_points)

                outcome_metrics[scenario_name] = {
                    'Final Net Worth': final_net_worth,
                    'Average Savings': avg_savings,
                    'Total Tax': total_tax
                }

        if parameter_variations and outcome_metrics:
            # Create parameter comparison
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📊 Parameter Impact Analysis")

                # Find common parameters across scenarios
                all_params = set()
                for params in parameter_variations.values():
                    all_params.update(params.keys())

                # Show parameter distribution
                for param in sorted(all_params):
                    param_values = {}
                    for scenario, params in parameter_variations.items():
                        if param in params:
                            value = params[param]
                            if isinstance(value, (int, float)):
                                param_values[scenario] = value

                    if len(param_values) > 1 and len(set(param_values.values())) > 1:
                        st.markdown(f"**{param.replace('_', ' ').title()}:**")
                        for scenario, value in param_values.items():
                            net_worth = outcome_metrics[scenario]['Final Net Worth']
                            st.markdown(f"• {scenario}: {value} → £{net_worth:,.0f} net worth")

            with col2:
                st.markdown("#### 🎯 Outcome Sensitivity")

                # Create sensitivity matrix
                sensitivity_data = []
                for scenario, metrics in outcome_metrics.items():
                    params = parameter_variations[scenario]

                    sensitivity_data.append({
                        'Scenario': scenario,
                        'Net Worth': metrics['Final Net Worth'],
                        'Avg Savings': metrics['Average Savings'],
                        'Tax Burden': metrics['Total Tax'],
                        'Location': params.get('location', 'Unknown'),
                        'Salary Template': params.get('salary_progression', 'Unknown')
                    })

                if sensitivity_data:
                    sens_df = pd.DataFrame(sensitivity_data)

                    # Correlation analysis
                    st.markdown("**Key Insights:**")

                    # Find scenarios with highest/lowest outcomes
                    best_nw = sens_df.loc[sens_df['Net Worth'].idxmax()]
                    worst_nw = sens_df.loc[sens_df['Net Worth'].idxmin()]

                    st.markdown(f"• **Best Net Worth**: {best_nw['Scenario']} (£{best_nw['Net Worth']:,.0f})")
                    st.markdown(f"• **Location**: {best_nw['Location']}")
                    st.markdown(f"• **Salary Template**: {best_nw['Salary Template']}")
                    st.markdown("")
                    st.markdown(f"• **Lowest Net Worth**: {worst_nw['Scenario']} (£{worst_nw['Net Worth']:,.0f})")
                    st.markdown(f"• **Location**: {worst_nw['Location']}")
                    st.markdown(f"• **Salary Template**: {worst_nw['Salary Template']}")

            # Parameter optimization recommendations
            with st.expander("🚀 Parameter Optimization Recommendations", expanded=False):
                st.markdown("### Template Configuration Recommendations")

                # Analyze best performing parameters
                best_scenario = max(outcome_metrics.keys(), key=lambda x: outcome_metrics[x]['Final Net Worth'])
                best_params = parameter_variations[best_scenario]

                st.markdown(f"**Best Performing Configuration** ({best_scenario}):")
                for param, value in best_params.items():
                    st.markdown(f"• {param.replace('_', ' ').title()}: {value}")

                st.markdown("### Parameter Sensitivity Rankings")

                # Simple sensitivity analysis
                param_impacts = {}
                for param in all_params:
                    values_outcomes = []
                    for scenario, params in parameter_variations.items():
                        if param in params and isinstance(params[param], (int, float)):
                            values_outcomes.append((params[param], outcome_metrics[scenario]['Final Net Worth']))

                    if len(values_outcomes) > 1:
                        # Calculate correlation
                        values, outcomes = zip(*values_outcomes)
                        if len(set(values)) > 1:
                            correlation = np.corrcoef(values, outcomes)[0, 1]
                            param_impacts[param] = abs(correlation)

                # Sort by impact
                sorted_impacts = sorted(param_impacts.items(), key=lambda x: x[1], reverse=True)

                st.markdown("**Parameters by Impact** (correlation with net worth):")
                for param, impact in sorted_impacts[:5]:
                    st.markdown(f"• {param.replace('_', ' ').title()}: {impact:.3f}")
        else:
            st.info("Insufficient parameter variation for sensitivity analysis.")

    except Exception as e:
        st.error(f"Error rendering template parameter sensitivity: {str(e)}")


def _get_scenario_template_info(scenario_name: str, enriched_metadata: Dict) -> Dict[str, str]:
    """Get simplified template information for a scenario."""
    # Handle empty metadata with simplified logic
    if not enriched_metadata:
        # Extract basic info from scenario name patterns
        phase_type = "Multi-Phase" if "year" in scenario_name.lower() else "Single-Phase"

        # Determine location/jurisdiction from name
        if "dubai" in scenario_name.lower():
            jurisdiction = "UAE"
            salary_template = "Tech (Tax-Free)"
        elif "seattle" in scenario_name.lower():
            jurisdiction = "US (Seattle)"
            salary_template = "Tech (US West Coast)"
        elif "new_york" in scenario_name.lower():
            jurisdiction = "US (New York)"
            salary_template = "Tech (US East Coast)"
        elif "uk" in scenario_name.lower():
            jurisdiction = "UK"
            salary_template = "Tech (UK)"
        else:
            jurisdiction = "Unknown"
            salary_template = "Unknown"

        # Determine housing strategy
        if "local_home" in scenario_name.lower():
            housing_template = "Local Purchase"
        elif "uk_home" in scenario_name.lower():
            housing_template = "UK Purchase"
        else:
            housing_template = "Unknown"

        # Determine investment strategy
        if "aggressive" in scenario_name.lower():
            investment_template = "Aggressive Growth"
        elif "conservative" in scenario_name.lower():
            investment_template = "Conservative"
        else:
            investment_template = "Balanced"

        return {
            'salary': salary_template,
            'housing': housing_template,
            'investments': investment_template,
            'phase': phase_type,
            'jurisdiction': jurisdiction
        }

    # Original logic for full metadata (kept for backward compatibility)
    for scenario_id, meta in enriched_metadata.items():
        if meta.get('name', scenario_id) == scenario_name:
            if 'error' not in meta:
                composition = meta.get('template_composition', {})
                return {
                    'salary': composition.get('salary', 'Unknown'),
                    'housing': composition.get('housing', 'Unknown'),
                    'investments': composition.get('investments', 'Unknown'),
                    'phase': meta.get('phase_type', 'Unknown'),
                    'jurisdiction': meta.get('configuration_summary', {}).get('jurisdiction', 'Unknown')
                }
            break
    return {'salary': 'Unknown', 'housing': 'Unknown', 'investments': 'Unknown', 'phase': 'Unknown', 'jurisdiction': 'Unknown'}


def main() -> None:
    """Main function to render the income and expense breakdown page."""
    render_income_expense_page()


if __name__ == "__main__":
    main()
