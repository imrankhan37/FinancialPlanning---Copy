# Tax System Configurations

This directory contains static tax system configurations that are referenced by scenario files. Tax systems are separated from scenarios because they don't change over time and can be reused across multiple scenarios.

## Available Tax Systems

### 1. **`uk_income_tax_ni.yaml`** - UK Income Tax + National Insurance
- **Location**: United Kingdom
- **Currency**: GBP
- **Components**: Income tax, National Insurance, Student Loan (Plan 2)
- **Features**: Progressive tax bands, NI contributions, student loan repayment
- **2025/26 Rates**: Personal Allowance £12,570, Basic Rate 20%, Higher Rate 40%, Additional Rate 45%

### 2. **`us_federal.yaml`** - US Federal Tax (Base)
- **Location**: United States (base configuration)
- **Currency**: USD
- **Components**: Federal income tax, FICA (Social Security + Medicare)
- **Features**: Progressive federal brackets, social security, medicare
- **2025 Rates**: Standard Deduction $15,000, Social Security Limit $168,600
- **Usage**: Extended by state-specific configurations

### 3. **`us_states/`** - US State Tax Configurations
- **Location**: Various US states
- **Currency**: USD
- **Components**: Extends federal tax + state-specific taxes
- **Features**: Modular state tax system
- **Available States**:
  - `washington.yaml` - No state tax (Seattle)
  - `new_york.yaml` - State + city tax (NYC)
  - `california.yaml` - High state tax (San Francisco, LA)
  - `texas.yaml` - No state tax (Austin, Dallas)

### 4. **`tax_free.yaml`** - Tax Free (Dubai)
- **Location**: Dubai, UAE
- **Currency**: USD
- **Components**: No income tax, no social security
- **Features**: Zero income tax, zero social security contributions

## Structure

Each tax system file follows this structure:

```yaml
tax_system:
  id: "tax_system_id"
  name: "Human Readable Name"
  description: "Detailed description"
  version: "2.0.0"
  created: "2025-01-29"
  currency: "CURRENCY"
  extends: "base_system"  # For US state systems

# Tax-specific configuration
income_tax:  # UK only
  # Tax bands, rates, etc.

national_insurance:  # UK only
  # NI bands and rates

federal:  # US only
  # Federal tax brackets

fica:  # US only
  # Social security and medicare

state:  # US states only
  # State tax configuration

city:  # NYC only
  # City tax configuration

student_loan:  # UK only
  # Student loan repayment configuration (Plan 2)
```

## Benefits of Separation

1. **Reusability**: Same tax system can be used by multiple scenarios
2. **Maintainability**: Tax changes only need to be updated in one place
3. **Cleaner Scenarios**: Focus on location-specific and goal-based parameters
4. **Version Control**: Tax systems can be versioned independently
5. **Professional Standard**: Follows separation of concerns principle
6. **Modularity**: US states extend base federal configuration

## Usage in Scenarios

Scenarios reference tax systems by ID:

```yaml
location:
  name: "United Kingdom"
  currency: "GBP"
  exchange_rate: 1.0
  tax_system: "uk_income_tax_ni"  # References external tax config

location:
  name: "Seattle, WA, USA"
  currency: "USD"
  exchange_rate: 1.26
  tax_system: "us_washington"  # References state-specific config
```

The financial planning system will load the appropriate tax configuration based on this reference.

## Adding New Tax Systems

### For New Countries:
1. Create a new YAML file in this directory
2. Follow the established structure
3. Include all necessary tax components
4. Update the scenario files to reference the new tax system ID
5. Update this README with the new system details

### For New US States:
1. Create a new YAML file in `us_states/` directory
2. Use `extends: "us_federal"` to inherit federal configuration
3. Add state-specific tax configuration
4. Update the `us_states/README.md`
5. Update scenario files to reference the new state system

## Recent Corrections (2025-01-29)

- **US FICA**: Updated Social Security limit to $168,600 (2025 rate)
- **Student Loans**: Removed UK student loan config from US/Dubai systems (location-specific)
- **Tax Rates**: Verified all rates match current 2025 tax year
- **US Structure**: Modularized US tax system with base federal + state-specific configurations 