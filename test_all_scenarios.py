"""
Comprehensive Test Script for All Scenarios
Tests all scenarios from config.py to ensure unified models work correctly.
"""

import sys
import traceback
from financial_planner_pydantic import (
    run_unified_scenario,
    run_unified_international_scenario,
    run_unified_delayed_relocation_scenario
)
from config import CONFIG

def test_uk_scenarios():
    """Test UK scenarios A and B."""
    print("\n🔍 Testing UK Scenarios...")
    
    try:
        # Test UK Scenario A
        scenario_a = run_unified_scenario('A', CONFIG)
        print(f"✅ UK Scenario A: £{scenario_a.get_final_net_worth_gbp():,.0f}")
        print(f"   - Data points: {len(scenario_a.data_points)}")
        print(f"   - Average savings: £{scenario_a.get_average_annual_savings_gbp():,.0f}")
        print(f"   - Total tax burden: £{scenario_a.get_total_tax_burden_gbp():,.0f}")
        
        # Test UK Scenario B
        scenario_b = run_unified_scenario('B', CONFIG)
        print(f"✅ UK Scenario B: £{scenario_b.get_final_net_worth_gbp():,.0f}")
        print(f"   - Data points: {len(scenario_b.data_points)}")
        print(f"   - Average savings: £{scenario_b.get_average_annual_savings_gbp():,.0f}")
        print(f"   - Total tax burden: £{scenario_b.get_total_tax_burden_gbp():,.0f}")
        
        return True
        
    except Exception as e:
        print(f"❌ UK Scenarios failed: {str(e)}")
        traceback.print_exc()
        return False

def test_international_scenarios():
    """Test international scenarios."""
    print("\n🔍 Testing International Scenarios...")
    
    locations = ['seattle', 'new_york', 'dubai']
    housing_strategies = ['uk_home', 'local_home']
    
    success_count = 0
    total_count = 0
    
    for location in locations:
        for housing_strategy in housing_strategies:
            total_count += 1
            try:
                scenario = run_unified_international_scenario(location, CONFIG, housing_strategy)
                print(f"✅ {location.title()} {housing_strategy}: £{scenario.get_final_net_worth_gbp():,.0f}")
                print(f"   - Data points: {len(scenario.data_points)}")
                print(f"   - Average savings: £{scenario.get_average_annual_savings_gbp():,.0f}")
                success_count += 1
                
            except Exception as e:
                print(f"❌ {location.title()} {housing_strategy} failed: {str(e)}")
                traceback.print_exc()
    
    print(f"\n📊 International Scenarios: {success_count}/{total_count} successful")
    return success_count == total_count

def test_delayed_relocation_scenarios():
    """Test delayed relocation scenarios."""
    print("\n🔍 Testing Delayed Relocation Scenarios...")
    
    # Get all delayed relocation scenarios from config
    delayed_scenarios = list(CONFIG["delayed_relocation"].keys())
    
    success_count = 0
    total_count = len(delayed_scenarios)
    
    for scenario_name in delayed_scenarios:
        try:
            scenario = run_unified_delayed_relocation_scenario(scenario_name, CONFIG)
            print(f"✅ {scenario_name}: £{scenario.get_final_net_worth_gbp():,.0f}")
            print(f"   - Data points: {len(scenario.data_points)}")
            print(f"   - Average savings: £{scenario.get_average_annual_savings_gbp():,.0f}")
            print(f"   - Growth rate: {scenario.get_net_worth_growth_rate():.1f}%")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {scenario_name} failed: {str(e)}")
            traceback.print_exc()
    
    print(f"\n📊 Delayed Relocation Scenarios: {success_count}/{total_count} successful")
    return success_count == total_count

def test_unified_models():
    """Test unified model functionality."""
    print("\n🔍 Testing Unified Model Functionality...")
    
    try:
        # Test UK scenario to check unified model structure
        scenario = run_unified_scenario('A', CONFIG)
        
        # Check data point structure
        if scenario.data_points:
            data_point = scenario.data_points[0]
            print(f"✅ Unified data point structure:")
            print(f"   - Year: {data_point.year}")
            print(f"   - Age: {data_point.age}")
            print(f"   - Phase: {data_point.phase.value}")
            print(f"   - Jurisdiction: {data_point.jurisdiction.value}")
            print(f"   - Currency: {data_point.currency.value}")
            print(f"   - Income breakdown: £{data_point.income.total_gbp:,.0f}")
            print(f"   - Expense breakdown: £{data_point.expenses.total_gbp:,.0f}")
            print(f"   - Tax breakdown: £{data_point.tax.total_gbp:,.0f}")
            print(f"   - Investment breakdown: £{data_point.investments.total_gbp:,.0f}")
            print(f"   - Net worth breakdown: £{data_point.net_worth.total_gbp:,.0f}")
        
        # Check scenario metadata
        print(f"✅ Scenario metadata:")
        print(f"   - Name: {scenario.name}")
        print(f"   - Description: {scenario.description}")
        print(f"   - Phase: {scenario.phase.value}")
        print(f"   - Metadata jurisdiction: {scenario.metadata.jurisdiction.value}")
        print(f"   - Metadata tax system: {scenario.metadata.tax_system}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified model test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_performance():
    """Test performance of scenario generation."""
    print("\n🔍 Testing Performance...")
    
    import time
    
    try:
        # Test UK scenario generation time
        start_time = time.time()
        scenario = run_unified_scenario('A', CONFIG)
        uk_time = time.time() - start_time
        print(f"✅ UK scenario generation: {uk_time:.3f} seconds")
        
        # Test international scenario generation time
        start_time = time.time()
        scenario = run_unified_international_scenario('seattle', CONFIG)
        int_time = time.time() - start_time
        print(f"✅ International scenario generation: {int_time:.3f} seconds")
        
        # Test delayed relocation scenario generation time
        start_time = time.time()
        scenario = run_unified_delayed_relocation_scenario('seattle_year4_uk_home', CONFIG)
        delayed_time = time.time() - start_time
        print(f"✅ Delayed relocation scenario generation: {delayed_time:.3f} seconds")
        
        total_time = uk_time + int_time + delayed_time
        print(f"✅ Total test time: {total_time:.3f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive Scenario Testing...")
    print("=" * 60)
    
    test_results = []
    
    # Test UK scenarios
    test_results.append(("UK Scenarios", test_uk_scenarios()))
    
    # Test international scenarios
    test_results.append(("International Scenarios", test_international_scenarios()))
    
    # Test delayed relocation scenarios
    test_results.append(("Delayed Relocation Scenarios", test_delayed_relocation_scenarios()))
    
    # Test unified model functionality
    test_results.append(("Unified Model Functionality", test_unified_models()))
    
    # Test performance
    test_results.append(("Performance", test_performance()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Unified models are working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 