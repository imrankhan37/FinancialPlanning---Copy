"""
Financial Planning Configuration
Contains core configuration parameters for the financial planning scenarios.
Note: Many parameters have been moved to the new schema-driven architecture.
"""

CONFIG = {
    # Core Planning Parameters - Still used by financial_planner_pydantic.py
    "start_year": 2025,
    "plan_duration_years": 10,
    "start_age": 24,
    
    # Investment & Economic Parameters - Still used throughout system
    "investment_return_rate": 0.065,  # Used in scenario_helpers.py and financial_planner_pydantic.py
    
    # Inflation Configuration - Still used by uk_tax.py and financial_planner_pydantic.py
    "inflation_rate": 0.025,  # Base rate, used as fallback
    "inflation_path": {
        2025: 0.032,  # 3.2% for 2025
        2026: 0.022,  # 2.2% for 2026
        2027: 0.020,  # 2.0% thereafter
        "default": 0.020
    },
    
    # Student Loan - Still used by financial_planner_pydantic.py
    "student_loan_debt": 57000,  # Initial debt amount
    
    # UK Tax Configuration - Still used by utils/tax/uk_tax.py
    # Note: This will eventually be replaced by config/tax_systems/uk_income_tax_ni.yaml
    "tax_bands": {
        "personal_allowance": 12570,
        "basic_rate_limit": 50270,
        "higher_rate_limit": 125140,
        "pa_taper_threshold": 100000,
        "threshold_freeze_until": 2028
    },
    "tax_rates": {
        "basic": 0.20,
        "higher": 0.40,
        "additional": 0.45
    },
    "ni_bands": {
        "primary_threshold": 12570,
        "upper_earnings_limit": 50270
    },
    "ni_rates": {
        "main": 0.08,
        "upper": 0.02
    },
    
    # Student Loan Configuration - Still used by utils/tax/uk_tax.py
    "student_loan_plan2": {
        "threshold": 28470,
        "repayment_rate": 0.09,
        "interest_rate_rpi": 0.043,
        "interest_rate_max_premium": 0.03,
        "interest_lower_income_threshold": 28470,
        "interest_upper_income_threshold": 51245
    },
    
    # Investment Allowances - Still used by utils/tax/uk_tax.py
    "isa_allowance": 20000,
    "lisa_allowance": 4000,
    "lisa_bonus_rate": 0.25,
    "sipp_allowance": 60000,
    
    # Universal Life Events - Still used by utils/tax/tax_utils.py
    # Note: These are duplicated in the new templates but still needed for backward compatibility
    "university_fee_payment": {
        "year": 1,
        "amount": 16800,
        "payment_schedule": [5600, 5600, 5600]
    },
    "marriage_goal": {
        "total_cost": 70000,
        "start_year": 3,
        "end_year": 4
    },
    "child_costs": {
        "start_year": 7,
        "one_off_cost": 8500,
        "ongoing_annual_cost": 10000
    },
    "personal_expenses": {1: 6000, 2: 9000, "default": 12000},
    "parental_support": {
        "before_house": 12000,
        "after_house": 12000,
        "house_purchase_year": 5
    },
    "annual_travel": 3000,
    
    # UK Housing Configuration - Still used by utils/scenario_helpers.py
    # Note: This is duplicated in scenarios but needed for UK-only scenarios
    "parental_home_purchase": {
        "target_year": 4,  # Purchase takes place at the start of Year 5
        "price_grows": [0.01, 0.04, 0.06, 0.06],  # Savills forecast for 2025-2028
        "base_price_2025": 600000,
        "deposit_pct": 0.20,
        "mortgage_rate": 0.0525,
        "mortgage_term_years": 25
    },
    
    # Location-Specific Configurations - Still used by financial_planner_pydantic.py
    "location_configs": {
        "UK": {
            "name": "United Kingdom",
            "currency": "GBP",
            "exchange_rate": 1.0,
            "rent_monthly": 2100,
            "healthcare_monthly": 0,
            "retirement_contribution": 0.05,
            "general_expenses_monthly": 1500,
        }
    },
    
    # International Scenarios Configuration - Still used by financial_planner_pydantic.py
    "international_scenarios": {
        "seattle": {
            "name": "Seattle, WA, USA",
            "currency": "USD",
            "exchange_rate": 1.26,
            "salary_progression": {
                1: 100000, 2: 110000, 3: 120000, 4: 150000, 5: 180000,
                6: 200000, 7: 200000, 8: 220000, 9: 220000, 10: 240000
            },
            "bonus_rate": 0.1,
            "rsu_rate": 0.25,
            "tax_system": "us_federal_state",
            "rent_monthly": 2200,
            "healthcare_monthly": 500,
            "retirement_contribution": 0.06,
            "general_expenses_monthly": 2000,
            "relocation_cost": 11300,
            "housing_options": {
                "uk_home": {
                    "purchase_year": 5,
                    "price_gbp": 575000,
                    "price_growth": [0.01, 0.04, 0.06, 0.06],
                    "deposit_pct": 0.25,
                    "mortgage_rate": 0.0525,
                    "mortgage_term_years": 25
                },
                "local_home": {
                    "purchase_year": 3,
                    "price_usd": 750000,
                    "price_growth": [0.03, 0.04, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
                    "deposit_pct": 0.25,
                    "mortgage_rate": 0.065,
                    "mortgage_term_years": 30
                }
            }
        },
        "new_york": {
            "name": "New York, NY, USA",
            "currency": "USD",
            "exchange_rate": 1.26,
            "salary_progression": {
                1: 100000, 2: 120000, 3: 130000, 4: 150000, 5: 180000,
                6: 200000, 7: 200000, 8: 200000, 9: 230000, 10: 250000
            },
            "bonus_rate": 0.15,
            "rsu_rate": 0.25,
            "tax_system": "us_federal_state_city",
            "rent_monthly": 4000,
            "healthcare_monthly": 500,
            "retirement_contribution": 0.06,
            "general_expenses_monthly": 2500,
            "relocation_cost": 11300,
            "housing_options": {
                "uk_home": {
                    "purchase_year": 5,
                    "price_gbp": 575000,
                    "price_growth": [0.01, 0.04, 0.06, 0.06],
                    "deposit_pct": 0.20,
                    "mortgage_rate": 0.0525,
                    "mortgage_term_years": 25
                },
                "local_home": {
                    "purchase_year": 4,
                    "price_usd": 1200000,
                    "price_growth": [0.04, 0.05, 0.06, 0.06, 0.06, 0.06, 0.06],
                    "deposit_pct": 0.20,
                    "mortgage_rate": 0.065,
                    "mortgage_term_years": 30
                }
            }
        },
        "dubai": {
            "name": "Dubai, UAE",
            "currency": "USD",
            "exchange_rate": 1.26,
            "salary_progression": {
                1: 90000, 2: 100000, 3: 110000, 4: 120000, 5: 150000,
                6: 169000, 7: 183000, 8: 197000, 9: 213000, 10: 230000
            },
            "bonus_rate": 0.10,
            "rsu_rate": 0.10,
            "tax_system": "tax_free",
            "rent_monthly": 2000,
            "healthcare_monthly": 200,
            "retirement_contribution": 0.0,
            "general_expenses_monthly": 2000,
            "relocation_cost": 11800,
            "housing_options": {
                "uk_home": {
                    "purchase_year": 5,
                    "price_gbp": 600000,
                    "price_growth": [0.01, 0.04, 0.06, 0.06],
                    "deposit_pct": 0.20,
                    "mortgage_rate": 0.0525,
                    "mortgage_term_years": 25
                },
                "local_home": {
                    "purchase_year": 3,
                    "price_usd": 520000,
                    "price_growth": [0.02, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
                    "deposit_pct": 0.20,
                    "mortgage_rate": 0.045,
                    "mortgage_term_years": 25
                }
            }
        }
    },
    
    # Delayed Relocation Scenarios - Still used by test_all_scenarios.py
    "delayed_relocation": {
        "seattle_year4_uk_home": {
            "name": "Seattle (Move Year 4) - Buy UK Home",
            "uk_years": 3,
            "location": "seattle",
            "salary_multiplier": 1.1,
            "housing_strategy": "uk_home"
        },
        "seattle_year4_local_home": {
            "name": "Seattle (Move Year 4) - Buy Local Home",
            "uk_years": 3,
            "location": "seattle",
            "salary_multiplier": 1.1,
            "housing_strategy": "local_home"
        },
        "seattle_year5_uk_home": {
            "name": "Seattle (Move Year 5) - Buy UK Home",
            "uk_years": 4,
            "location": "seattle",
            "salary_multiplier": 1.2,
            "housing_strategy": "uk_home"
        },
        "seattle_year5_local_home": {
            "name": "Seattle (Move Year 5) - Buy Local Home",
            "uk_years": 4,
            "location": "seattle",
            "salary_multiplier": 1.2,
            "housing_strategy": "local_home"
        },
        "new_york_year4_uk_home": {
            "name": "New York (Move Year 4) - Buy UK Home",
            "uk_years": 3,
            "location": "new_york",
            "salary_multiplier": 1.1,
            "housing_strategy": "uk_home"
        },
        "new_york_year4_local_home": {
            "name": "New York (Move Year 4) - Buy Local Home",
            "uk_years": 3,
            "location": "new_york",
            "salary_multiplier": 1.1,
            "housing_strategy": "local_home"
        },
        "new_york_year5_uk_home": {
            "name": "New York (Move Year 5) - Buy UK Home",
            "uk_years": 4,
            "location": "new_york",
            "salary_multiplier": 1.2,
            "housing_strategy": "uk_home"
        },
        "new_york_year5_local_home": {
            "name": "New York (Move Year 5) - Buy Local Home",
            "uk_years": 4,
            "location": "new_york",
            "salary_multiplier": 1.2,
            "housing_strategy": "local_home"
        },
        "dubai_year4_uk_home": {
            "name": "Dubai (Move Year 4) - Buy UK Home",
            "uk_years": 3,
            "location": "dubai",
            "salary_multiplier": 1.1,
            "housing_strategy": "uk_home"
        },
        "dubai_year4_local_home": {
            "name": "Dubai (Move Year 4) - Buy Local Home",
            "uk_years": 3,
            "location": "dubai",
            "salary_multiplier": 1.1,
            "housing_strategy": "local_home"
        },
        "dubai_year5_uk_home": {
            "name": "Dubai (Move Year 5) - Buy UK Home",
            "uk_years": 4,
            "location": "dubai",
            "salary_multiplier": 1.2,
            "housing_strategy": "uk_home"
        },
        "dubai_year5_local_home": {
            "name": "Dubai (Move Year 5) - Buy Local Home",
            "uk_years": 4,
            "location": "dubai",
            "salary_multiplier": 1.2,
            "housing_strategy": "local_home"
        }
    }
} 