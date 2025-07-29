"""
Performance monitoring utilities for the financial planning dashboard.
Provides tools for tracking and optimizing application performance.
"""

import streamlit as st
import time
import psutil
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import pandas as pd
import plotly.graph_objects as go


class PerformanceMonitor:
    """Monitor and track application performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'load_times': [],
            'chart_creation_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        self.start_time = time.time()
    
    def track_load_time(self, operation: str, duration: float) -> None:
        """Track data loading times."""
        self.metrics['load_times'].append({
            'operation': operation,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 load times
        if len(self.metrics['load_times']) > 50:
            self.metrics['load_times'] = self.metrics['load_times'][-50:]
    
    def track_chart_creation(self, chart_type: str, duration: float) -> None:
        """Track chart creation times."""
        self.metrics['chart_creation_times'].append({
            'chart_type': chart_type,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 100 chart creation times
        if len(self.metrics['chart_creation_times']) > 100:
            self.metrics['chart_creation_times'] = self.metrics['chart_creation_times'][-100:]
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system performance metrics."""
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            
            return {
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'cpu_percent': cpu
            }
        except Exception:
            return {
                'memory_percent': 0,
                'memory_available_gb': 0,
                'cpu_percent': 0
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        if not self.metrics['load_times']:
            return {
                'avg_load_time': 0,
                'avg_chart_time': 0,
                'total_operations': 0,
                'uptime': time.time() - self.start_time
            }
        
        # Calculate average load times by operation
        load_times_by_operation = {}
        for load_time in self.metrics['load_times']:
            op = load_time['operation']
            if op not in load_times_by_operation:
                load_times_by_operation[op] = []
            load_times_by_operation[op].append(load_time['duration'])
        
        avg_load_times = {
            op: sum(times) / len(times) 
            for op, times in load_times_by_operation.items()
        }
        
        # Calculate average chart creation time
        chart_times = [ct['duration'] for ct in self.metrics['chart_creation_times']]
        avg_chart_time = sum(chart_times) / len(chart_times) if chart_times else 0
        
        return {
            'avg_load_times': avg_load_times,
            'avg_chart_time': avg_chart_time,
            'total_operations': len(self.metrics['load_times']) + len(self.metrics['chart_creation_times']),
            'uptime': time.time() - self.start_time
        }
    
    def get_performance_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        summary = self.get_performance_summary()
        
        # Check load times
        if summary.get('avg_load_times'):
            for operation, avg_time in summary['avg_load_times'].items():
                if avg_time > 5.0:
                    recommendations.append(f"⚠️ {operation} is slow ({avg_time:.2f}s). Consider caching.")
                elif avg_time > 2.0:
                    recommendations.append(f"⚡ {operation} could be optimized ({avg_time:.2f}s).")
        
        # Check chart creation times
        if summary['avg_chart_time'] > 1.0:
            recommendations.append(f"📊 Chart creation is slow ({summary['avg_chart_time']:.2f}s). Consider reducing data points.")
        
        # Check system resources
        system_metrics = self.get_system_metrics()
        if system_metrics['memory_percent'] > 80:
            recommendations.append("💾 High memory usage detected. Consider clearing cache.")
        
        if system_metrics['cpu_percent'] > 70:
            recommendations.append("🔥 High CPU usage detected. Consider reducing concurrent operations.")
        
        if not recommendations:
            recommendations.append("✅ Performance is optimal!")
        
        return recommendations


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def track_operation(operation_type: str, operation_name: str):
    """Decorator to track operation performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                if operation_type == 'load':
                    performance_monitor.track_load_time(operation_name, duration)
                elif operation_type == 'chart':
                    performance_monitor.track_chart_creation(operation_name, duration)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                st.error(f"Operation {operation_name} failed after {duration:.2f}s: {str(e)}")
                raise
        return wrapper
    return decorator


def render_performance_dashboard() -> None:
    """Render a performance monitoring dashboard."""
    st.markdown("### 📊 Performance Dashboard")
    
    # Get performance summary
    summary = performance_monitor.get_performance_summary()
    system_metrics = performance_monitor.get_system_metrics()
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Uptime",
            f"{summary['uptime']/3600:.1f}h",
            help="Application uptime"
        )
    
    with col2:
        st.metric(
            "Total Operations",
            summary['total_operations'],
            help="Total tracked operations"
        )
    
    with col3:
        st.metric(
            "Memory Usage",
            f"{system_metrics['memory_percent']:.1f}%",
            help="Current memory usage"
        )
    
    with col4:
        st.metric(
            "CPU Usage",
            f"{system_metrics['cpu_percent']:.1f}%",
            help="Current CPU usage"
        )
    
    # Display average load times
    st.markdown("### Average Load Times")
    if summary.get('avg_load_times'):
        load_times_df = pd.DataFrame([
            {'Operation': op, 'Avg Time (s)': time}
            for op, time in summary['avg_load_times'].items()
        ])
        st.dataframe(load_times_df, use_container_width=True)
    else:
        st.info("No load time data available yet.")
    
    # Display performance recommendations
    st.markdown("### Performance Recommendations")
    recommendations = performance_monitor.get_performance_recommendations()
    
    for rec in recommendations:
        if rec.startswith("✅"):
            st.success(rec)
        elif rec.startswith("⚠️"):
            st.warning(rec)
        elif rec.startswith("🔥") or rec.startswith("💾"):
            st.error(rec)
        else:
            st.info(rec)
    
    # Performance optimization buttons
    st.markdown("### Performance Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Clear Cache", help="Clear all cached data", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with col2:
        if st.button("📊 Reset Metrics", help="Reset performance tracking", use_container_width=True):
            performance_monitor.metrics = {
                'load_times': [],
                'chart_creation_times': [],
                'memory_usage': [],
                'cpu_usage': []
            }
            st.success("Metrics reset!")
    
    with col3:
        if st.button("📈 Export Metrics", help="Export performance data", use_container_width=True):
            metrics_json = json.dumps(performance_monitor.metrics, indent=2)
            st.download_button(
                label="Download Metrics",
                data=metrics_json,
                file_name=f"performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


def optimize_chart_rendering(fig, max_points: int = 1000) -> go.Figure:
    """Optimize chart rendering by reducing data points if necessary."""
    if hasattr(fig, 'data') and fig.data:
        for trace in fig.data:
            if hasattr(trace, 'x') and len(trace.x) > max_points:
                # Sample data points to improve performance
                step = len(trace.x) // max_points
                trace.x = trace.x[::step]
                trace.y = trace.y[::step]
                if hasattr(trace, 'text'):
                    trace.text = trace.text[::step] if trace.text else None
    
    return fig


def get_optimal_cache_ttl(operation_type: str) -> int:
    """Get optimal cache TTL based on operation type."""
    ttl_map = {
        'scenario_data': 300,  # 5 minutes for scenario data
        'chart_data': 60,      # 1 minute for chart data
        'metrics': 30,         # 30 seconds for metrics
        'filtered_data': 120   # 2 minutes for filtered data
    }
    return ttl_map.get(operation_type, 60)


def monitor_memory_usage() -> None:
    """Monitor memory usage and provide warnings if needed."""
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            st.warning(f"⚠️ High memory usage detected: {memory.percent:.1f}%. Consider clearing cache.")
        elif memory.percent > 70:
            st.info(f"ℹ️ Memory usage: {memory.percent:.1f}%")
    except Exception:
        pass  # Skip if psutil is not available 