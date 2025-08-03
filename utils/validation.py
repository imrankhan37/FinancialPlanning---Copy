"""
Validation utilities for the financial planning dashboard.
Enhanced with template-specific error handling and troubleshooting guidance.
"""

import streamlit as st
from typing import Dict, Any, List, Optional
import pandas as pd
from constants import ERROR_MESSAGES, SUCCESS_MESSAGES


def validate_session_state() -> bool:
    """
    Validate that required session state variables are initialized with template awareness.

    Returns:
        bool: True if session state is valid, False otherwise
    """
    try:
        required_keys = ['selected_scenarios', 'year_range']

        for key in required_keys:
            if key not in st.session_state:
                st.session_state[key] = [] if key == 'selected_scenarios' else [1, 10]

        # Template-specific session state validation
        template_keys = ['template_metadata_loaded', 'enriched_metadata', 'validation_status']
        for key in template_keys:
            if key not in st.session_state:
                if key == 'template_metadata_loaded':
                    st.session_state[key] = False
                else:
                    st.session_state[key] = {}

        return True
    except Exception as e:
        st.error(f"Session state validation failed: {e}")
        st.error("💡 **Troubleshooting**: Try refreshing the page or clearing browser cache")
        return False


def validate_scenario_data(scenarios: Dict[str, Any]) -> bool:
    """
    Validate that scenario data is properly structured with template validation.

    Args:
        scenarios: Dictionary of scenario data

    Returns:
        bool: True if data is valid, False otherwise
    """
    if not scenarios:
        st.warning("No scenarios provided for validation.")
        st.info("💡 **Troubleshooting**: Ensure scenarios are selected in the sidebar")
        return False

    try:
        for scenario_name, scenario in scenarios.items():
            if not hasattr(scenario, 'data_points'):
                st.error(f"Scenario {scenario_name} missing data_points attribute.")
                st.error("💡 **Template Issue**: This suggests a template loading problem")
                with st.expander("🔧 Template Troubleshooting"):
                    st.markdown("**Possible causes:**")
                    st.markdown("• Template YAML file is corrupted or missing")
                    st.markdown("• Template validation failed during loading")
                    st.markdown("• Template inheritance chain is broken")
                    st.markdown("**Solutions:**")
                    st.markdown("• Check template validation status in sidebar")
                    st.markdown("• Verify YAML syntax in template files")
                    st.markdown("• Review template inheritance dependencies")
                return False

            if not scenario.data_points:
                st.warning(f"Scenario {scenario_name} has no data points.")
                st.info("💡 **Template Issue**: This scenario may have calculation errors")
                with st.expander("🔧 Calculation Troubleshooting"):
                    st.markdown("**Possible causes:**")
                    st.markdown("• Template parameters are invalid")
                    st.markdown("• Required template components are missing")
                    st.markdown("• Calculation engine failed to process scenario")
                    st.markdown("**Solutions:**")
                    st.markdown("• Review scenario configuration in template files")
                    st.markdown("• Check template validation results")
                    st.markdown("• Verify all required templates are available")
                continue

            # Validate each data point with template context
            for i, point in enumerate(scenario.data_points):
                if not _validate_data_point(point, scenario_name, i):
                    return False
        return True
    except Exception as e:
        st.error(f"Scenario data validation failed: {e}")
        _show_template_error_guidance(e)
        return False


def _validate_data_point(point, scenario_name: str, index: int) -> bool:
    """Validate individual data point with enhanced error context."""
    try:
        # Check for required attributes
        required_attrs = ['net_worth', 'income', 'tax', 'expenses']

        for attr in required_attrs:
            if not hasattr(point, attr):
                st.error(f"Data point {index} in scenario {scenario_name} missing '{attr}' attribute.")
                st.error("💡 **Template Data Issue**: Financial calculation incomplete")
                with st.expander("🔧 Data Point Troubleshooting"):
                    st.markdown(f"**Missing attribute**: `{attr}`")
                    st.markdown("**Possible causes:**")
                    st.markdown("• Template calculation logic is incomplete")
                    st.markdown("• Required input parameters are missing")
                    st.markdown("• Template composition has gaps")
                    st.markdown("**Solutions:**")
                    st.markdown("• Check template configuration for completeness")
                    st.markdown("• Verify all template dependencies are satisfied")
                    st.markdown("• Review calculation engine logs")
                return False

        return True
    except Exception as e:
        st.error(f"Data point validation failed: {e}")
        _show_template_error_guidance(e)
        return False


