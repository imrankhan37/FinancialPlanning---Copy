"""
Financial Planning Configuration
Contains all configuration parameters for the financial planning scenarios.
"""

CONFIG = {
    # General Assumptions
    "start_year": 2025,
    "plan_duration_years": 10,
    "inflation_rate": 0.025,  # Will be adjusted per year
    "investment_return_rate": 0.065,  # Reduced from 7% to 6.5% for conservatism

    # User Profile
    "start_age": 24,

    # Liabilities
    "student_loan_debt": 57000,  # Undergraduate Plan 2 student loan
    "university_fee_payment": {  # Direct payments for current masters degree
        "year": 1,
        "amount": 16800,  # 3 payments of £5,600 each = £16,800 total
        "payment_schedule": [5600, 5600, 5600]  # 3 equal payments in Year 1
    },

    # Expenses (Year 1 baseline)
    "personal_expenses": {1: 6000, 2: 9000, "default": 12000},
    "parental_support": {
        "before_house": 12000,
        "after_house": 12000,
        "house_purchase_year": 5
    },
    "annual_travel": 3000,
    "personal_rent": {
        "start_year": 3,
        "amount": 25200
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
    
    # Major Goals
    "parental_home_purchase": {
        "target_year": 4, # Purchase takes place at the start of Year 5
        "price_grows": [0.01, 0.04, 0.06, 0.06], # Savills forecast for 2025-2028
        "base_price_2025": 600000,
        "deposit_pct": 0.20,
        "mortgage_rate": 0.0525,  # Updated from 4.5% to 5.25% based on market data
        "mortgage_term_years": 25
    },

    # Tax & NI (2025/26 England)
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

    # Student Loan (Plan 2)
    "student_loan_plan2": {
        "threshold": 28470,
        "repayment_rate": 0.09,
        "interest_rate_rpi": 0.043,
        "interest_rate_max_premium": 0.03,
        "interest_lower_income_threshold": 28470,
        "interest_upper_income_threshold": 51245
    },

    # Investment Allowances
    "isa_allowance": 20000,
    "lisa_allowance": 4000,
    "lisa_bonus_rate": 0.25,
    "sipp_allowance": 60000,
    
    # Inflation path (OBR-aligned)
    "inflation_path": {
        2025: 0.032,  # 3.2% for 2025
        2026: 0.022,  # 2.2% for 2026
        2027: 0.020,  # 2.0% thereafter
        "default": 0.020
    },
    
    # International Scenarios Configuration
    "international_scenarios": {
        "seattle": {
            "name": "Seattle, WA, USA",
            "currency": "USD",
            "exchange_rate": 1.26,  # GBP/USD (conservative)
            "salary_progression": {
                1: 100000,  # $180,000
                2: 110000,  # $200,000
                3: 120000,  # $220,000
                4: 150000,  # $240,000
                5: 180000,  # $260,000
                6: 200000,  # $280,000
                7: 200000,  # $300,000
                8: 220000,  # $320,000
                9: 220000,  # $340,000
                10: 240000   # $360,000
            },
            "bonus_rate": 0.1,
            "rsu_rate": 0.25,  # 25% of salary as RSUs
            "tax_system": "us_federal_state",  # Federal + WA State tax
            "rent_monthly": 2200,  # $2,200/month for 1-bedroom apartment
            "healthcare_monthly": 500,  # $500/month
            "retirement_contribution": 0.06,  # 6% for 401k match
            "general_expenses_monthly": 2000,  # $2,000/month
            "relocation_cost": 11300,  # £11,300
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
                    "price_usd": 750000,  # $750k Seattle home
                    "price_growth": [0.03, 0.04, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
                    "deposit_pct": 0.25,
                    "mortgage_rate": 0.065,  # Higher US rates
                    "mortgage_term_years": 30
                }
            }
        },
        "new_york": {
            "name": "New York, NY, USA",
            "currency": "USD",
            "exchange_rate": 1.26,
            "salary_progression": {
                1: 100000,  # $200,000
                2: 120000,  # $220,000
                3: 130000,  # $240,000
                4: 150000,  # $260,000
                5: 180000,  # $280,000
                6: 200000,  # $300,000
                7: 200000,  # $320,000
                8: 200000,  # $340,000
                9: 230000,  # $360,000
                10: 250000   # $380,000
            },
            "bonus_rate": 0.15,
            "rsu_rate": 0.25,
            "tax_system": "us_federal_state_city",  # Federal + NY State + NYC
            "rent_monthly": 4000,  # $4,000/month for 1-bedroom apartment
            "healthcare_monthly": 500,
            "retirement_contribution": 0.06,
            "general_expenses_monthly": 2500,  # $2,500/month
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
                    "price_usd": 1200000,  # $1.2M NYC home
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
                1: 90000,  # $115,000 (reduced from $150k)
                2: 100000,  # $124,000
                3: 110000,  # $134,000
                4: 120000,  # $145,000
                5: 150000,  # $157,000
                6: 169000,  # $169,000
                7: 183000,  # $183,000
                8: 197000,  # $197,000
                9: 213000,  # $213,000
                10: 230000   # $230,000
            },
            "bonus_rate": 0.10,
            "rsu_rate": 0.10,  # Lower RSU component in Middle East
            "tax_system": "tax_free",
            "rent_monthly": 2000,  # $2,000/month for 1-bedroom apartment
            "healthcare_monthly": 200,  # $125/month (much cheaper)
            "retirement_contribution": 0.0,  # No 401k equivalent
            "general_expenses_monthly": 2000,  # $1,500/month
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
                    "price_usd": 520000,  # $400k Dubai home
                    "price_growth": [0.02, 0.03, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04],
                    "deposit_pct": 0.20,
                    "mortgage_rate": 0.045,  # Lower rates in UAE
                    "mortgage_term_years": 25
                }
            }
        }
    },
    
    # Delayed Relocation Scenarios
    "delayed_relocation": {
        "seattle_year4_uk_home": {
            "name": "Seattle (Move Year 4) - Buy UK Home",
            "uk_years": 3,
            "location": "seattle",
            "salary_multiplier": 1.1,  # Slight premium for experience
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
            "salary_multiplier": 1.2,  # Higher premium for more experience
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