"""
Data loading and processing utilities for the financial planning dashboard.
Includes enhanced caching for performance optimization with unified models.
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import time
import functools

# Import unified financial planner functions
from financial_planner_pydantic import (
    run_unified_scenario,
    run_unified_international_scenario,
    run_unified_delayed_relocation_scenario
)
from config import CONFIG

# Import unified models and helpers
from models.unified_financial_data import (
    UnifiedFinancialScenario, UnifiedFinancialData, ScenarioMetadata,
    CurrencyValue, Currency, Jurisdiction, FinancialPhase
)
from models.unified_helpers import (
    create_scenario_metadata_from_name,
    get_performance_metrics,
    clear_performance_caches
)


@st.cache_data(ttl=300, max_entries=10)
def load_all_scenarios() -> Dict[str, UnifiedFinancialScenario]:
    """
    Load all financial scenarios with enhanced caching for performance using unified models.
    
    Returns:
        Dict containing all scenario data with unified structure.
    """
    scenarios = {}
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # UK Scenarios (fastest to load) - using unified models
        status_text.text("Loading UK scenarios...")
        scenarios['UK_Scenario_A'] = run_unified_scenario('A', CONFIG)
        scenarios['UK_Scenario_B'] = run_unified_scenario('B', CONFIG)
        progress_bar.progress(0.15)
        
        # International Scenarios
        status_text.text("Loading international scenarios...")
        international_scenarios = [
            ('seattle', 'uk_home'), ('seattle', 'local_home'),
            ('new_york', 'uk_home'), ('new_york', 'local_home'),
            ('dubai', 'uk_home'), ('dubai', 'local_home')
        ]
        
        for i, (location, housing_strategy) in enumerate(international_scenarios):
            try:
                scenario = run_unified_international_scenario(location, CONFIG, housing_strategy)
                # Convert location to proper title case (e.g., "new_york" -> "New York")
                location_display = location.replace('_', ' ').title()
                display_name = f"{location_display} {housing_strategy.replace('_', ' ').title()}"
                scenarios[display_name] = scenario
                
                # Update progress
                progress = 0.15 + (0.35 * (i + 1) / len(international_scenarios))
                progress_bar.progress(progress)
                
            except Exception as e:
                st.warning(f"Failed to load international scenario {location} {housing_strategy}: {str(e)}")
        
        # Delayed Relocation Scenarios (more complex)
        status_text.text("Loading delayed relocation scenarios...")
        delayed_scenarios = [
            'seattle_year4_uk_home', 'seattle_year4_local_home',
            'seattle_year5_uk_home', 'seattle_year5_local_home',
            'new_york_year4_uk_home', 'new_york_year4_local_home',
            'new_york_year5_uk_home', 'new_york_year5_local_home',
            'dubai_year4_uk_home', 'dubai_year4_local_home',
            'dubai_year5_uk_home', 'dubai_year5_local_home'
        ]
        
        for i, scenario_name in enumerate(delayed_scenarios):
            try:
                # Use unified scenario generation
                unified_scenario = run_unified_delayed_relocation_scenario(scenario_name, CONFIG)
                # Convert scenario name to display format
                display_name = scenario_name.replace('_', ' ').title()
                scenarios[display_name] = unified_scenario
                
                # Update progress
                progress = 0.5 + (0.5 * (i + 1) / len(delayed_scenarios))
                progress_bar.progress(progress)
                
            except Exception as e:
                st.warning(f"Failed to load scenario {scenario_name}: {str(e)}")
        
        status_text.text("Data loading complete!")
        time.sleep(0.5)  # Brief pause to show completion
        
    except Exception as e:
        st.error(f"Error loading scenarios: {str(e)}")
        return {}
    
    finally:
        progress_bar.empty()
        status_text.empty()
    
    return scenarios


def filter_scenarios(
    _all_scenarios: Dict[str, UnifiedFinancialScenario],
    selected_scenarios: List[str],
    year_range: Tuple[int, int]
) -> Dict[str, UnifiedFinancialScenario]:
    """
    Filter scenarios based on selection and year range with caching using unified models.
    
    Args:
        all_scenarios: All available scenarios with unified structure
        selected_scenarios: List of selected scenario names
        year_range: Tuple of (start_year, end_year)
    
    Returns:
        Filtered scenarios dictionary with unified structure
    """
    filtered = {}
    
    for scenario_name in selected_scenarios:
        if scenario_name in _all_scenarios:
            scenario = _all_scenarios[scenario_name]
            
            # Filter data points by year range
            filtered_data_points = []
            for point in scenario.data_points:
                if year_range[0] <= point.year <= year_range[1]:
                    filtered_data_points.append(point)
            
            # Create filtered scenario with unified structure
            filtered_scenario = UnifiedFinancialScenario(
                name=scenario.name,
                description=scenario.description,
                phase=scenario.phase,
                data_points=filtered_data_points,
                metadata=scenario.metadata
            )
            filtered[scenario_name] = filtered_scenario
    return filtered


def filter_scenarios_by_type(
    all_scenarios: Dict[str, UnifiedFinancialScenario],
    uk_only: bool = False,
    international_only: bool = False,
    tax_free_only: bool = False,
    delayed_relocation_only: bool = False
) -> Dict[str, UnifiedFinancialScenario]:
    """
    Filter scenarios based on type filters using unified models.
    
    Args:
        all_scenarios: All available scenarios with unified structure
        uk_only: Show only UK scenarios
        international_only: Show only international scenarios
        tax_free_only: Show only tax-free scenarios
        delayed_relocation_only: Show only delayed relocation scenarios
    
    Returns:
        Filtered scenarios dictionary with unified structure
    """
    filtered = {}
    
    for scenario_name, scenario in all_scenarios.items():
        include_scenario = True
        
        # UK scenarios filter
        if uk_only:
            if not scenario_name.startswith('UK_Scenario'):
                include_scenario = False
        
        # International scenarios filter
        if international_only:
            if scenario_name.startswith('UK_Scenario'):
                include_scenario = False
        
        # Tax-free scenarios filter (Dubai scenarios)
        if tax_free_only:
            if not 'Dubai' in scenario_name:
                include_scenario = False
        
        # Delayed relocation scenarios filter
        if delayed_relocation_only:
            if not any(keyword in scenario_name for keyword in ['Year4', 'Year5']):
                include_scenario = False
        
        if include_scenario:
            filtered[scenario_name] = scenario
    
    return filtered


def calculate_key_metrics(scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, Any]:
    """
    Calculate key performance metrics for selected scenarios with caching using unified models.
    
    Args:
        scenarios: Dictionary of scenario data with unified structure
    
    Returns:
        Dictionary containing calculated metrics
    """
    if not scenarios:
        return {
            'max_net_worth': 0,
            'avg_annual_savings': 0,
            'total_tax_burden': 0,
            'scenarios_count': 0
        }
    
    max_net_worth = 0
    total_savings = 0
    total_tax = 0
    savings_count = 0
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points:
            continue
        
        # Calculate net worth metrics using unified structure
        for point in scenario.data_points:
            net_worth = point.net_worth_gbp
            max_net_worth = max(max_net_worth, net_worth)
            
            # Calculate savings using unified structure
            savings = point.annual_savings_gbp
            total_savings += savings
            savings_count += 1
            
            # Calculate tax burden using unified structure
            tax = point.total_tax_gbp
            total_tax += tax
    
    return {
        'max_net_worth': max_net_worth,
        'avg_annual_savings': total_savings / max(1, savings_count),
        'total_tax_burden': total_tax,
        'scenarios_count': len(scenarios)
    }


@st.cache_data(ttl=60, max_entries=10)
def get_scenario_metadata() -> Dict[str, Any]:
    """
    Get metadata about available scenarios for UI components using unified models.
    
    Returns:
        Dictionary containing scenario metadata
    """
    return {
        'uk_scenarios': ['UK_Scenario_A', 'UK_Scenario_B'],
        'international_scenarios': [
            'Seattle Uk Home', 'Seattle Local Home',
            'New York Uk Home', 'New York Local Home',
            'Dubai Uk Home', 'Dubai Local Home'
        ],
        'delayed_relocation_scenarios': [
            'Seattle Year4 Uk Home', 'Seattle Year4 Local Home',
            'Seattle Year5 Uk Home', 'Seattle Year5 Local Home',
            'New York Year4 Uk Home', 'New York Year4 Local Home',
            'New York Year5 Uk Home', 'New York Year5 Local Home',
            'Dubai Year4 Uk Home', 'Dubai Year4 Local Home',
            'Dubai Year5 Uk Home', 'Dubai Year5 Local Home'
        ],
        'tax_free_scenarios': [
            'Dubai Uk Home', 'Dubai Local Home',
            'Dubai Year4 Uk Home', 'Dubai Year4 Local Home',
            'Dubai Year5 Uk Home', 'Dubai Year5 Local Home'
        ],
        'scenario_groups': {
            'UK': ['UK_Scenario_A', 'UK_Scenario_B'],
            'Seattle': ['Seattle Uk Home', 'Seattle Local Home', 'Seattle Year4 Uk Home', 'Seattle Year4 Local Home', 'Seattle Year5 Uk Home', 'Seattle Year5 Local Home'],
            'New York': ['New York Uk Home', 'New York Local Home', 'New York Year4 Uk Home', 'New York Year4 Local Home', 'New York Year5 Uk Home', 'New York Year5 Local Home'],
            'Dubai': ['Dubai Uk Home', 'Dubai Local Home', 'Dubai Year4 Uk Home', 'Dubai Year4 Local Home', 'Dubai Year5 Uk Home', 'Dubai Year5 Local Home']
        },
        'all_scenarios': [
            'UK_Scenario_A', 'UK_Scenario_B',
            'Seattle Uk Home', 'Seattle Local Home',
            'New York Uk Home', 'New York Local Home',
            'Dubai Uk Home', 'Dubai Local Home',
            'Seattle Year4 Uk Home', 'Seattle Year4 Local Home',
            'Seattle Year5 Uk Home', 'Seattle Year5 Local Home',
            'New York Year4 Uk Home', 'New York Year4 Local Home',
            'New York Year5 Uk Home', 'New York Year5 Local Home',
            'Dubai Year4 Uk Home', 'Dubai Year4 Local Home',
            'Dubai Year5 Uk Home', 'Dubai Year5 Local Home'
        ]
    }


def prepare_comparison_data(scenario1: str, scenario2: str, all_scenarios: Dict[str, UnifiedFinancialScenario]) -> Dict[str, Any]:
    """
    Prepare data for scenario comparison with caching using unified models.
    
    Args:
        scenario1: First scenario name
        scenario2: Second scenario name
        all_scenarios: All available scenarios with unified structure
    
    Returns:
        Dictionary containing comparison data
    """
    if scenario1 not in all_scenarios or scenario2 not in all_scenarios:
        return {}
    
    scenario1_data = all_scenarios[scenario1]
    scenario2_data = all_scenarios[scenario2]
    
    comparison_data = {
        'scenario1': {
            'name': scenario1,
            'final_net_worth': scenario1_data.get_final_net_worth_gbp() if scenario1_data.data_points else 0,
            'total_savings': sum(point.annual_savings_gbp for point in scenario1_data.data_points),
            'total_tax': sum(point.total_tax_gbp for point in scenario1_data.data_points)
        },
        'scenario2': {
            'name': scenario2,
            'final_net_worth': scenario2_data.get_final_net_worth_gbp() if scenario2_data.data_points else 0,
            'total_savings': sum(point.annual_savings_gbp for point in scenario2_data.data_points),
            'total_tax': sum(point.total_tax_gbp for point in scenario2_data.data_points)
        }
    }
    
    return comparison_data


def export_scenario_data(scenarios: Dict[str, UnifiedFinancialScenario], format: str = 'csv') -> bytes:
    """
    Export scenario data in specified format with caching using unified models.
    
    Args:
        scenarios: Dictionary of scenario data with unified structure
        format: Export format ('csv', 'excel')
    
    Returns:
        Bytes object containing exported data
    """
    if not scenarios:
        return b''
    
    # Prepare data for export using unified structure
    export_data = []
    
    for scenario_name, scenario in scenarios.items():
        if not scenario.data_points:
            continue
        
        for point in scenario.data_points:
            export_data.append({
                'Scenario': scenario_name,
                'Year': point.year,
                'Net_Worth': point.net_worth_gbp,
                'Annual_Savings': point.annual_savings_gbp,
                'Gross_Income': point.gross_income_gbp,
                'Total_Expenses': point.total_expenses_gbp,
                'Total_Tax': point.total_tax_gbp,
                'Jurisdiction': point.jurisdiction.value,
                'Phase': point.phase.value
            })
    
    if not export_data:
        return b''
    
    df = pd.DataFrame(export_data)
    
    if format.lower() == 'csv':
        return df.to_csv(index=False).encode('utf-8')
    elif format.lower() == 'excel':
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Scenario_Data')
        return output.getvalue()
    else:
        return df.to_csv(index=False).encode('utf-8')


def get_performance_metrics() -> Dict[str, Any]:
    """Get performance metrics for monitoring."""
    from models.unified_helpers import get_performance_metrics as get_unified_performance_metrics
    return get_unified_performance_metrics()


def clear_cache() -> None:
    """Clear all cached data to force reload."""
    st.cache_data.clear()
    clear_performance_caches() 