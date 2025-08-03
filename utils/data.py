"""
Data loading and processing utilities for the financial planning dashboard.
Uses the new template-driven system for scenario generation.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import time
import functools
import sys
from pathlib import Path

# Import the new template-driven financial planner
from financial_planner_template_driven import TemplateFinancialPlanner
from config.template_engine import TemplateEngine, GenericCalculationEngine

# Import unified models and helpers
from models.unified_financial_data import (
    UnifiedFinancialScenario, UnifiedFinancialData, ScenarioMetadata,
    CurrencyValue, Currency, Jurisdiction, FinancialPhase
)
from models.unified_helpers import (
    get_performance_metrics,
    clear_performance_caches
)


@st.cache_data(ttl=300, max_entries=10)
def load_all_scenarios() -> Dict[str, UnifiedFinancialScenario]:
    """
    Load all available scenarios using the template-driven financial planner with proper ID mapping.

    Returns:
        Dictionary of scenario_id -> UnifiedFinancialScenario objects
    """
    try:
        with st.spinner("Loading template-driven scenarios..."):
            planner = TemplateFinancialPlanner()
            scenario_ids = planner.get_available_scenarios()

            scenarios = {}

            # Progress tracking
            progress_bar = st.progress(0)
            total_scenarios = len(scenario_ids)

            for i, scenario_id in enumerate(scenario_ids):
                try:
                    # Load and run the scenario
                    unified_scenario = planner.run_scenario(scenario_id)

                    # Store using both the scenario ID and the display name as keys
                    scenarios[scenario_id] = unified_scenario

                    # Also store using display name for backward compatibility
                    if unified_scenario.name != scenario_id:
                        scenarios[unified_scenario.name] = unified_scenario

                    # Update progress
                    progress_bar.progress((i + 1) / total_scenarios)

                except Exception as e:
                    st.warning(f"Failed to load scenario {scenario_id}: {str(e)}")
                    continue

            progress_bar.empty()

            print(f"DEBUG: Loaded {len(scenarios)} scenario entries")
            print(f"DEBUG: Scenario keys: {list(scenarios.keys())}")

            return scenarios

    except Exception as e:
        st.error(f"Failed to load scenarios: {str(e)}")
        return {}


@st.cache_data(ttl=600, max_entries=5)
def get_enriched_scenario_metadata() -> Dict[str, Dict[str, Any]]:
    """
    Get enriched scenario metadata with template composition details.

    Returns:
        Dict mapping scenario IDs to enriched metadata including:
        - Template composition (salary, housing, investment, tax)
        - Configuration parameters
        - Validation status
        - Phase information
        - Jurisdiction details
    """
    metadata = {}
    planner = TemplateFinancialPlanner()

    try:
        available_scenarios = planner.get_available_scenarios()

        for scenario_id in available_scenarios:
            try:
                # Get basic summary
                summary = planner.get_scenario_summary(scenario_id)

                if 'error' not in summary:
                    # Enrich with additional template metadata
                    metadata[scenario_id] = {
                        **summary,
                        'scenario_id': scenario_id,
                        'template_composition': summary.get('components', {}),
                        'phase_type': summary.get('phase', 'Unknown'),
                        'validation_status': 'unknown',  # Will be updated by validation
                        'configuration_summary': _get_configuration_summary(planner, scenario_id),
                        'template_types': _get_template_types(summary.get('components', {}))
                    }
                else:
                    metadata[scenario_id] = {
                        'scenario_id': scenario_id,
                        'name': scenario_id,
                        'error': summary['error'],
                        'validation_status': 'error'
                    }

            except Exception as e:
                metadata[scenario_id] = {
                    'scenario_id': scenario_id,
                    'name': scenario_id,
                    'error': str(e),
                    'validation_status': 'error'
                }

        return metadata

    except Exception as e:
        st.error(f"Failed to get enriched scenario metadata: {str(e)}")
        return {}


@st.cache_data(ttl=300, max_entries=5)
def validate_all_scenarios() -> Dict[str, Dict[str, Any]]:
    """
    Validate all available scenarios and return detailed status.

    Returns:
        Dict mapping scenario IDs to validation results:
        - valid: bool
        - message: str
        - errors: List[str] (if any)
        - warnings: List[str] (if any)
    """
    validation_results = {}
    planner = TemplateFinancialPlanner()

    try:
        available_scenarios = planner.get_available_scenarios()

        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, scenario_id in enumerate(available_scenarios):
            status_text.text(f"Validating {scenario_id}...")

            try:
                # Validate scenario
                result = planner.validate_scenario(scenario_id)
                validation_results[scenario_id] = result

                # Update progress
                progress = (i + 1) / len(available_scenarios)
                progress_bar.progress(progress)

            except Exception as e:
                validation_results[scenario_id] = {
                    'scenario_id': scenario_id,
                    'valid': False,
                    'message': f"Validation failed: {str(e)}",
                    'errors': [str(e)]
                }

        progress_bar.empty()
        status_text.empty()

        return validation_results

    except Exception as e:
        st.error(f"Failed to validate scenarios: {str(e)}")
        return {}


@st.cache_data(ttl=600, max_entries=5)
def get_template_configuration_summary() -> Dict[str, Dict[str, Any]]:
    """
    Get summary of template configurations for each scenario.

    Returns:
        Dict mapping scenario IDs to configuration summaries:
        - parameters: key configuration values
        - template_files: source template files
        - inheritance_tree: template composition hierarchy
    """
    config_summaries = {}
    planner = TemplateFinancialPlanner()

    try:
        available_scenarios = planner.get_available_scenarios()

        for scenario_id in available_scenarios:
            try:
                # Load scenario configuration
                config = planner.template_engine.load_scenario(scenario_id)

                config_summaries[scenario_id] = {
                    'scenario_parameters': {
                        'start_year': config.planning_parameters.get('start_year'),
                        'duration_years': config.planning_parameters.get('duration_years'),
                        'start_age': config.planning_parameters.get('start_age')
                    },
                    'template_files': {
                        'salary_progression': config.salary_progression.get('template'),
                        'housing_strategy': config.housing_strategy.get('template'),
                        'expense_profile': config.expense_profile.get('template'),
                        'investment_strategy': config.investment_strategy.get('template') if config.investment_strategy else None,
                        'tax_system': config.tax_system.get('tax_system_id')
                    },
                    'key_parameters': _extract_key_parameters(config),
                    'template_inheritance': _build_inheritance_tree(config)
                }

            except Exception as e:
                config_summaries[scenario_id] = {
                    'error': str(e),
                    'scenario_parameters': {},
                    'template_files': {},
                    'key_parameters': {},
                    'template_inheritance': {}
                }

        return config_summaries

    except Exception as e:
        st.error(f"Failed to get template configuration summaries: {str(e)}")
        return {}


def _get_configuration_summary(planner: TemplateFinancialPlanner, scenario_id: str) -> Dict[str, Any]:
    """Extract key configuration parameters for display."""
    try:
        config = planner.template_engine.load_scenario(scenario_id)
        return {
            'duration': f"{config.planning_parameters.get('duration_years', 'Unknown')} years",
            'start_year': config.planning_parameters.get('start_year', 'Unknown'),
            'start_age': config.planning_parameters.get('start_age', 'Unknown'),
            'tax_system': config.tax_system.get('tax_system_id', 'Unknown'),
            'num_phases': len(config.phases) if hasattr(config, 'phases') else 1
        }
    except Exception:
        return {'error': 'Could not load configuration'}


def _get_template_types(components: Dict[str, str]) -> List[str]:
    """Extract template types from component composition."""
    types = []
    if components.get('salary'):
        types.append('salary_progression')
    if components.get('housing'):
        types.append('housing_strategy')
    if components.get('expenses'):
        types.append('expense_profile')
    if components.get('investments'):
        types.append('investment_strategy')
    if components.get('tax_system'):
        types.append('tax_system')
    return types


def _extract_key_parameters(config) -> Dict[str, Any]:
    """Extract key parameters from scenario configuration."""
    try:
        params = {}

        # Salary progression parameters
        if hasattr(config, 'salary_progression') and config.salary_progression:
            salary_params = config.salary_progression.get('parameters', {})
            if salary_params:
                params['salary'] = {
                    'base_salary': salary_params.get('base_salary'),
                    'growth_rate': salary_params.get('annual_increase_rate'),
                    'bonus_rate': salary_params.get('bonus_rate')
                }

        # Housing parameters
        if hasattr(config, 'housing_strategy') and config.housing_strategy:
            housing_params = config.housing_strategy.get('parameters', {})
            if housing_params:
                params['housing'] = {
                    'purchase_year': housing_params.get('purchase_year'),
                    'deposit_pct': housing_params.get('deposit_pct'),
                    'property_price': housing_params.get('property_price')
                }

        # Investment parameters
        if hasattr(config, 'investment_strategy') and config.investment_strategy:
            investment_params = config.investment_strategy.get('parameters', {})
            if investment_params:
                params['investments'] = {
                    'return_rate': investment_params.get('annual_return_rate'),
                    'risk_level': investment_params.get('risk_level')
                }

        return params

    except Exception:
        return {}


def _build_inheritance_tree(config) -> Dict[str, Any]:
    """Build template inheritance tree for visualization."""
    try:
        tree = {
            'scenario': config.scenario_metadata.get('name', 'Unknown'),
            'templates': {}
        }

        # Add template composition
        if hasattr(config, 'salary_progression') and config.salary_progression:
            tree['templates']['salary_progression'] = {
                'template': config.salary_progression.get('template'),
                'extends': config.salary_progression.get('extends')
            }

        if hasattr(config, 'housing_strategy') and config.housing_strategy:
            tree['templates']['housing_strategy'] = {
                'template': config.housing_strategy.get('template'),
                'extends': config.housing_strategy.get('extends')
            }

        if hasattr(config, 'expense_profile') and config.expense_profile:
            tree['templates']['expense_profile'] = {
                'template': config.expense_profile.get('template'),
                'extends': config.expense_profile.get('extends')
            }

        if hasattr(config, 'investment_strategy') and config.investment_strategy:
            tree['templates']['investment_strategy'] = {
                'template': config.investment_strategy.get('template'),
                'extends': config.investment_strategy.get('extends')
            }

        return tree

    except Exception:
        return {'error': 'Could not build inheritance tree'}


def filter_scenarios(scenarios: Dict[str, Any],
    selected_scenarios: List[str],
                    year_range: Tuple[int, int]) -> Dict[str, Any]:
    """
    Filter scenarios by selection and year range with enhanced debugging.

    Args:
        scenarios: Dictionary of all scenarios
        selected_scenarios: List of selected scenario names/IDs
        year_range: Tuple of (start_year, end_year)

    Returns:
        Filtered scenarios dictionary
    """
    try:
        if not scenarios:
            print("DEBUG: No scenarios provided to filter")
            return {}

        if not selected_scenarios:
            print("DEBUG: No scenarios selected")
            return {}

        print(f"DEBUG: Filtering {len(scenarios)} scenarios, {len(selected_scenarios)} selected")
        print(f"DEBUG: Available scenario keys: {list(scenarios.keys())}")
        print(f"DEBUG: Selected scenarios: {selected_scenarios}")

        # Handle both scenario IDs and scenario names
        filtered_scenarios = {}

        for scenario_key, scenario_data in scenarios.items():
            scenario_name = getattr(scenario_data, 'name', scenario_key)

            # Check if this scenario is selected (by key or name)
            is_selected = (
                scenario_key in selected_scenarios or
                scenario_name in selected_scenarios or
                any(selected in scenario_key or selected in scenario_name
                    for selected in selected_scenarios)
            )

            if is_selected:
                print(f"DEBUG: Including scenario {scenario_key} (name: {scenario_name})")

                # Filter by year range if scenario has data points
                if hasattr(scenario_data, 'data_points') and scenario_data.data_points:
                    # Use relative year indexing (1-based years to 0-based indexing)
                    start_idx = max(0, year_range[0] - 1)  # Convert 1-based to 0-based
                    end_idx = min(len(scenario_data.data_points), year_range[1])

                    print(f"DEBUG: Year range {year_range}, start_idx={start_idx}, end_idx={end_idx}, data_points={len(scenario_data.data_points)}")

                    if start_idx < len(scenario_data.data_points) and end_idx > start_idx:
                        # Create a filtered copy with year-range data
                        filtered_data = type(scenario_data)(
                            name=scenario_data.name,
                            description=getattr(scenario_data, 'description', ''),
                            phase=scenario_data.phase,
                            data_points=scenario_data.data_points[start_idx:end_idx],
                            metadata=getattr(scenario_data, 'metadata', None)
                        )
                        filtered_scenarios[scenario_key] = filtered_data
                        print(f"DEBUG: Filtered {scenario_key} to years {year_range[0]}-{year_range[1]} ({len(filtered_data.data_points)} data points)")
                    else:
                        print(f"DEBUG: Skipping {scenario_key} - invalid year range: start_idx={start_idx}, end_idx={end_idx}, data_points={len(scenario_data.data_points)}")
                else:
                    print(f"DEBUG: Including {scenario_key} without year filtering (no data points)")
                    filtered_scenarios[scenario_key] = scenario_data

        print(f"DEBUG: Final filtered scenarios: {len(filtered_scenarios)} scenarios")
        return filtered_scenarios

    except Exception as e:
        print(f"ERROR: Failed to filter scenarios: {e}")
        import traceback
        traceback.print_exc()
        return {}


def filter_scenarios_by_type(
    all_scenarios: Dict[str, UnifiedFinancialScenario],
    scenario_type: Optional[str] = None
) -> Dict[str, UnifiedFinancialScenario]:
    """
    Filter scenarios by type using the new unified model phase and jurisdiction attributes.

    Args:
        all_scenarios: Dictionary of all scenarios
        scenario_type: Type filter ('uk_only', 'international', 'tax_free', 'delayed_relocation')

    Returns:
        Filtered dictionary of scenarios
    """
    if not scenario_type or scenario_type == 'all':
        return all_scenarios

    filtered = {}

    for name, scenario in all_scenarios.items():
        include_scenario = False

        if scenario_type == 'uk_only':
            # UK only scenarios
            include_scenario = (scenario.phase == FinancialPhase.UK_ONLY or
                              scenario.jurisdiction == Jurisdiction.UK)

        elif scenario_type == 'international':
            # International scenarios (not UK only)
            include_scenario = (scenario.phase != FinancialPhase.UK_ONLY and
                              scenario.jurisdiction != Jurisdiction.UK)

        elif scenario_type == 'tax_free':
            # Tax-free jurisdictions (UAE)
            include_scenario = scenario.jurisdiction == Jurisdiction.UAE

        elif scenario_type == 'delayed_relocation':
            # Multi-phase scenarios with relocation
            include_scenario = scenario.phase in [
                FinancialPhase.UK_THEN_INTERNATIONAL,
                FinancialPhase.INTERNATIONAL_THEN_UK
            ]

        if include_scenario:
            filtered[name] = scenario

    return filtered


def calculate_key_metrics(scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, Any]:
    """
    Calculate key performance metrics across scenarios using unified models.

    Args:
        scenarios: Dictionary of scenarios to analyze

    Returns:
        Dictionary containing aggregated metrics
    """
    if not scenarios:
        return {
            'total_scenarios': 0,
            'avg_final_net_worth': 0,
            'avg_total_savings': 0,
            'avg_total_tax': 0,
            'best_scenario': None,
            'metrics_by_scenario': {}
        }

    metrics = {
        'total_scenarios': len(scenarios),
        'metrics_by_scenario': {}
    }

    total_net_worth = 0
    total_savings = 0
    total_tax = 0
    best_net_worth = 0
    best_scenario = None

    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            # Use unified methods for calculations
            final_net_worth = scenario.get_final_net_worth_gbp()
            total_savings_scenario = sum(point.net_worth.total_gbp - (point.net_worth.total_gbp - point.annual_savings.total_gbp)
                                       for point in scenario.data_points if hasattr(point, 'annual_savings'))
            total_tax_scenario = sum(point.tax.total_gbp for point in scenario.data_points)

            # Track metrics per scenario
            metrics['metrics_by_scenario'][scenario_name] = {
                'final_net_worth': final_net_worth,
                'total_savings': total_savings_scenario,
                'total_tax': total_tax_scenario,
                'data_points': len(scenario.data_points)
            }

            # Aggregate totals
            total_net_worth += final_net_worth
            total_savings += total_savings_scenario
            total_tax += total_tax_scenario

            # Track best scenario
            if final_net_worth > best_net_worth:
                best_net_worth = final_net_worth
                best_scenario = scenario_name

    # Calculate averages
    num_scenarios = len(scenarios)
    metrics.update({
        'avg_final_net_worth': total_net_worth / num_scenarios if num_scenarios > 0 else 0,
        'avg_total_savings': total_savings / num_scenarios if num_scenarios > 0 else 0,
        'avg_total_tax': total_tax / num_scenarios if num_scenarios > 0 else 0,
        'best_scenario': best_scenario,
        'best_net_worth': best_net_worth
    })

    return metrics


def get_scenario_metadata() -> Dict[str, Any]:
    """
    Get metadata about all available scenarios with proper ID/name mapping.

    Returns:
        Dictionary containing scenario metadata and mappings
    """
    try:
        planner = TemplateFinancialPlanner()
        scenario_ids = planner.get_available_scenarios()

        # Get enriched metadata for mapping
        enriched_metadata = get_enriched_scenario_metadata()

        # Create mappings between IDs and names
        id_to_name = {}
        name_to_id = {}
        all_scenarios = []

        for scenario_id in scenario_ids:
            # Try to get the display name from enriched metadata
            scenario_meta = enriched_metadata.get(scenario_id, {})
            display_name = scenario_meta.get('name', scenario_id)

            # Store mappings
            id_to_name[scenario_id] = display_name
            name_to_id[display_name] = scenario_id

            # Use scenario ID as the primary key for selection
            all_scenarios.append(scenario_id)

        print(f"DEBUG: Created mappings for {len(scenario_ids)} scenarios")
        print(f"DEBUG: ID to Name mapping: {id_to_name}")

        return {
            'all_scenarios': all_scenarios,  # Use IDs for consistency
            'id_to_name': id_to_name,
            'name_to_id': name_to_id,
            'scenario_count': len(scenario_ids),
            'enriched_metadata': enriched_metadata
        }

    except Exception as e:
        st.error(f"Failed to get scenario metadata: {str(e)}")
    return {
            'all_scenarios': [],
            'id_to_name': {},
            'name_to_id': {},
            'scenario_count': 0,
            'enriched_metadata': {}
        }


def prepare_comparison_data(scenarios: Dict[str, UnifiedFinancialScenario]) -> pd.DataFrame:
    """
    Prepare data for scenario comparison using unified models.

    Args:
        scenarios: Dictionary of scenarios to compare

    Returns:
        DataFrame with comparison metrics
    """
    comparison_data = []

    for scenario_name, scenario in scenarios.items():
        if scenario.data_points:
            # Use unified methods for calculations
            row = {
                'Scenario': scenario_name,
                'Final Net Worth (£)': scenario.get_final_net_worth_gbp(),
                'Average Annual Savings (£)': scenario.get_average_annual_savings_gbp(),
                'Total Tax Burden (£)': sum(point.tax.total_gbp for point in scenario.data_points),
                'Growth Rate (%)': scenario.get_net_worth_growth_rate(),
                'Years': len(scenario.data_points),
                'Phase': str(scenario.phase).split('.')[-1] if scenario.phase else 'Unknown',
                'Jurisdiction': str(scenario.jurisdiction).split('.')[-1] if scenario.jurisdiction else 'Unknown'
            }
            comparison_data.append(row)

    return pd.DataFrame(comparison_data)


def export_scenario_data(scenarios: Dict[str, UnifiedFinancialScenario], filename: str = "scenario_analysis.csv") -> bool:
    """
    Export scenario data to CSV using unified models.

    Args:
        scenarios: Dictionary of scenarios to export
        filename: Output filename

    Returns:
        True if export successful, False otherwise
    """
    try:
        export_data = []

        for scenario_name, scenario in scenarios.items():
            for year, data_point in enumerate(scenario.data_points, 1):
                row = {
                    'Scenario': scenario_name,
                    'Year': year,
                    'Net Worth (£)': data_point.net_worth.total_gbp,
                    'Income (£)': data_point.income.total_gbp,
                    'Tax (£)': data_point.tax.total_gbp,
                    'Expenses (£)': data_point.expenses.total_gbp,
                    'Savings (£)': data_point.net_worth.total_gbp - (data_point.net_worth.total_gbp - getattr(data_point, 'annual_savings', CurrencyValue()).total_gbp),
                    'Phase': str(scenario.phase).split('.')[-1] if scenario.phase else 'Unknown',
                    'Jurisdiction': str(scenario.jurisdiction).split('.')[-1] if scenario.jurisdiction else 'Unknown'
                }
                export_data.append(row)

        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False)
        return True

    except Exception as e:
        st.error(f"Failed to export data: {str(e)}")
        return False


def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics for monitoring."""
    from models.unified_helpers import get_performance_metrics as get_unified_performance_metrics
    return get_unified_performance_metrics()


def clear_cache():
    """Clear all cached data including performance caches."""
    try:
        # Clear Streamlit caches
        load_all_scenarios.clear()
        get_enriched_scenario_metadata.clear()
        validate_all_scenarios.clear()
        get_template_configuration_summary.clear()

        # Clear performance caches if available
        clear_performance_caches()
    except Exception:
        # Ignore cache clearing errors
        pass


def check_yaml_enhancement() -> bool:
    """
    Check if YAML enhancement features are available.

    Returns:
        True since template-driven system handles YAML internally
    """
    return True
