# Financial Planning Dashboard

A comprehensive financial planning and analysis dashboard built with Streamlit, featuring multi-scenario analysis, interactive visualizations, and professional styling.

## 🚀 Features

### 📊 **Multi-Scenario Analysis**
- **UK Scenarios**: Traditional UK-based financial planning
- **International Scenarios**: US, UAE, and other international locations
- **Delayed Relocation**: Scenarios with UK experience before international move
- **Tax Optimization**: Different tax jurisdictions and strategies

### 🎨 **Professional UI/UX**
- **Unified CSS Architecture**: Organized styling with component-based loading
- **Interactive Charts**: Plotly-powered visualizations with hover effects
- **Responsive Design**: Mobile-friendly interface
- **Performance Metrics**: KPI cards with gradient styling

### 📈 **Analysis Capabilities**
- **Time Series Analysis**: Net worth, income, and savings trajectories
- **Income/Expense Breakdown**: Detailed component analysis
- **Performance Monitoring**: Scenario comparison and ranking
- **Cash Flow Analysis**: Net cash flow and ratio calculations

## 🏗️ Architecture

### **Core Components**
```
├── streamlit_app.py          # Main application entry point
├── financial_planner_pydantic.py  # Core financial calculation engine
├── models/                   # Pydantic data models
│   ├── financial_data.py     # Unified data structures
│   └── scenario_builder.py   # Scenario construction helpers
├── pages/                    # Streamlit page modules
│   ├── 1_Time_Series_Analysis.py
│   ├── 2_Income_Expense_Breakdown.py
│   └── 3_Performance_Monitoring.py
├── components/               # Reusable UI components
├── utils/                    # Utility functions
├── static/css/              # CSS architecture
└── config.py                # Configuration management
```

### **Data Model**
- **Unified Financial Data**: Currency-agnostic with GBP conversion
- **Pydantic Validation**: Type-safe data structures
- **Scenario Metadata**: Rich scenario comparison capabilities

## 🛠️ Installation

### **Prerequisites**
- Python 3.8+
- pip

### **Setup**
```bash
# Clone the repository
git clone <repository-url>
cd FinancialPlanning-Dashboard

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

### **Environment Setup**
```bash
# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### **Starting the Dashboard**
```bash
# Default port (8501)
streamlit run streamlit_app.py

# Custom port
streamlit run streamlit_app.py --server.port 8520
```

### **Accessing the Dashboard**
- **Local**: http://localhost:8501
- **Network**: http://your-ip:8501

## 📊 Key Features

### **Scenario Analysis**
- **UK Scenarios**: A and B with different growth trajectories
- **International Scenarios**: US, UAE, and other locations
- **Delayed Relocation**: UK experience before international move
- **Housing Strategies**: UK home vs local home options

### **Financial Metrics**
- **Net Worth Tracking**: Real-time net worth calculations
- **Income Analysis**: Salary, bonus, and RSU breakdown
- **Expense Tracking**: Detailed expense categorization
- **Tax Optimization**: Multi-jurisdiction tax planning
- **Investment Strategies**: Retirement and taxable accounts

### **Visualizations**
- **Interactive Charts**: Plotly-powered with hover effects
- **Performance Tables**: Styled with pandas Styler
- **KPI Cards**: Gradient-styled key performance indicators
- **Comparison Views**: Side-by-side scenario analysis

## 🎨 CSS Architecture

### **Component-Based Styling**
```python
from utils.css_loader import load_component_styles

# Load specific components
load_component_styles(["kpi_cards", "enhanced_tables"])
```

### **Available Components**
- **`kpi_cards`**: Key Performance Indicator cards
- **`enhanced_tables`**: Professional table styling
- **`metric_highlights`**: Color-coded metric containers
- **`streamlit_components`**: Enhanced Streamlit UI elements

### **Design System**
- **Color Palette**: Purple-blue gradients, success blues, warning pinks
- **Typography**: Consistent font weights and spacing
- **Spacing**: Standardized 4px, 8px, 16px, 24px system
- **Border Radius**: 8px, 10px, 15px for different elements

## 🔧 Configuration

### **Financial Parameters**
Edit `config.py` to customize:
- Tax rates and thresholds
- Salary progression paths
- Investment return rates
- Inflation assumptions
- Exchange rates

### **Scenario Configuration**
```python
# UK Scenarios
UK_Scenario_A: Internal growth path
UK_Scenario_B: External growth path

# International Scenarios
Seattle, New York, Dubai: Different tax jurisdictions

# Delayed Relocation
Year4/Year5: Different timing for international move
```

## 📈 Data Model

### **Unified Financial Data**
```python
class FinancialDataPoint(BaseModel):
    # Core metadata
    year: int
    age: int
    phase: Phase  # UK or INTERNATIONAL
    
    # Multi-currency support
    net_worth_gbp_equiv: float
    gross_income_gbp_equiv: float
    annual_savings_gbp_equiv: float
    
    # Detailed breakdowns
    expenses: Dict[str, float]
    investments: Dict[str, float]
    tax: Dict[str, float]
```

### **Scenario Structure**
```python
class FinancialScenario(BaseModel):
    name: str
    data_points: List[FinancialDataPoint]
    
    def get_final_net_worth(self) -> float:
        # Unified access to net worth in GBP
        pass
```

## 🧪 Testing

### **Running Tests**
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_financial_models.py

# Run with coverage
python -m pytest --cov=.
```

### **Test Structure**
```
tests/
├── test_financial_models.py
├── test_scenario_builder.py
├── test_utils.py
└── test_integration.py
```

## 📚 Documentation

### **Architecture Documentation**
- **CSS Architecture**: `static/css/README.md`
- **Data Models**: `models/README.md`
- **API Reference**: `docs/api.md`

### **User Guides**
- **Getting Started**: `docs/getting_started.md`
- **Scenario Configuration**: `docs/scenarios.md`
- **Customization**: `docs/customization.md`

## 🤝 Contributing

### **Development Setup**
```bash
# Fork the repository
git clone <your-fork-url>
cd FinancialPlanning-Dashboard

# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create pull request
git push origin feature/new-feature
```

### **Code Style**
- **Python**: PEP 8 with Black formatting
- **CSS**: BEM methodology for component naming
- **Documentation**: Google-style docstrings

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing dashboard framework
- **Plotly**: For interactive visualizations
- **Pydantic**: For data validation and serialization
- **Pandas**: For data manipulation and analysis

## 📞 Support

For questions, issues, or contributions:
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: your-email@example.com

---

**Built with ❤️ for financial planning and analysis** 