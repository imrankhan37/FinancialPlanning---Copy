"""
Scenario selector components for the financial planning dashboard.
Provides interactive filtering and selection capabilities.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple, Set
from utils.data import get_scenario_metadata


def render_scenario_selector() -> None:
    """Render the main scenario selector with multi-select dropdown."""
    
    # Get available scenarios
    metadata: Dict[str, List[str]] = get_scenario_metadata()
    all_scenarios: List[str] = metadata['uk_scenarios'] + metadata['international_scenarios']
    
    # Set default selection to all scenarios if none selected
    if not st.session_state.selected_scenarios and all_scenarios:
        st.session_state.selected_scenarios = all_scenarios
    
    # Multi-select dropdown for scenario selection
    selected: List[str] = st.sidebar.multiselect(
        "Select Scenarios",
        options=all_scenarios,
        default=st.session_state.selected_scenarios,
        help="Choose scenarios to compare. Use Ctrl/Cmd+Click for multiple selections."
    )
    
    # Update session state if selection changed
    if selected != st.session_state.selected_scenarios:
        st.session_state.selected_scenarios = selected
    
    # Show selection summary
    if selected:
        st.sidebar.caption(f"Selected {len(selected)} scenario(s): {', '.join(selected)}")
    else:
        st.sidebar.warning("Please select at least one scenario.")


def render_quick_filters() -> None:
    """Render quick filter checkboxes for scenario types."""
        
    # Quick filter checkboxes
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        uk_only: bool = st.sidebar.checkbox(
            "UK Only",
            value=st.session_state.quick_filters['uk_only'],
            help="Show only UK scenarios"
        )
        
        international_only: bool = st.sidebar.checkbox(
            "International Only",
            value=st.session_state.quick_filters['international_only'],
            help="Show only international scenarios"
        )
    
    with col2:
        tax_free_only: bool = st.sidebar.checkbox(
            "Tax-Free Only",
            value=st.session_state.quick_filters['tax_free_only'],
            help="Show only tax-free scenarios (Dubai)"
        )
        
        delayed_relocation_only: bool = st.sidebar.checkbox(
            "Delayed Relocation Only",
            value=st.session_state.quick_filters['delayed_relocation_only'],
            help="Show only delayed relocation scenarios"
        )
    
    # Update session state if filters changed
    filters_changed: bool = (
        uk_only != st.session_state.quick_filters['uk_only'] or
        international_only != st.session_state.quick_filters['international_only'] or
        tax_free_only != st.session_state.quick_filters['tax_free_only'] or
        delayed_relocation_only != st.session_state.quick_filters['delayed_relocation_only']
    )
    
    if filters_changed:
        st.session_state.quick_filters.update({
            'uk_only': uk_only,
            'international_only': international_only,
            'tax_free_only': tax_free_only,
            'delayed_relocation_only': delayed_relocation_only
        })
        
        # Apply filters to scenario selection
        apply_quick_filters()


def apply_quick_filters() -> None:
    """Apply quick filters to the scenario selection."""
    
    metadata: Dict[str, List[str]] = get_scenario_metadata()
    filters: Dict[str, bool] = st.session_state.quick_filters
    
    # Get filtered scenarios based on quick filters
    filtered_scenarios: List[str] = []
    
    if filters['uk_only']:
        filtered_scenarios.extend(metadata['uk_scenarios'])
    
    if filters['international_only']:
        filtered_scenarios.extend(metadata['international_scenarios'])
    
    if filters['tax_free_only']:
        filtered_scenarios.extend(metadata['tax_free_scenarios'])
    
    if filters['delayed_relocation_only']:
        # All international scenarios are delayed relocation
        filtered_scenarios.extend(metadata['international_scenarios'])
    
    # If no filters are active, show all scenarios
    if not any(filters.values()):
        filtered_scenarios = metadata['uk_scenarios'] + metadata['international_scenarios']
    
    # Update selected scenarios to only include filtered ones
    current_selected: List[str] = st.session_state.selected_scenarios
    new_selected: List[str] = [s for s in current_selected if s in filtered_scenarios]
    
    # If no scenarios are selected after filtering, select the first available
    if not new_selected and filtered_scenarios:
        new_selected = [filtered_scenarios[0]]
    
    st.session_state.selected_scenarios = new_selected


def render_year_range_slider() -> None:
    """Render the year range slider for filtering data."""
    
    year_range: Tuple[int, int] = st.sidebar.slider(
        "Year Range",
        min_value=1,
        max_value=10,
        value=st.session_state.year_range,
        help="Filter data to show only selected years"
    )
    
    # Update session state if year range changed
    if year_range != st.session_state.year_range:
        st.session_state.year_range = year_range
        st.rerun()
    
    # Show year range summary
    if year_range[0] == year_range[1]:
        st.sidebar.caption(f"Showing data for Year {year_range[0]}")
    else:
        st.sidebar.caption(f"Showing data for Years {year_range[0]}-{year_range[1]}")


def render_comparison_mode() -> None:
    """Render comparison mode toggle and controls."""
    
    comparison_mode: bool = st.sidebar.checkbox(
        "Comparison Mode",
        value=st.session_state.comparison_mode,
        help="Enable side-by-side scenario comparison"
    )
    
    if comparison_mode != st.session_state.comparison_mode:
        st.session_state.comparison_mode = comparison_mode
        st.rerun()
    
    # Show comparison mode instructions
    if comparison_mode:
        st.sidebar.info("""
        <strong>Comparison Mode Active</strong>
        - Select exactly 2 scenarios for side-by-side comparison
        - Charts will show both scenarios simultaneously
        - Use the comparison page for detailed analysis
        """)


def render_scenario_groups() -> None:
    """Render scenario group selection."""
    
    metadata: Dict[str, List[str]] = get_scenario_metadata()
    
    st.subheader("Scenario Groups")
    
    # Group selection
    selected_group: str = st.selectbox(
        "Select Scenario Group",
        options=["All", "UK", "Seattle", "New York", "Dubai"],
        help="Quickly select scenarios by location"
    )
    
    if selected_group != "All":
        group_scenarios: List[str] = metadata['scenario_groups'].get(selected_group, [])
        
        # Update selected scenarios to include all from the group
        current_selected: List[str] = st.session_state.selected_scenarios
        new_selected: List[str] = list(set(current_selected + group_scenarios))
        
        # Limit to 3 scenarios maximum
        if len(new_selected) > 3:
            new_selected = new_selected[:3]
        
        if new_selected != current_selected:
            st.session_state.selected_scenarios = new_selected
            st.rerun()


def render_advanced_filters() -> None:
    """Render advanced filtering options."""
    
    st.subheader("Advanced Filters")
    
    # Net worth threshold
    min_net_worth: float = st.number_input(
        "Minimum Final Net Worth (£)",
        min_value=0,
        max_value=2000000,
        value=0,
        step=50000,
        help="Filter scenarios by minimum final net worth"
    )
    
    # Savings rate threshold
    min_savings_rate: float = st.number_input(
        "Minimum Savings Rate (%)",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0,
        help="Filter scenarios by minimum savings rate"
    )
    
    # Apply advanced filters button
    if st.button("Apply Advanced Filters"):
        apply_advanced_filters(min_net_worth, min_savings_rate)


def apply_advanced_filters(min_net_worth: float, min_savings_rate: float) -> None:
    """Apply advanced filters to scenario selection."""
    
    # This would require loading scenario data to apply filters
    # For now, just show a message
    st.info(f"Advanced filters applied: Min Net Worth £{min_net_worth:,.0f}, Min Savings Rate {min_savings_rate:.1f}%")


def render_scenario_info(scenario_name: str) -> None:
    """Render detailed information about a selected scenario."""
    
    st.subheader(f"Scenario Information: {scenario_name}")
    
    # Get scenario metadata
    metadata: Dict[str, List[str]] = get_scenario_metadata()
    
    # Determine scenario type
    scenario_type: str = "Unknown"
    if scenario_name in metadata['uk_scenarios']:
        scenario_type = "UK"
    elif scenario_name in metadata['international_scenarios']:
        scenario_type = "International"
    
    # Display scenario information
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Type", scenario_type)
        st.metric("Tax Status", "Tax-Free" if scenario_name in metadata['tax_free_scenarios'] else "Taxed")
    
    with col2:
        # Determine location from scenario name
        location: str = "UK"
        if "Seattle" in scenario_name:
            location = "Seattle, WA"
        elif "New York" in scenario_name:
            location = "New York, NY"
        elif "Dubai" in scenario_name:
            location = "Dubai, UAE"
        
        st.metric("Location", location)
        
        # Determine housing strategy
        housing_strategy: str = "UK Home" if "UK Home" in scenario_name else "Local Home" if "Local Home" in scenario_name else "N/A"
        st.metric("Housing Strategy", housing_strategy)
    
    # Show scenario description
    if "Year4" in scenario_name:
        st.info("This scenario involves 3 years in the UK followed by international relocation.")
    elif "Year5" in scenario_name:
        st.info("This scenario involves 4 years in the UK followed by international relocation.")
    elif scenario_type == "UK":
        st.info("This is a UK-only scenario with no international relocation.")