def _show_template_error_guidance(error: Exception):
    """Show template-specific error guidance based on error type."""
    error_str = str(error).lower()

    with st.expander("🆘 Template Error Guidance", expanded=True):
        if "yaml" in error_str or "template" in error_str:
            st.markdown("### 📄 YAML/Template Error")
            st.markdown("**Common solutions:**")
            st.markdown("• Check YAML syntax for missing colons, quotes, or indentation")
            st.markdown("• Verify template file paths and names")
            st.markdown("• Ensure all referenced templates exist")
            st.markdown("• Review template inheritance chain")

        elif "validation" in error_str:
            st.markdown("### ✅ Validation Error")
            st.markdown("**Common solutions:**")
            st.markdown("• Check template validation status in sidebar")
            st.markdown("• Review required parameters in template schemas")
            st.markdown("• Verify data types match schema expectations")
            st.markdown("• Ensure all mandatory fields are provided")

        elif "calculation" in error_str or "math" in error_str:
            st.markdown("### 🧮 Calculation Error")
            st.markdown("**Common solutions:**")
            st.markdown("• Check for division by zero in template parameters")
            st.markdown("• Verify numeric values are within expected ranges")
            st.markdown("• Review financial calculation logic")
            st.markdown("• Ensure currency conversion rates are available")

        elif "import" in error_str or "module" in error_str:
            st.markdown("### 📦 Import/Module Error")
            st.markdown("**Common solutions:**")
            st.markdown("• Verify all required dependencies are installed")
            st.markdown("• Check Python path configuration")
            st.markdown("• Ensure template engine modules are available")
            st.markdown("• Review system requirements")

        else:
            st.markdown("### ❓ General Error")
            st.markdown("**General troubleshooting steps:**")
            st.markdown("• Clear cache and reload data")
            st.markdown("• Check system resources (memory, CPU)")
            st.markdown("• Review error logs for more details")
            st.markdown("• Try with a smaller subset of scenarios")

        # Add quick actions
        st.markdown("### 🛠️ Quick Actions")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Reload Templates"):
                if 'template_metadata_loaded' in st.session_state:
                    st.session_state.template_metadata_loaded = False
                st.success("Templates will reload on next action")

        with col2:
            if st.button("🧹 Clear Cache"):
                try:
                    from utils.data import clear_cache
                    clear_cache()
                    st.success("Cache cleared successfully")
                except Exception:
                    st.error("Failed to clear cache")

        with col3:
            if st.button("✅ Validate All"):
                try:
                    from utils.data import validate_all_scenarios
                    validate_all_scenarios.clear()  # Clear cache
                    st.success("Validation will run on next action")
                except Exception:
                    st.error("Failed to trigger validation")


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling division by zero with enhanced error context.

    Args:
        numerator: The numerator value
        denominator: The denominator value
        default: Default value to return if denominator is zero

    Returns:
        float: The result of the division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError) as e:
        st.warning(f"Mathematical operation failed: {e}")
        st.info("💡 **Calculation Issue**: Using default value to continue")
        return default
    except Exception as e:
        st.error(f"Unexpected calculation error: {e}")
        _show_template_error_guidance(e)
        return default


