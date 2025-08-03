"""
Performance Optimizations for Unified Financial Data Model
Implements caching, memoization, and data access optimizations.
"""

import functools
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
import json
import os

from .unified_financial_data import CurrencyValue, Currency


class CacheStrategy(str, Enum):
    """Cache strategy types."""
    MEMORY = "memory"
    PERSISTENT = "persistent"
    HYBRID = "hybrid"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    value: Any
    timestamp: datetime
    ttl: timedelta
    access_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > self.timestamp + self.ttl
    
    def access(self) -> None:
        """Record cache access."""
        self.access_count += 1


class CurrencyConversionCache:
    """Caching system for currency conversions."""
    
    def __init__(self, strategy: CacheStrategy = CacheStrategy.HYBRID):
        self.strategy = strategy
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.persistent_file = "currency_cache.json"
        self.lock = threading.Lock()
        self.default_ttl = timedelta(hours=24)  # 24 hours for exchange rates
        
        # Load persistent cache if exists
        if strategy in [CacheStrategy.PERSISTENT, CacheStrategy.HYBRID]:
            self._load_persistent_cache()
    
    def _get_cache_key(self, from_currency: Currency, to_currency: Currency, 
                       value: float, exchange_rate: float) -> str:
        """Generate cache key for currency conversion."""
        return f"{from_currency.value}_{to_currency.value}_{value}_{exchange_rate}"
    
    def _load_persistent_cache(self) -> None:
        """Load cache from persistent storage."""
        try:
            if os.path.exists(self.persistent_file):
                with open(self.persistent_file, 'r') as f:
                    data = json.load(f)
                    for key, entry_data in data.items():
                        if not self._is_expired_entry(entry_data):
                            self.memory_cache[key] = CacheEntry(
                                value=entry_data['value'],
                                timestamp=datetime.fromisoformat(entry_data['timestamp']),
                                ttl=timedelta(seconds=entry_data['ttl_seconds']),
                                access_count=entry_data['access_count']
                            )
        except Exception as e:
            print(f"Warning: Could not load persistent cache: {e}")
    
    def _save_persistent_cache(self) -> None:
        """Save cache to persistent storage."""
        try:
            data = {}
            for key, entry in self.memory_cache.items():
                # Skip non-serializable objects
                try:
                    # Test if the value is JSON serializable
                    json.dumps(entry.value)
                    data[key] = {
                        'value': entry.value,
                        'timestamp': entry.timestamp.isoformat(),
                        'ttl_seconds': entry.ttl.total_seconds(),
                        'access_count': entry.access_count
                    }
                except (TypeError, ValueError):
                    # Skip non-serializable entries
                    continue
            
            with open(self.persistent_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save persistent cache: {e}")
    
    def _is_expired_entry(self, entry_data: Dict[str, Any]) -> bool:
        """Check if persistent cache entry is expired."""
        try:
            timestamp = datetime.fromisoformat(entry_data['timestamp'])
            ttl = timedelta(seconds=entry_data['ttl_seconds'])
            return datetime.now() > timestamp + ttl
        except (KeyError, ValueError):
            return True  # Consider malformed entries as expired
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            entry = self.memory_cache.get(key)
            if entry and not entry.is_expired():
                entry.access()
                return entry.value
            elif entry and entry.is_expired():
                # Remove expired entry
                del self.memory_cache[key]
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Set value in cache."""
        with self.lock:
            self.memory_cache[key] = CacheEntry(
                value=value,
                timestamp=datetime.now(),
                ttl=ttl or self.default_ttl
            )
            
            # Save to persistent storage if needed
            if self.strategy in [CacheStrategy.PERSISTENT, CacheStrategy.HYBRID]:
                self._save_persistent_cache()
    
    def clear_expired(self) -> int:
        """Clear expired entries and return count of cleared entries."""
        with self.lock:
            expired_keys = [
                key for key, entry in self.memory_cache.items() 
                if entry.is_expired()
            ]
            for key in expired_keys:
                del self.memory_cache[key]
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_entries = len(self.memory_cache)
            expired_entries = sum(1 for entry in self.memory_cache.values() if entry.is_expired())
            total_accesses = sum(entry.access_count for entry in self.memory_cache.values())
            
            return {
                'total_entries': total_entries,
                'expired_entries': expired_entries,
                'active_entries': total_entries - expired_entries,
                'total_accesses': total_accesses,
                'strategy': self.strategy.value
            }


# Global cache instance
currency_cache = CurrencyConversionCache()


def cached_currency_conversion(func: Callable) -> Callable:
    """Decorator for caching currency conversions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key from function arguments
        cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
        
        # Try to get from cache
        cached_result = currency_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Calculate result
        result = func(*args, **kwargs)
        
        # Cache the result
        currency_cache.set(cache_key, result)
        
        return result
    return wrapper


@cached_currency_conversion
def optimized_currency_conversion(value: float, from_currency: Currency, 
                                to_currency: Currency, exchange_rate: float) -> CurrencyValue:
    """Optimized currency conversion with caching."""
    if from_currency == to_currency:
        return CurrencyValue.from_gbp(value)
    
    # Convert to GBP first (our base currency)
    if from_currency == Currency.GBP:
        gbp_value = value
    else:
        gbp_value = value / exchange_rate
    
    # Create CurrencyValue with caching
    return CurrencyValue(
        value=value,
        currency=from_currency,
        gbp_value=gbp_value,
        exchange_rate=exchange_rate,
        conversion_date=datetime.now()
    )


class DataAccessOptimizer:
    """Optimizes data access patterns for large datasets."""
    
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size
        self.access_patterns: Dict[str, int] = {}
    
    def optimize_scenario_list(self, scenarios: List[Any], 
                             filter_func: Optional[Callable] = None,
                             sort_func: Optional[Callable] = None) -> List[Any]:
        """Optimize scenario list access with filtering and sorting."""
        # Apply filtering if provided
        if filter_func:
            scenarios = [s for s in scenarios if filter_func(s)]
        
        # Apply sorting if provided
        if sort_func:
            scenarios = sorted(scenarios, key=sort_func)
        
        return scenarios
    
    def paginate_data(self, data: List[Any], page: int = 1, 
                     page_size: int = 50) -> Dict[str, Any]:
        """Paginate data for efficient UI rendering."""
        total_items = len(data)
        total_pages = (total_items + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            'data': data[start_idx:end_idx],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_items': total_items,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }
    
    def lazy_load_scenarios(self, scenario_names: List[str], 
                          load_func: Callable) -> Dict[str, Any]:
        """Lazy load scenarios on demand."""
        loaded_scenarios = {}
        
        for name in scenario_names:
            if name not in loaded_scenarios:
                loaded_scenarios[name] = load_func(name)
        
        return loaded_scenarios
    
    def track_access_pattern(self, pattern: str) -> None:
        """Track data access patterns for optimization."""
        self.access_patterns[pattern] = self.access_patterns.get(pattern, 0) + 1
    
    def get_access_stats(self) -> Dict[str, int]:
        """Get access pattern statistics."""
        return self.access_patterns.copy()


class PerformanceMonitor:
    """Monitor performance metrics for optimization."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = time.time()
    
    def end_timer(self, operation: str) -> float:
        """End timing an operation and return duration."""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration)
            del self.start_times[operation]
            return duration
        return 0.0
    
    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation."""
        if operation in self.metrics and self.metrics[operation]:
            return sum(self.metrics[operation]) / len(self.metrics[operation])
        return 0.0
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        report = {
            'cache_stats': currency_cache.get_stats(),
            'operation_times': {},
            'recommendations': []
        }
        
        for operation, times in self.metrics.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
                
                report['operation_times'][operation] = {
                    'average_ms': avg_time * 1000,
                    'max_ms': max_time * 1000,
                    'min_ms': min_time * 1000,
                    'count': len(times)
                }
                
                # Generate recommendations
                if avg_time > 1.0:  # More than 1 second
                    report['recommendations'].append(
                        f"Optimize {operation}: {avg_time:.2f}s average"
                    )
        
        return report


# Global instances
data_optimizer = DataAccessOptimizer()
performance_monitor = PerformanceMonitor()


def optimize_currency_value_creation(value: float, currency: Currency, 
                                   exchange_rate: float = 1.0) -> CurrencyValue:
    """Optimized currency value creation with caching."""
    performance_monitor.start_timer('currency_conversion')
    
    try:
        result = optimized_currency_conversion(value, currency, Currency.GBP, exchange_rate)
        return result
    finally:
        performance_monitor.end_timer('currency_conversion')


# REMOVED: optimize_scenario_analysis - was never used in the codebase


def get_performance_summary() -> Dict[str, Any]:
    """Get comprehensive performance summary."""
    return {
        'cache': currency_cache.get_stats(),
        'data_access': data_optimizer.get_access_stats(),
        'performance': performance_monitor.get_performance_report()
    }


def clear_all_caches() -> None:
    """Clear all caches and reset performance monitors."""
    # Clear global cache
    currency_cache.clear_expired()
    currency_cache.memory_cache.clear()
    
    # Clear global data optimizer
    data_optimizer.access_patterns.clear()
    
    # Clear global performance monitor
    performance_monitor.metrics.clear()
    performance_monitor.start_times.clear() 