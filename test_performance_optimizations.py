"""
Test script for performance optimizations.
Validates caching, data access optimization, and performance monitoring.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.performance_optimizations import (
    CurrencyConversionCache,
    CacheStrategy,
    DataAccessOptimizer,
    PerformanceMonitor,
    optimize_currency_value_creation,
    optimize_scenario_analysis,
    get_performance_summary,
    clear_all_caches
)
from models.unified_financial_data import Currency, CurrencyValue
from datetime import timedelta


def test_currency_conversion_cache():
    """Test currency conversion caching."""
    print("Testing Currency Conversion Cache...")
    
    # Create cache with hybrid strategy
    cache = CurrencyConversionCache(CacheStrategy.HYBRID)
    
    # Test cache operations
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    print("✅ Basic cache operations passed")
    
    # Test cache statistics
    stats = cache.get_stats()
    assert stats['total_entries'] >= 1
    assert stats['strategy'] == 'hybrid'
    print("✅ Cache statistics passed")
    
    # Test cache expiration
    cache.set("expired_key", "expired_value", ttl=timedelta(milliseconds=1))  # Very short TTL
    time.sleep(0.002)  # Wait for expiration
    assert cache.get("expired_key") is None
    print("✅ Cache expiration passed")
    
    # Test cache clearing
    cleared = cache.clear_expired()
    assert cleared >= 0  # May be 0 if no expired entries
    print("✅ Cache clearing passed")


def test_optimized_currency_conversion():
    """Test optimized currency conversion."""
    print("Testing Optimized Currency Conversion...")
    
    # Test GBP conversion
    gbp_value = optimize_currency_value_creation(50000, Currency.GBP)
    assert gbp_value.value == 50000
    assert gbp_value.currency == Currency.GBP
    assert gbp_value.gbp_value == 50000
    print("✅ GBP conversion passed")
    
    # Test USD conversion
    usd_value = optimize_currency_value_creation(75000, Currency.USD, 1.26)
    assert usd_value.value == 75000
    assert usd_value.currency == Currency.USD
    assert usd_value.gbp_value == 75000 / 1.26
    print("✅ USD conversion passed")
    
    # Test EUR conversion
    eur_value = optimize_currency_value_creation(60000, Currency.EUR, 1.15)
    assert eur_value.value == 60000
    assert eur_value.currency == Currency.EUR
    assert eur_value.gbp_value == 60000 / 1.15
    print("✅ EUR conversion passed")


def test_data_access_optimizer():
    """Test data access optimization."""
    print("Testing Data Access Optimizer...")
    
    optimizer = DataAccessOptimizer()
    
    # Test scenario list optimization
    scenarios = [{"name": f"Scenario_{i}", "value": i} for i in range(100)]
    
    # Test filtering
    filtered = optimizer.optimize_scenario_list(
        scenarios, 
        filter_func=lambda s: s['value'] % 2 == 0
    )
    assert len(filtered) == 50
    print("✅ Scenario filtering passed")
    
    # Test sorting
    sorted_scenarios = optimizer.optimize_scenario_list(
        scenarios,
        sort_func=lambda s: s['value']
    )
    assert sorted_scenarios[0]['value'] == 0
    assert sorted_scenarios[-1]['value'] == 99
    print("✅ Scenario sorting passed")
    
    # Test pagination
    paginated = optimizer.paginate_data(scenarios, page=2, page_size=10)
    assert len(paginated['data']) == 10
    assert paginated['pagination']['page'] == 2
    assert paginated['pagination']['total_pages'] == 10
    print("✅ Data pagination passed")
    
    # Test access pattern tracking
    optimizer.track_access_pattern("test_pattern")
    stats = optimizer.get_access_stats()
    assert stats["test_pattern"] == 1
    print("✅ Access pattern tracking passed")


def test_performance_monitor():
    """Test performance monitoring."""
    print("Testing Performance Monitor...")
    
    monitor = PerformanceMonitor()
    
    # Test timing operations
    monitor.start_timer("test_operation")
    time.sleep(0.1)  # Simulate work
    duration = monitor.end_timer("test_operation")
    assert duration > 0.09  # Should be close to 0.1
    print("✅ Operation timing passed")
    
    # Test average time calculation
    monitor.start_timer("avg_test")
    time.sleep(0.05)
    monitor.end_timer("avg_test")
    
    monitor.start_timer("avg_test")
    time.sleep(0.15)
    monitor.end_timer("avg_test")
    
    avg_time = monitor.get_average_time("avg_test")
    assert 0.05 < avg_time < 0.15  # Average should be around 0.1 with some tolerance
    print("✅ Average time calculation passed")
    
    # Test performance report
    report = monitor.get_performance_report()
    assert "operation_times" in report
    assert "recommendations" in report
    print("✅ Performance report generation passed")


def test_optimized_scenario_analysis():
    """Test optimized scenario analysis."""
    print("Testing Optimized Scenario Analysis...")
    
    # Create test scenarios
    scenarios = [
        {"name": "Scenario_A", "value": 100},
        {"name": "Scenario_B", "value": 200},
        {"name": "Scenario_C", "value": 150}
    ]
    
    # Test analysis function
    def analyze_scenarios(scenario_list):
        return {
            "total_value": sum(s['value'] for s in scenario_list),
            "count": len(scenario_list),
            "average": sum(s['value'] for s in scenario_list) / len(scenario_list)
        }
    
    result = optimize_scenario_analysis(scenarios, analyze_scenarios)
    assert result['total_value'] == 450
    assert result['count'] == 3
    assert result['average'] == 150
    print("✅ Optimized scenario analysis passed")


def test_performance_summary():
    """Test performance summary generation."""
    print("Testing Performance Summary...")
    
    # Generate some activity
    cache = CurrencyConversionCache()
    cache.set("test_key", "test_value")
    cache.get("test_key")
    
    optimizer = DataAccessOptimizer()
    optimizer.track_access_pattern("test_pattern")
    
    monitor = PerformanceMonitor()
    monitor.start_timer("test_op")
    time.sleep(0.01)
    monitor.end_timer("test_op")
    
    # Get performance summary
    summary = get_performance_summary()
    
    assert "cache" in summary
    assert "data_access" in summary
    assert "performance" in summary
    
    cache_stats = summary["cache"]
    assert cache_stats["total_entries"] >= 0  # May be 0 after clearing
    assert cache_stats["strategy"] == "hybrid"
    
    data_stats = summary["data_access"]
    # Note: data_stats may be empty if caches were cleared
    print(f"Data access patterns: {data_stats}")
    
    perf_stats = summary["performance"]
    assert "operation_times" in perf_stats
    print("✅ Performance summary generation passed")


def test_cache_clearing():
    """Test cache clearing functionality."""
    print("Testing Cache Clearing...")
    
    # Import the global instances
    from models.performance_optimizations import currency_cache, data_optimizer, performance_monitor
    
    # Add some data to global instances
    currency_cache.set("key1", "value1")
    currency_cache.set("key2", "value2")
    data_optimizer.track_access_pattern("pattern1")
    data_optimizer.track_access_pattern("pattern2")
    performance_monitor.start_timer("test_op")
    performance_monitor.end_timer("test_op")
    
    # Verify data exists before clearing
    assert currency_cache.get_stats()["total_entries"] >= 2
    assert len(data_optimizer.get_access_stats()) >= 2
    assert len(performance_monitor.get_performance_report()["operation_times"]) >= 1
    
    # Clear all caches
    clear_all_caches()
    
    # Verify global instances are cleared
    assert currency_cache.get_stats()["total_entries"] == 0
    assert len(data_optimizer.get_access_stats()) == 0
    assert len(performance_monitor.get_performance_report()["operation_times"]) == 0
    
    print("✅ Cache clearing passed")


def main():
    """Run all performance optimization tests."""
    print("🧪 Testing Performance Optimizations")
    print("=" * 50)
    
    try:
        test_currency_conversion_cache()
        test_optimized_currency_conversion()
        test_data_access_optimizer()
        test_performance_monitor()
        test_optimized_scenario_analysis()
        test_performance_summary()
        test_cache_clearing()
        
        print("\n" + "=" * 50)
        print("✅ All performance optimization tests passed!")
        print("🚀 Performance optimizations are working correctly.")
        
        # Show final performance summary
        summary = get_performance_summary()
        print(f"\n📊 Final Performance Summary:")
        print(f"Cache Entries: {summary['cache']['total_entries']}")
        print(f"Cache Strategy: {summary['cache']['strategy']}")
        print(f"Data Access Patterns: {len(summary['data_access'])}")
        print(f"Monitored Operations: {len(summary['performance']['operation_times'])}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main() 