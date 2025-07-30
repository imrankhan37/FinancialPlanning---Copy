# Scenario Configuration Structure

This directory contains complete scenario configurations in YAML format that match the current system exactly. Each scenario file is self-contained and includes all necessary information for financial planning calculations.

## Current System Scenarios

Based on analysis of `config.py` and `financial_planner_pydantic.py`, the following scenarios are currently used:

### UK Scenarios
1. **`uk_scenario_a.yaml`** - UK Scenario A (conservative progression)
2. **`uk_scenario_b.yaml`** - UK Scenario B (aggressive progression)

### International Scenarios (6 total)
3. **`seattle_uk_home.yaml`** - Seattle tech graduate buying UK home
4. **`seattle_local_home.yaml`** - Seattle tech graduate buying local home
5. **`new_york_uk_home.yaml`** - New York tech graduate buying UK home
6. **`new_york_local_home.yaml`** - New York tech graduate buying local home
7. **`dubai_uk_home.yaml`** - Dubai tech graduate buying UK home
8. **`dubai_local_home.yaml`** - Dubai tech graduate buying local home

### Delayed Relocation Scenarios (12 total)
9. **`seattle_year4_uk_home.yaml`** - Move to Seattle Year 4, buy UK home
10. **`seattle_year4_local_home.yaml`** - Move to Seattle Year 4, buy local home
11. **`seattle_year5_uk_home.yaml`** - Move to Seattle Year 5, buy UK home
12. **`seattle_year5_local_home.yaml`** - Move to Seattle Year 5, buy local home
13. **`new_york_year4_uk_home.yaml`** - Move to New York Year 4, buy UK home
14. **`new_york_year4_local_home.yaml`** - Move to New York Year 4, buy local home
15. **`new_york_year5_uk_home.yaml`** - Move to New York Year 5, buy UK home
16. **`new_york_year5_local_home.yaml`** - Move to New York Year 5, buy local home
17. **`dubai_year4_uk_home.yaml`** - Move to Dubai Year 4, buy UK home
18. **`dubai_year4_local_home.yaml`** - Move to Dubai Year 4, buy local home
19. **`dubai_year5_uk_home.yaml`** - Move to Dubai Year 5, buy UK home
20. **`dubai_year5_local_home.yaml`** - Move to Dubai Year 5, buy local home

## Structure Overview

Each scenario file follows this clean structure:

```yaml
scenario:
  id: "unique_scenario_id"
  name: "Human Readable Name"
  description: "Detailed description"
  version: "2.0.0"
  created: "2025-01-29"

location:
  name: "Location Name"
  currency: "CURRENCY"
  exchange_rate: 1.0
  tax_system: "tax_system_id"  # References external tax config

income:
  base_salary: 45000
  progression:
    type: "yearly_overrides"  # or "compound_rate"
    rates:
      1: { salary: 45000, bonus: 0.05, rsu: 0.15 }
      # ... year by year overrides
  rsu_config:
    vesting_schedule: "4_year_cliff"
    ipo_multiplier: 2.0

expenses:
  location_expenses:  # Rent, healthcare, general, retirement
    rent: { monthly: 2100, currency: "GBP" }
    healthcare: { monthly: 0, currency: "GBP" }
    general_expenses: { monthly: 1500, currency: "GBP" }
    retirement_contribution: { percentage: 0.05 }
  
  goals:  # Universal goal-based expenses
    university_fees: { year: 1, amount: 16800, currency: "GBP" }
    marriage: { total_cost: 70000, start_year: 3, end_year: 4, currency: "GBP" }
    child_costs: { start_year: 7, one_off_cost: 8500, ongoing_annual_cost: 10000, currency: "GBP" }
    personal_expenses: { year_1: 6000, year_2: 9000, default: 12000, currency: "GBP" }
    parental_support: { before_house: 12000, after_house: 12000, house_purchase_year: 5, currency: "GBP" }
    travel: { annual: 3000, currency: "GBP" }
    housing: { strategy: "uk_home", purchase_year: 5, base_price: 600000, currency: "GBP" }

assumptions:
  start_year: 2025
  plan_duration_years: 10
  # ... economic assumptions
```

## Multi-Phase Scenarios

For scenarios with location changes (like delayed relocation), use the `phases` structure:

```yaml
phases:
  uk_phase:
    location: { name: "United Kingdom", currency: "GBP", tax_system: "uk_income_tax_ni" }
    duration: 3
    income: { ... }
    expenses: { ... }
  
  seattle_phase:
    location: { name: "Seattle, WA, USA", currency: "USD", tax_system: "us_federal_state" }
    duration: 7
    income: { ... }
    expenses: { ... }
```

## Key Features

### 1. **Complete Self-Containment**
Each scenario file contains everything needed for calculations:
- Location and currency information
- Income progression with bonuses and RSUs
- Location-specific expenses (rent, healthcare, general)
- Universal goal-based expenses (marriage, children, housing)
- Economic assumptions

### 2. **Externalized Tax Systems**
Tax configurations are stored separately in `../tax_systems/`:
- **Reusability**: Same tax system used by multiple scenarios
- **Maintainability**: Tax changes only need to be updated in one place
- **Cleaner Scenarios**: Focus on location-specific and goal-based parameters
- **Professional Standard**: Follows separation of concerns principle

### 3. **Flexible Income Progression**
Two progression types supported:
- `yearly_overrides`: Explicit salary/bonus/rsu for each year
- `compound_rate`: Automatic progression with compound rate

### 4. **Universal vs Location-Specific Expenses**
- **Location expenses**: Rent, healthcare, general expenses, retirement contributions
- **Universal goals**: University fees, marriage, children, personal expenses, parental support, travel, housing

### 5. **Housing Strategies**
- `uk_home`: Buy UK home regardless of location (with rental income when abroad)
- `local_home`: Buy home in current location

## Current System Mapping

The scenarios in this directory exactly match what's used in the current system:

- **UK Scenarios**: `run_unified_scenario('A', CONFIG)` and `run_unified_scenario('B', CONFIG)`
- **International Scenarios**: `run_unified_international_scenario(location, CONFIG, housing_strategy)`
- **Delayed Relocation**: `run_unified_delayed_relocation_scenario(scenario_name, CONFIG)`

## Benefits of This Structure

1. **Professional Standard**: Each scenario is a complete, self-contained configuration
2. **Easy to Understand**: Clear separation of concerns (location, income, expenses, tax)
3. **Flexible**: Supports both simple and complex multi-phase scenarios
4. **Maintainable**: Changes to one scenario don't affect others
5. **Extensible**: Easy to add new scenarios or modify existing ones
6. **Version Controlled**: Each scenario has version and creation date
7. **Clean Architecture**: Tax systems externalized for reusability

## Usage

The financial planning system will load these YAML files and use them to generate complete financial projections, taking into account:
- Currency conversions
- Tax calculations (from external tax system files)
- Inflation adjustments
- Housing purchase timing
- Goal-based expense timing
- Multi-phase location changes 