def validate_numeric_value(value: Any, min_value: Optional[float] = None,
                          max_value: Optional[float] = None) -> bool:
    """
    Validate that a value is numeric and within specified bounds with template context.

    Args:
        value: The value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        bool: True if value is valid, False otherwise
    """
    try:
        numeric_value = float(value)

        if min_value is not None and numeric_value < min_value:
            st.error(f"Value {numeric_value} is below minimum {min_value}")
            st.info("💡 **Template Parameter Issue**: Check template configuration ranges")
            return False

        if max_value is not None and numeric_value > max_value:
            st.error(f"Value {numeric_value} exceeds maximum {max_value}")
            st.info("💡 **Template Parameter Issue**: Check template configuration limits")
            return False

        return True
    except (TypeError, ValueError) as e:
        st.error(f"Invalid numeric value: {value}")
        st.error("💡 **Template Data Issue**: Expected numeric value in template")
        with st.expander("🔧 Numeric Validation Help"):
            st.markdown("**Common issues:**")
            st.markdown("• Template contains non-numeric strings")
            st.markdown("• Currency symbols not properly handled")
            st.markdown("• Missing or null values in template")
            st.markdown("**Solutions:**")
            st.markdown("• Check template YAML for proper numeric formatting")
            st.markdown("• Ensure currency values use numeric format")
            st.markdown("• Verify all required parameters are provided")
        return False


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that a DataFrame has the required columns with template awareness.

    Args:
        df: The DataFrame to validate
        required_columns: List of required column names

    Returns:
        bool: True if DataFrame is valid, False otherwise
    """
    try:
        if df is None or df.empty:
            st.error("DataFrame is empty or None")
            st.info("💡 **Data Loading Issue**: Template calculation may have failed")
            with st.expander("🔧 DataFrame Troubleshooting"):
                st.markdown("**Possible causes:**")
                st.markdown("• No valid scenarios were loaded")
                st.markdown("• Template calculations failed for all scenarios")
                st.markdown("• Data filtering removed all records")
                st.markdown("**Solutions:**")
                st.markdown("• Check scenario selection and filters")
                st.markdown("• Verify template validation status")
                st.markdown("• Review calculation engine logs")
            return False

        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            st.error("💡 **Template Structure Issue**: Template output structure mismatch")
            with st.expander("🔧 Column Validation Help"):
                st.markdown(f"**Expected columns**: {required_columns}")
                st.markdown(f"**Available columns**: {list(df.columns)}")
                st.markdown("**Possible causes:**")
                st.markdown("• Template output format has changed")
                st.markdown("• Template calculation logic is incomplete")
                st.markdown("• Data processing pipeline has errors")
                st.markdown("**Solutions:**")
                st.markdown("• Check template output structure")
                st.markdown("• Verify calculation engine configuration")
                st.markdown("• Review data processing steps")
            return False

        return True
    except Exception as e:
        st.error(f"DataFrame validation failed: {e}")
        _show_template_error_guidance(e)
        return False


def handle_data_loading_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Handle data loading errors with appropriate user feedback and template-specific guidance.

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    error_message = f"Error loading data{f' in {context}' if context else ''}: {error}"
    st.error(error_message)

    # Provide helpful suggestions based on error type
    error_str = str(error).lower()

    if "template" in error_str or "yaml" in error_str:
        st.error("🔧 **Template System Issue Detected**")
        with st.expander("📋 Template Error Details", expanded=True):
            st.markdown("**Error Type**: Template/YAML Processing")
            st.markdown(f"**Context**: {context or 'Unknown'}")
            st.markdown("**Immediate Actions**:")
            st.markdown("• Check template validation status in sidebar")
            st.markdown("• Verify YAML file syntax and structure")
            st.markdown("• Ensure all referenced templates exist")
            st.markdown("• Review template inheritance chain")

    elif "validation" in error_str:
        st.error("✅ **Template Validation Issue**")
        with st.expander("🔍 Validation Error Details", expanded=True):
            st.markdown("**Error Type**: Template Validation Failure")
            st.markdown("**Immediate Actions**:")
            st.markdown("• Run template validation from sidebar")
            st.markdown("• Check required parameters in templates")
            st.markdown("• Verify data types and value ranges")
            st.markdown("• Review template schema compliance")

    elif "connection" in error_str or "network" in error_str:
        st.error("🌐 **Network/Connection Issue**")
        st.info("**Immediate Actions**: Check internet connection and retry")

    elif "memory" in error_str or "resource" in error_str:
        st.error("💾 **System Resource Issue**")
        with st.expander("🚀 Resource Optimization", expanded=True):
            st.markdown("**Immediate Actions**:")
            st.markdown("• Clear cache to free memory")
            st.markdown("• Reduce number of selected scenarios")
            st.markdown("• Close other applications")
            st.markdown("• Try with smaller year range")

    else:
        st.error("❓ **General System Issue**")
        with st.expander("🔧 General Troubleshooting", expanded=True):
            st.markdown("**Try these steps in order**:")
            st.markdown("1. Refresh the page")
            st.markdown("2. Clear cache and reload")
            st.markdown("3. Check system requirements")
            st.markdown("4. Contact support if issue persists")


def validate_user_inputs(selected_scenarios: List[str], year_range: List[int]) -> bool:
    """
    Validate user inputs from the interface with template awareness.

    Args:
        selected_scenarios: List of selected scenario names
        year_range: List containing start and end years

    Returns:
        bool: True if inputs are valid, False otherwise
    """
    try:
        # Validate scenarios selection
        if not selected_scenarios:
            st.warning("Please select at least one scenario to analyze.")
            st.info("💡 **Template Selection**: Use the enhanced scenario selector in the sidebar")
            with st.expander("🎯 Scenario Selection Help"):
                st.markdown("**How to select scenarios:**")
                st.markdown("• Use the multi-select dropdown in sidebar")
                st.markdown("• Filter by template type, phase, or validation status")
                st.markdown("• Check template composition viewer for details")
                st.markdown("• Ensure selected scenarios are validated")
            return False

        # Validate year range
        if len(year_range) != 2:
            st.error("Year range must contain exactly two values.")
            st.info("💡 **Range Selection**: Use the year range slider in sidebar")
            return False

        start_year, end_year = year_range
        if not validate_numeric_value(start_year, min_value=1):
            st.error("Start year must be a positive number.")
            return False

        if not validate_numeric_value(end_year, min_value=start_year):
            st.error("End year must be greater than or equal to start year.")
            return False

        # Template-specific validation
        try:
            from utils.data import get_enriched_scenario_metadata, validate_all_scenarios

            # Check if selected scenarios exist and are valid
            enriched_metadata = get_enriched_scenario_metadata()
            validation_status = validate_all_scenarios()

            invalid_scenarios = []
            for scenario_name in selected_scenarios:
                # Find scenario in metadata
                found = False
                for scenario_id, meta in enriched_metadata.items():
                    if meta.get('name', scenario_id) == scenario_name:
                        found = True
                        if not validation_status.get(scenario_id, {}).get('valid', False):
                            invalid_scenarios.append(scenario_name)
                        break

                if not found:
                    invalid_scenarios.append(scenario_name)

            if invalid_scenarios:
                st.warning(f"⚠️ Some selected scenarios have validation issues: {', '.join(invalid_scenarios)}")
                st.info("💡 **Template Validation**: Check validation status in sidebar for details")

                # Show validation details
                with st.expander("🔍 Validation Issues Details"):
                    for scenario in invalid_scenarios:
                        for scenario_id, meta in enriched_metadata.items():
                            if meta.get('name', scenario_id) == scenario:
                                validation_result = validation_status.get(scenario_id, {})
                                st.markdown(f"**{scenario}**: {validation_result.get('message', 'Unknown validation issue')}")
                                break

                # Allow user to continue with warning
                if st.checkbox("Continue with invalid scenarios (may cause errors)"):
                    st.warning("Proceeding with potentially invalid scenarios")
                else:
                    return False

        except Exception as e:
            st.warning(f"Could not validate template status: {e}")
            st.info("💡 **Template Check**: Continuing without template validation")

        return True
    except Exception as e:
        st.error(f"Input validation failed: {e}")
        _show_template_error_guidance(e)
        return False


def log_validation_error(error: Exception, context: Optional[str] = None) -> None:
    """
    Log validation errors for debugging purposes with template context.

    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    # In a production environment, this would log to a file or monitoring service
    error_context = f" in {context}" if context else ""
    print(f"Validation Error{error_context}: {error}")

    # Also log template-specific context if available
    try:
        if hasattr(st.session_state, 'enriched_metadata'):
            print(f"Template metadata available: {len(st.session_state.enriched_metadata)} scenarios")
        if hasattr(st.session_state, 'validation_status'):
            valid_count = sum(1 for v in st.session_state.validation_status.values() if v.get('valid', False))
            print(f"Template validation: {valid_count}/{len(st.session_state.validation_status)} valid")
    except Exception:
        pass  # Don't fail on logging


