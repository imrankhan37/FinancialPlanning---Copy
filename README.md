# Financial Planning Dashboard

A comprehensive financial planning dashboard built with Streamlit and Plotly, featuring unified data models and interactive visualizations for multi-jurisdiction financial scenarios.

## 🚀 Features

- **Unified Data Models**: Currency-agnostic Pydantic models for consistent data handling
- **Multi-Jurisdiction Support**: UK, US, UAE, and EU financial scenarios
- **Interactive Visualizations**: Plotly charts with drill-down capabilities
- **Performance Optimized**: Cached data loading and optimized currency conversions
- **Comprehensive Analysis**: Income breakdown, expense analysis, cash flow tracking
- **Real-time Monitoring**: Performance metrics and migration status tracking

## 📊 Analysis Capabilities

- **Time Series Analysis**: Net worth trajectories, income growth, savings patterns
- **Income & Expense Breakdown**: Hierarchical drill-down analysis with unified models
- **Performance Monitoring**: Real-time metrics and optimization tracking
- **Scenario Comparison**: Multi-scenario analysis with unified data access

## 🔄 Migration Status

### Phase 1: Foundation ✅ Complete
- [x] Unified data models with Pydantic
- [x] Currency-agnostic design
- [x] Performance optimizations
- [x] Comprehensive validation

### Phase 2: Gradual Migration ✅ Complete
- [x] Updated data loading utilities to use unified models
- [x] Updated UI components to use unified data access
- [x] Updated financial planner to generate unified data
- [x] Enhanced performance monitoring with unified metrics

### Phase 3: Legacy Removal ✅ Complete
- [x] Removed old financial data models
- [x] Cleaned up conversion utilities
- [x] Final performance optimization
- [x] Documentation updates

## 🎯 Migration Complete!

The application has successfully migrated to unified models throughout the entire codebase. All legacy code has been removed and the application now uses:

- **UnifiedFinancialData**: Single data structure for all scenarios
- **UnifiedFinancialScenario**: Consistent scenario management
- **CurrencyValue**: Currency-agnostic value handling
- **Performance Optimizations**: Cached conversions and optimized data access

## 🛠️ Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `streamlit run streamlit_app.py`

## 📁 Project Structure

```
FinancialPlanning/
├── models/                    # Unified data models
│   ├── unified_financial_data.py
│   ├── unified_helpers.py
│   └── performance_optimizations.py
├── pages/                    # Analysis pages
│   ├── 1_Time_Series_Analysis.py
│   ├── 2_Income_Expense_Breakdown.py
│   └── 3_Performance_Monitoring.py
├── utils/                    # Utility functions
├── components/               # UI components
├── financial_planner_pydantic.py  # Scenario generation
└── streamlit_app.py         # Main application
```

## 🎨 Key Technologies

- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualizations
- **Pydantic**: Data validation and serialization
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations

## 📈 Performance Features

- **Cached Data Loading**: Optimized scenario generation
- **Currency Conversion Cache**: Efficient multi-currency handling
- **Memory Optimization**: Streamlined data structures
- **Real-time Monitoring**: Performance metrics tracking

## 🔧 Configuration

The application uses a centralized configuration system with support for:
- Multiple jurisdictions (UK, US, UAE, EU)
- Various housing strategies
- Flexible tax systems
- Configurable investment parameters

## 📊 Data Models

All financial data is now represented using unified Pydantic models:
- **UnifiedFinancialData**: Single data point with all financial information
- **UnifiedFinancialScenario**: Complete scenario with multiple data points
- **CurrencyValue**: Currency-agnostic value representation
- **Breakdown Models**: Detailed income, expense, tax, and investment breakdowns

## 🚀 Getting Started

1. **Select Scenarios**: Choose which financial scenarios to analyze
2. **Set Year Range**: Define the analysis period
3. **Explore Analysis**: Navigate through different analysis pages
4. **Monitor Performance**: Track system performance and optimization metrics

The application is now fully optimized with unified models and ready for production use! 