# Configuration Architecture

## 🏗️ Optimal Configuration Structure

This document outlines the professional-grade configuration architecture that follows software engineering best practices for modularity, maintainability, and scalability.

## 📁 Directory Structure

```
config/
├── README.md                    # This file - architecture documentation
├── constants/                   # Immutable system constants
│   ├── currencies.yaml         # Currency definitions and exchange rates
│   ├── tax_bands.yaml          # Static tax thresholds and bands
│   └── defaults.yaml           # System-wide default values
├── markets/                     # Market-specific configurations
│   ├── locations/              # Location definitions
│   │   ├── uk.yaml            # UK market configuration
│   │   ├── us_washington.yaml  # Washington state configuration
│   │   ├── us_new_york.yaml   # New York configuration
│   │   └── uae_dubai.yaml     # Dubai configuration
│   ├── housing/               # Housing market definitions
│   │   ├── uk_residential.yaml
│   │   ├── us_seattle.yaml
│   │   └── us_new_york.yaml
│   └── tax_systems/           # Tax system definitions (current structure)
├── templates/                  # Reusable configuration templates
│   ├── salary_progressions/   # Salary progression templates
│   │   ├── conservative.yaml  # Conservative growth template
│   │   ├── aggressive.yaml    # Aggressive growth template
│   │   └── tech_worker.yaml   # Tech industry specific
│   ├── expense_profiles/      # Expense profile templates
│   │   ├── graduate.yaml     # Fresh graduate expenses
│   │   ├── mid_career.yaml   # Mid-career professional
│   │   └── senior.yaml       # Senior professional
│   └── life_events/          # Life event templates
│       ├── marriage.yaml     # Marriage cost templates
│       ├── children.yaml     # Child-related expenses
│       └── education.yaml    # Education expenses
├── scenarios/                 # Scenario instances (current structure)
└── schema/                   # Configuration schemas and validation
    ├── location.schema.yaml  # Location configuration schema
    ├── scenario.schema.yaml  # Scenario configuration schema
    └── template.schema.yaml  # Template configuration schema
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
- **Constants**: Immutable system values (tax rates, currency codes)
- **Markets**: Location and market-specific configurations
- **Templates**: Reusable patterns and configurations
- **Scenarios**: Specific instances that compose templates and markets
- **Schema**: Validation rules and type definitions

### 2. **DRY (Don't Repeat Yourself)**
- Templates eliminate duplication across scenarios
- Market configurations shared across multiple scenarios
- Single source of truth for each type of configuration

### 3. **Composition Over Inheritance**
- Scenarios compose templates and market configs
- Templates can be mixed and matched
- Flexible combination of different configuration elements

### 4. **Schema-Driven Development**
- All configurations validated against schemas
- Type safety and consistency enforced
- Documentation generated from schemas

### 5. **Immutable Constants vs Mutable Instances**
- Constants (tax rates, currency codes) in separate directory
- Instance configurations (scenarios) reference constants
- Clear distinction between what changes and what doesn't

## 🔧 Configuration Composition

### Example Scenario Composition:

```yaml
# config/scenarios/uk_conservative_scenario.yaml
scenario:
  id: "uk_conservative"
  name: "UK Conservative Growth Scenario"
  version: "3.0.0"

composition:
  location: 
    market: "uk"                           # References config/markets/locations/uk.yaml
  
  salary_progression:
    template: "conservative"               # References config/templates/salary_progressions/conservative.yaml
    base_salary: 45000
    overrides:                             # Optional overrides to template
      year_3: { salary: 60000 }
  
  expense_profile:
    template: "graduate"                   # References config/templates/expense_profiles/graduate.yaml
    location_overrides:                    # Location-specific overrides
      rent: { monthly: 2100 }
  
  life_events:
    - template: "education"                # References config/templates/life_events/education.yaml
      year: 1
    - template: "marriage"                 # References config/templates/life_events/marriage.yaml
      start_year: 3
      end_year: 4
  
  housing:
    strategy: "uk_home"                    # References config/markets/housing/uk_residential.yaml
    purchase_year: 5

assumptions:
  start_year: 2025
  plan_duration_years: 10
  custom_inflation_rate: 0.025  # Override system default if needed
```

## 🏛️ Architecture Benefits

### 1. **Modularity**
- Each component serves a single purpose
- Components can be developed and tested independently
- Easy to swap out different templates or markets

### 2. **Maintainability**
- Changes to tax rates only need updating in constants
- Template updates apply to all scenarios using that template
- Clear structure makes debugging and updates straightforward

### 3. **Scalability**
- Adding new countries: Just add location and housing market configs
- Adding new scenario types: Create new templates
- Adding new life events: Create new life event templates

### 4. **Testability**
- Each component can be unit tested independently
- Schema validation ensures configuration integrity
- Template composition can be integration tested

### 5. **Documentation**
- Self-documenting through schema definitions
- Clear relationships between components
- Examples and templates serve as documentation

## 🔄 Migration Strategy

### Phase 1: Constants Extraction
1. Extract all static values (tax rates, currencies) to constants/
2. Update code to reference constants instead of hardcoded values

### Phase 2: Template Creation
1. Analyze existing scenarios to identify common patterns
2. Create reusable templates for salary progressions, expenses, life events
3. Update scenarios to reference templates

### Phase 3: Market Separation
1. Extract location-specific configurations to markets/
2. Create housing market configurations
3. Update scenarios to reference market configurations

### Phase 4: Schema Implementation
1. Define schemas for all configuration types
2. Implement validation in the application
3. Generate documentation from schemas

### Phase 5: Composition Implementation
1. Update scenario format to use composition
2. Implement template resolution logic
3. Update all existing scenarios to new format

## 📊 Performance Considerations

### 1. **Caching Strategy**
- Cache resolved configurations after composition
- Use configuration versioning for cache invalidation
- Lazy loading of unused templates and markets

### 2. **Memory Optimization**
- Load only required configurations
- Share immutable constants across scenarios
- Use weak references for large configuration objects

### 3. **Validation Performance**
- Schema validation only during configuration loading
- Pre-compiled schema validators
- Async validation for large configuration sets

## 🛡️ Type Safety & Validation

### 1. **Schema Definitions**
- JSON Schema or similar for all configuration types
- Runtime validation ensures data integrity
- IDE support through schema definitions

### 2. **Type Generation**
- Generate TypeScript/Python types from schemas
- Compile-time type checking where possible
- Auto-completion support in IDEs

### 3. **Configuration Linting**
- Automated checks for configuration consistency
- Validation of references between configurations
- Style guide enforcement for configuration files

This architecture provides a robust, maintainable, and scalable foundation for the financial planning system while following software engineering best practices. 