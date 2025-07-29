"""
Constants and configuration values for the Financial Planning Dashboard.
"""

# Currency conversion rates
USD_TO_GBP_RATE = 1.26
GBP_TO_USD_RATE = 1 / USD_TO_GBP_RATE

# Default values
DEFAULT_YEAR_RANGE = (1, 10)
DEFAULT_SCENARIOS = []

# Performance thresholds
MEMORY_WARNING_THRESHOLD = 80.0  # Percentage
CPU_WARNING_THRESHOLD = 90.0      # Percentage

# Financial thresholds
HIGH_NET_WORTH_THRESHOLD = 1000000  # £1M
MEDIUM_NET_WORTH_THRESHOLD = 500000  # £500K
HIGH_GROWTH_THRESHOLD = 50.0        # 50%
MEDIUM_GROWTH_THRESHOLD = 20.0      # 20%
HIGH_SAVINGS_RATE_THRESHOLD = 30.0  # 30%
MEDIUM_SAVINGS_RATE_THRESHOLD = 15.0  # 15%
HIGH_CASH_FLOW_RATIO_THRESHOLD = 20.0  # 20%
MEDIUM_CASH_FLOW_RATIO_THRESHOLD = 10.0  # 10%

# Styling constants
GRADIENT_COLORS = {
    'primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'success': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'info': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'warning': 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    'danger': 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)'
}

# Error messages
ERROR_MESSAGES = {
    'session_state_missing': 'Session state not initialized. Please refresh the page.',
    'data_loading_failed': 'Failed to load scenario data. Please try again.',
    'validation_failed': 'Data validation failed. Please check your inputs.',
    'division_by_zero': 'Cannot calculate percentage: denominator is zero.',
    'missing_data': 'Required data is missing for this calculation.'
}

# Success messages
SUCCESS_MESSAGES = {
    'data_loaded': 'Data loaded successfully!',
    'calculation_complete': 'Calculations completed successfully!',
    'validation_passed': 'Data validation passed!'
} 