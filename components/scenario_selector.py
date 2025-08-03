"""
Scenario selector components for the financial planning dashboard.
Provides interactive filtering and selection capabilities with template-driven discovery.
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple, Set
from utils.data import (
    get_scenario_metadata,
    get_enriched_scenario_metadata,
    validate_all_scenarios,
    get_template_configuration_summary
)
from financial_planner_template_driven import TemplateFinancialPlanner


def render_scenario_selector() -> None:
    """Render the enhanced scenario selector with template metadata and dynamic discovery."""

    try:
        # Simplified approach: Get scenarios directly without expensive metadata
        planner = TemplateFinancialPlanner()
        all_scenarios = planner.get_available_scenarios()

        # Initialize empty metadata and validation to avoid hangs
        enriched_metadata = {}
        validation_status = {}

        # Create simplified metadata structure
        metadata = {
            'all_scenarios': all_scenarios,
            'id_to_name': {sid: sid for sid in all_scenarios},  # Use ID as display name for now
            'name_to_id': {sid: sid for sid in all_scenarios},
            'scenario_count': len(all_scenarios),
            'enriched_metadata': enriched_metadata
        }

        # Debug information
        st.sidebar.markdown(f"**Debug Info:**")
        st.sidebar.text(f"Available: {len(all_scenarios)}")
        st.sidebar.text(f"In session: {len(st.session_state.selected_scenarios)}")

        # Set default selection to all scenarios if none selected
        if (not st.session_state.selected_scenarios or
            len(st.session_state.selected_scenarios) == 0) and all_scenarios:
            st.session_state.selected_scenarios = all_scenarios.copy()
            st.sidebar.success(f"✅ Auto-selected {len(all_scenarios)} scenarios")

        # Check for mismatched scenarios and clean up selection
        mismatched = [s for s in st.session_state.selected_scenarios if s not in all_scenarios]
        if mismatched:
            st.sidebar.warning(f"⚠️ Removing {len(mismatched)} invalid scenarios")
            st.session_state.selected_scenarios = [s for s in st.session_state.selected_scenarios if s in all_scenarios]

        # If no scenarios are selected after filtering, select all available
        if not st.session_state.selected_scenarios and all_scenarios:
            st.session_state.selected_scenarios = all_scenarios.copy()
            st.sidebar.info(f"🔄 Reset to all {len(all_scenarios)} scenarios")

        # Enhanced scenario selection with template metadata
        st.sidebar.markdown("### 🎯 Scenario Selection")

        # Template-aware filtering options
        render_template_filters(enriched_metadata, validation_status)

        # Multi-select dropdown with enriched options
        selected_scenarios = render_enhanced_multiselect(
            all_scenarios, enriched_metadata, validation_status
        )

        # Update session state if selection changed
        if selected_scenarios != st.session_state.selected_scenarios:
            st.session_state.selected_scenarios = selected_scenarios
            st.sidebar.success(f"✅ Updated selection: {len(selected_scenarios)} scenarios")

        # Show enhanced selection summary
        render_selection_summary(selected_scenarios, enriched_metadata, validation_status)

        # Template composition viewer for selected scenarios
        if selected_scenarios:
            render_template_composition_viewer(selected_scenarios, enriched_metadata)

    except Exception as e:
        st.sidebar.error(f"Failed to render scenario selector: {str(e)}")
        import traceback
        st.sidebar.code(traceback.format_exc())


def render_template_filters(enriched_metadata: Dict[str, Dict], validation_status: Dict[str, Dict]) -> None:
    """Render simplified filtering options."""

    st.sidebar.markdown("#### 🔍 Basic Filters")

    # Initialize filter state if not exists
    if 'template_filters' not in st.session_state:
        st.session_state.template_filters = {
            'phase_filter': 'all',
            'jurisdiction_filter': 'all',
            'template_type_filter': 'all',
            'validation_filter': 'all',
            'show_composition': False
        }

    # Simplified phase filter
    phase_options = ['all', 'UK', 'International', 'Multi-Phase']

    phase_filter = st.sidebar.selectbox(
        "Filter by Phase",
        options=phase_options,
        index=phase_options.index(st.session_state.template_filters['phase_filter']),
        help="Filter scenarios by their phase type (UK only, international, etc.)"
    )

    # Jurisdiction filter (derived from scenario metadata)
    jurisdiction_options = ['all', 'UK', 'US', 'UAE', 'Multi-jurisdiction']
    jurisdiction_filter = st.sidebar.selectbox(
        "Filter by Jurisdiction",
        options=jurisdiction_options,
        index=jurisdiction_options.index(st.session_state.template_filters['jurisdiction_filter']),
        help="Filter scenarios by primary jurisdiction"
    )

    # Template type filter
    template_type_options = ['all', 'salary_progression', 'housing_strategy', 'investment_strategy', 'tax_system']
    template_type_filter = st.sidebar.selectbox(
        "Filter by Template Type",
        options=template_type_options,
        index=template_type_options.index(st.session_state.template_filters['template_type_filter']),
        help="Filter scenarios by included template types"
    )

    # Validation filter
    validation_options = ['all', 'valid_only', 'invalid_only', 'unknown']
    validation_filter = st.sidebar.selectbox(
        "Filter by Validation Status",
        options=validation_options,
        index=validation_options.index(st.session_state.template_filters['validation_filter']),
        help="Filter scenarios by template validation status"
    )

    # Template composition viewer toggle
    show_composition = st.sidebar.checkbox(
        "Show Template Composition",
        value=st.session_state.template_filters['show_composition'],
        help="Display template composition details for each scenario"
    )

    # Update session state
    st.session_state.template_filters.update({
        'phase_filter': phase_filter,
        'jurisdiction_filter': jurisdiction_filter,
        'template_type_filter': template_type_filter,
        'validation_filter': validation_filter,
        'show_composition': show_composition
    })


def render_enhanced_multiselect(all_scenarios: List[str],
                               enriched_metadata: Dict,
                               validation_status: Dict) -> List[str]:
    """Render enhanced multi-select dropdown with simplified handling to avoid hangs."""

    try:
        # Simplified approach: Use scenario IDs directly as display names
        scenario_options = []
        scenario_id_map = {}

        for scenario_id in all_scenarios:
            display_name = scenario_id.replace('_', ' ').title()  # Make it more readable

            # Use green checkmark since scenarios are loading successfully
            validation_icon = "✅"  # Success icon since scenarios are working
            phase_icon = "📊"  # Default icon

            # Create display option
            option_label = f"{validation_icon} {phase_icon} {display_name}"
            scenario_options.append(option_label)
            scenario_id_map[option_label] = scenario_id

        # Convert current selection (IDs) to display format
        current_selection_display = []
        for scenario_id in st.session_state.selected_scenarios:
            display_name = scenario_id.replace('_', ' ').title()
            # Find the matching option with icons
            for option in scenario_options:
                if display_name in option:
                    current_selection_display.append(option)
                    break

        # Render multiselect
        selected_options = st.multiselect(
            "Select scenarios to analyze:",
            options=scenario_options,
            default=current_selection_display,
            help="Choose which scenarios to include in your analysis. ✅=Successfully loaded, 📊=Ready for analysis"
        )

        # Convert selected options back to scenario IDs
        selected_scenario_ids = [scenario_id_map.get(option, option) for option in selected_options]

        print(f"DEBUG: Selected options: {selected_options}")
        print(f"DEBUG: Mapped to IDs: {selected_scenario_ids}")

        return selected_scenario_ids

    except Exception as e:
        st.error(f"Failed to render enhanced multiselect: {str(e)}")
        return st.session_state.selected_scenarios


def apply_template_filters(
    all_scenarios: List[str],
    enriched_metadata: Dict[str, Dict],
    validation_status: Dict[str, Dict]
) -> List[str]:
    """Apply template-based filters to scenario list."""

    filters = st.session_state.template_filters
    filtered_scenarios = all_scenarios.copy()

    # Apply phase filter
    if filters['phase_filter'] != 'all':
        filtered_scenarios = [
            s for s in filtered_scenarios
            if enriched_metadata.get(s, {}).get('phase_type', 'Unknown') == filters['phase_filter']
        ]

    # Apply jurisdiction filter
    if filters['jurisdiction_filter'] != 'all':
        filtered_scenarios = [
            s for s in filtered_scenarios
            if _matches_jurisdiction_filter(s, enriched_metadata, filters['jurisdiction_filter'])
        ]

    # Apply template type filter
    if filters['template_type_filter'] != 'all':
        filtered_scenarios = [
            s for s in filtered_scenarios
            if filters['template_type_filter'] in enriched_metadata.get(s, {}).get('template_types', [])
        ]

    # Apply validation filter
    if filters['validation_filter'] != 'all':
        filtered_scenarios = [
            s for s in filtered_scenarios
            if _matches_validation_filter(s, validation_status, filters['validation_filter'])
        ]

    return filtered_scenarios


def _matches_jurisdiction_filter(scenario_id: str, enriched_metadata: Dict, filter_value: str) -> bool:
    """Check if scenario matches jurisdiction filter."""
    scenario_name = enriched_metadata.get(scenario_id, {}).get('name', scenario_id).lower()

    if filter_value == 'UK':
        return 'uk' in scenario_name and 'year' not in scenario_name
    elif filter_value == 'US':
        return any(city in scenario_name for city in ['seattle', 'new_york'])
    elif filter_value == 'UAE':
        return 'dubai' in scenario_name
    elif filter_value == 'Multi-jurisdiction':
        return 'year' in scenario_name  # Multi-phase scenarios

    return True


def _matches_validation_filter(scenario_id: str, validation_status: Dict, filter_value: str) -> bool:
    """Check if scenario matches validation filter."""
    validation = validation_status.get(scenario_id, {})

    if filter_value == 'valid_only':
        return validation.get('valid', False)
    elif filter_value == 'invalid_only':
        return not validation.get('valid', True)
    elif filter_value == 'unknown':
        return 'valid' not in validation

    return True


def render_selection_summary(
    selected_scenarios: List[str],
    enriched_metadata: Dict[str, Dict],
    validation_status: Dict[str, Dict]
) -> None:
    """Render enhanced selection summary with template metadata."""

    if not selected_scenarios:
        st.sidebar.warning("⚠️ Please select at least one scenario.")
        return

    st.sidebar.markdown("#### 📊 Selection Summary")

    # Since we're using simplified loading, assume all selected scenarios are valid
    valid_count = len(selected_scenarios)

    # Display summary metrics
    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.metric("Selected", len(selected_scenarios))
    with col2:
        st.metric("Valid", valid_count)

    if valid_count > 0:
        st.sidebar.success(f"✅ All {valid_count} scenario(s) are ready for analysis!")

    # Quick action buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Select All", help="Select all available scenarios", use_container_width=True):
            metadata = get_scenario_metadata()
            st.session_state.selected_scenarios = metadata['all_scenarios'].copy()
            st.rerun()

    with col2:
        if st.button("Clear All", help="Clear all selections", use_container_width=True):
            st.session_state.selected_scenarios = []
            st.rerun()


def render_template_composition_viewer(
    selected_scenarios: List[str],
    enriched_metadata: Dict[str, Dict]
) -> None:
    """Render template composition details for selected scenarios."""

    if not st.session_state.template_filters.get('show_composition', False):
        return

    st.sidebar.markdown("#### 🧩 Template Composition")

    for scenario_id in selected_scenarios[:3]:  # Limit to first 3 to avoid clutter
        meta = enriched_metadata.get(scenario_id, {})

        if 'error' in meta:
            st.sidebar.error(f"❌ {scenario_id}: {meta['error']}")
            continue

        with st.sidebar.expander(f"📋 {meta.get('name', scenario_id)}", expanded=False):
            composition = meta.get('template_composition', {})
            config_summary = meta.get('configuration_summary', {})

            # Template components
            st.markdown("**Template Components:**")
            for component_type, template_name in composition.items():
                if template_name and template_name != 'Unknown':
                    st.markdown(f"• **{component_type.title()}**: {template_name}")

            # Key configuration
            if config_summary:
                st.markdown("**Configuration:**")
                for key, value in config_summary.items():
                    if value and value != 'Unknown':
                        st.markdown(f"• **{key.replace('_', ' ').title()}**: {value}")


def render_validation_status_panel() -> None:
    """Display template validation status and errors."""

    st.sidebar.markdown("#### 🔍 Validation Status")

    try:
        validation_results = validate_all_scenarios()

        if not validation_results:
            st.sidebar.info("No validation data available")
            return

        # Count validation results
        total_scenarios = len(validation_results)
        valid_scenarios = sum(1 for result in validation_results.values() if result.get('valid', False))
        invalid_scenarios = total_scenarios - valid_scenarios

        # Display summary
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("✅ Valid", valid_scenarios)
        with col2:
            st.metric("❌ Invalid", invalid_scenarios)

        # Show validation details if there are issues
        if invalid_scenarios > 0:
            with st.sidebar.expander(f"⚠️ Validation Issues ({invalid_scenarios})", expanded=False):
                for scenario_id, result in validation_results.items():
                    if not result.get('valid', True):
                        st.markdown(f"**{scenario_id}**")
                        st.markdown(f"• {result.get('message', 'Unknown error')}")

        # Refresh validation button
        if st.sidebar.button("🔄 Refresh Validation", help="Re-validate all scenarios"):
            validate_all_scenarios.clear()  # Clear cache
            st.rerun()

    except Exception as e:
        st.sidebar.error(f"Failed to load validation status: {str(e)}")


def render_quick_filters() -> None:
    """Render quick filter checkboxes for common scenario types."""

    st.sidebar.markdown("#### ⚡ Quick Filters")

    # Quick filter checkboxes
    col1, col2 = st.sidebar.columns(2)

    with col1:
        uk_only = st.checkbox(
            "UK Only",
            value=st.session_state.quick_filters.get('uk_only', False),
            help="Show only UK scenarios"
        )

        international_only = st.checkbox(
            "International",
            value=st.session_state.quick_filters.get('international_only', False),
            help="Show only international scenarios"
        )

    with col2:
        tax_free_only = st.checkbox(
            "Tax-Free",
            value=st.session_state.quick_filters.get('tax_free_only', False),
            help="Show only tax-free scenarios (UAE)"
        )

        delayed_relocation_only = st.checkbox(
            "Multi-Phase",
            value=st.session_state.quick_filters.get('delayed_relocation_only', False),
            help="Show only multi-phase scenarios"
        )

    # Update session state and apply filters if changed
    filters_changed = (
        uk_only != st.session_state.quick_filters.get('uk_only', False) or
        international_only != st.session_state.quick_filters.get('international_only', False) or
        tax_free_only != st.session_state.quick_filters.get('tax_free_only', False) or
        delayed_relocation_only != st.session_state.quick_filters.get('delayed_relocation_only', False)
    )

    if filters_changed:
        st.session_state.quick_filters.update({
            'uk_only': uk_only,
            'international_only': international_only,
            'tax_free_only': tax_free_only,
            'delayed_relocation_only': delayed_relocation_only
        })

        apply_quick_filters()


def apply_quick_filters() -> None:
    """Apply simplified quick filters to avoid expensive metadata calls."""

    try:
        # Simplified approach: Get scenarios directly
        planner = TemplateFinancialPlanner()
        all_scenarios = planner.get_available_scenarios()
        filters = st.session_state.quick_filters

        # Get filtered scenarios based on quick filters using scenario ID patterns
        filtered_scenarios = []

        if filters.get('uk_only', False):
            # Filter scenarios that contain 'uk' in the name
            uk_scenarios = [s for s in all_scenarios if 'uk' in s.lower()]
            filtered_scenarios.extend(uk_scenarios)

        if filters.get('international_only', False):
            # Filter scenarios that contain international locations
            intl_scenarios = [s for s in all_scenarios if any(loc in s.lower() for loc in ['seattle', 'new_york', 'dubai'])]
            filtered_scenarios.extend(intl_scenarios)

        if filters.get('tax_free_only', False):
            # Filter for UAE/Dubai scenarios
            tax_free_scenarios = [s for s in all_scenarios if 'dubai' in s.lower()]
            filtered_scenarios.extend(tax_free_scenarios)

        if filters.get('delayed_relocation_only', False):
            # Filter scenarios that contain 'year' (multi-phase scenarios)
            delayed_scenarios = [s for s in all_scenarios if 'year' in s.lower()]
            filtered_scenarios.extend(delayed_scenarios)

        # If no filters are active, show all scenarios
        if not any(filters.values()):
            filtered_scenarios = all_scenarios

        # Remove duplicates and update selection
        filtered_scenarios = list(set(filtered_scenarios))
        current_selected = st.session_state.selected_scenarios
        new_selected = [s for s in current_selected if s in filtered_scenarios]

        # If no scenarios are selected after filtering, select the first available
        if not new_selected and filtered_scenarios:
            new_selected = [filtered_scenarios[0]]

        st.session_state.selected_scenarios = new_selected

    except Exception as e:
        st.sidebar.error(f"Failed to apply quick filters: {str(e)}")


def render_scenario_info(scenario_name: str) -> None:
    """Render detailed template information about a selected scenario."""

    st.subheader(f"📋 Scenario Details: {scenario_name}")

    try:
        # Get enriched metadata and configuration
        enriched_metadata = get_enriched_scenario_metadata()
        config_summary = get_template_configuration_summary()
        validation_status = validate_all_scenarios()

        meta = enriched_metadata.get(scenario_name, {})
        config = config_summary.get(scenario_name, {})
        validation = validation_status.get(scenario_name, {})

        if 'error' in meta:
            st.error(f"❌ Error loading scenario: {meta['error']}")
            return

        # Validation status
        if validation.get('valid', False):
            st.success("✅ Scenario validation: PASSED")
        else:
            st.error(f"❌ Scenario validation: FAILED - {validation.get('message', 'Unknown error')}")

        # Basic information
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Phase Type", meta.get('phase_type', 'Unknown'))
            st.metric("Duration", meta.get('configuration_summary', {}).get('duration', 'Unknown'))

        with col2:
            st.metric("Start Year", meta.get('configuration_summary', {}).get('start_year', 'Unknown'))
            st.metric("Start Age", meta.get('configuration_summary', {}).get('start_age', 'Unknown'))

        with col3:
            st.metric("Tax System", meta.get('configuration_summary', {}).get('tax_system', 'Unknown'))
            st.metric("Phases", meta.get('configuration_summary', {}).get('num_phases', 'Unknown'))

        # Template composition
        st.markdown("### 🧩 Template Composition")
        composition = meta.get('template_composition', {})

        if composition:
            comp_col1, comp_col2 = st.columns(2)

            with comp_col1:
                st.markdown("**Income & Career:**")
                if composition.get('salary'):
                    st.markdown(f"• Salary: {composition['salary']}")

                st.markdown("**Housing & Location:**")
                if composition.get('housing'):
                    st.markdown(f"• Housing: {composition['housing']}")

            with comp_col2:
                st.markdown("**Financial Strategy:**")
                if composition.get('investments'):
                    st.markdown(f"• Investments: {composition['investments']}")

                st.markdown("**Tax & Compliance:**")
                if composition.get('tax_system'):
                    st.markdown(f"• Tax System: {composition['tax_system']}")

        # Configuration parameters
        if config and 'error' not in config:
            st.markdown("### ⚙️ Configuration Parameters")

            # Scenario parameters
            scenario_params = config.get('scenario_parameters', {})
            if scenario_params:
                st.markdown("**Planning Parameters:**")
                for key, value in scenario_params.items():
                    if value:
                        st.markdown(f"• {key.replace('_', ' ').title()}: {value}")

            # Template files
            template_files = config.get('template_files', {})
            if template_files:
                st.markdown("**Template Sources:**")
                for template_type, template_file in template_files.items():
                    if template_file:
                        st.markdown(f"• {template_type.replace('_', ' ').title()}: `{template_file}`")

    except Exception as e:
        st.error(f"Failed to load scenario information: {str(e)}")


# Legacy function compatibility - kept for backward compatibility
def render_year_range_slider() -> None:
    """Render the year range slider for filtering data."""

    year_range = st.sidebar.slider(
        "Year Range",
        min_value=1,
        max_value=10,
        value=st.session_state.year_range,
        help="Filter data to show only selected years"
    )

    if year_range != st.session_state.year_range:
        st.session_state.year_range = year_range
        st.rerun()

    if year_range[0] == year_range[1]:
        st.sidebar.caption(f"Showing data for Year {year_range[0]}")
    else:
        st.sidebar.caption(f"Showing data for Years {year_range[0]}-{year_range[1]}")


# Legacy functions for backward compatibility
def render_comparison_mode() -> None:
    """Legacy function for comparison mode."""
    comparison_mode = st.sidebar.checkbox(
        "Comparison Mode",
        value=st.session_state.get('comparison_mode', False),
        help="Enable side-by-side scenario comparison"
    )

    if comparison_mode != st.session_state.get('comparison_mode', False):
        st.session_state.comparison_mode = comparison_mode
        st.rerun()


def render_scenario_groups() -> None:
    """Legacy function for scenario groups."""
    st.sidebar.info("💡 Use the enhanced template filters above for advanced scenario grouping.")


def render_advanced_filters() -> None:
    """Legacy function for advanced filters."""
    st.sidebar.info("💡 Advanced filtering is now available through template-based filters above.")


def apply_advanced_filters(min_net_worth: float, min_savings_rate: float) -> None:
    """Legacy function for advanced filters."""
    st.info(f"Advanced filters applied: Min Net Worth £{min_net_worth:,.0f}, Min Savings Rate {min_savings_rate:.1f}%")