def create_error_summary(errors: List[str]) -> str:
    """
    Create a summary of validation errors with template-specific context.

    Args:
        errors: List of error messages

    Returns:
        str: Formatted error summary
    """
    if not errors:
        return "No validation errors found."

    summary = "Template Validation Error Summary:\n"
    template_errors = []
    general_errors = []

    # Categorize errors
    for error in errors:
        if any(keyword in error.lower() for keyword in ['template', 'yaml', 'validation', 'calculation']):
            template_errors.append(error)
        else:
            general_errors.append(error)

    # Add template-specific errors first
    if template_errors:
        summary += "\n🔧 Template-Related Issues:\n"
        for i, error in enumerate(template_errors, 1):
            summary += f"{i}. {error}\n"

    # Add general errors
    if general_errors:
        summary += "\n❓ General Issues:\n"
        for i, error in enumerate(general_errors, len(template_errors) + 1):
            summary += f"{i}. {error}\n"

    # Add troubleshooting guidance
    summary += "\n💡 Troubleshooting Tips:\n"
    summary += "• Check template validation status in sidebar\n"
    summary += "• Clear cache and reload data\n"
    summary += "• Verify template file integrity\n"
    summary += "• Review system requirements\n"

    return summary


def validate_template_system() -> Dict[str, Any]:
    """
    Validate the overall template system health and return status.

    Returns:
        Dict containing validation results and recommendations
    """
    try:
        from utils.data import get_enriched_scenario_metadata, validate_all_scenarios
        from financial_planner_template_driven import TemplateFinancialPlanner

        # Initialize components
        planner = TemplateFinancialPlanner()

        # Test basic functionality
        scenarios = planner.get_available_scenarios()
        metadata = get_enriched_scenario_metadata()
        validation = validate_all_scenarios()

        # Calculate health metrics
        total_scenarios = len(scenarios)
        valid_scenarios = sum(1 for v in validation.values() if v.get('valid', False))
        metadata_coverage = len(metadata)

        validation_rate = (valid_scenarios / max(total_scenarios, 1)) * 100
        metadata_rate = (metadata_coverage / max(total_scenarios, 1)) * 100

        # Determine overall health
        if validation_rate >= 90 and metadata_rate >= 90:
            health_status = "Excellent"
            health_color = "success"
        elif validation_rate >= 75 and metadata_rate >= 75:
            health_status = "Good"
            health_color = "info"
        elif validation_rate >= 50 and metadata_rate >= 50:
            health_status = "Fair"
            health_color = "warning"
        else:
            health_status = "Poor"
            health_color = "error"

        return {
            'status': health_status,
            'color': health_color,
            'total_scenarios': total_scenarios,
            'valid_scenarios': valid_scenarios,
            'validation_rate': validation_rate,
            'metadata_coverage': metadata_coverage,
            'metadata_rate': metadata_rate,
            'recommendations': _get_health_recommendations(validation_rate, metadata_rate)
        }

    except Exception as e:
        return {
            'status': 'Error',
            'color': 'error',
            'error': str(e),
            'recommendations': ['Fix template system initialization', 'Check system dependencies']
        }


def _get_health_recommendations(validation_rate: float, metadata_rate: float) -> List[str]:
    """Get health recommendations based on metrics."""
    recommendations = []

    if validation_rate < 75:
        recommendations.append("Review and fix template validation issues")
        recommendations.append("Check YAML syntax and template dependencies")

    if metadata_rate < 75:
        recommendations.append("Improve template metadata loading")
        recommendations.append("Verify template configuration completeness")

    if validation_rate >= 90 and metadata_rate >= 90:
        recommendations.append("Template system is healthy - continue monitoring")

    return recommendations or ["No specific recommendations - system appears healthy"]
