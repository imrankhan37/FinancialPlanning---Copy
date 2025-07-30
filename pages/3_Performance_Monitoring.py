"""
Performance Monitoring Page
Track and optimize dashboard performance with real-time metrics using unified models.
"""

import streamlit as st
import time
import pandas as pd
from typing import Dict, Any

# Import custom modules
from utils.performance import render_performance_dashboard, performance_monitor, monitor_memory_usage
from utils.data import load_all_scenarios, clear_cache

# Import unified helpers for performance monitoring
from models.unified_helpers import get_performance_metrics as get_unified_performance_metrics


def render_performance_page(scenarios_to_analyze=None) -> None:
    """Render the performance monitoring page using unified models."""
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 15px; margin-bottom: 2rem; color: white; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">⚡ System Performance Monitor</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">Monitor dashboard performance, optimize data loading, and track system resources in real-time with unified models.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main performance dashboard
    render_performance_dashboard()
    
    # Unified model performance metrics
    st.markdown("---")
    st.subheader("🔄 Unified Model Performance")
    
    try:
        # Get unified performance metrics
        unified_metrics = get_unified_performance_metrics()
        
        if unified_metrics:
            st.markdown("#### 📊 Unified Model Metrics")
            
            # Display metrics in a clean format
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'conversion_time' in unified_metrics:
                    st.metric(
                        label="Data Conversion Time",
                        value=f"{unified_metrics['conversion_time']:.3f}s",
                        delta=None
                    )
            
            with col2:
                if 'cache_hits' in unified_metrics:
                    st.metric(
                        label="Cache Hit Rate",
                        value=f"{unified_metrics['cache_hits']:.1f}%",
                        delta=None
                    )
            
            with col3:
                if 'memory_usage' in unified_metrics:
                    st.metric(
                        label="Memory Usage",
                        value=f"{unified_metrics['memory_usage']:.1f}MB",
                        delta=None
                    )
            
            # Detailed metrics table
            if len(unified_metrics) > 3:
                st.markdown("#### 📋 Detailed Performance Metrics")
                metrics_df = pd.DataFrame([unified_metrics]).T
                metrics_df.columns = ['Value']
                st.dataframe(metrics_df, use_container_width=True)
        else:
            st.info("No unified performance metrics available.")
    
    except Exception as e:
        st.warning(f"Could not load unified performance metrics: {str(e)}")
    
    # Performance testing section
    st.markdown("---")
    st.subheader("🧪 Performance Testing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Test Data Loading", help="Test scenario data loading performance with unified models", use_container_width=True):
            with st.spinner("Testing data loading..."):
                start_time = time.time()
                try:
                    scenarios = load_all_scenarios()
                    load_time = time.time() - start_time
                    st.success(f"✅ Data loaded successfully in {load_time:.2f}s")
                    
                    # Track the operation
                    performance_monitor.track_load_time("test_data_loading", load_time)
                    
                    # Show scenario count
                    if scenarios:
                        st.info(f"📊 Loaded {len(scenarios)} scenarios with unified models")
                    
                except Exception as e:
                    st.error(f"❌ Data loading failed: {str(e)}")
    
    with col2:
        if st.button("🧹 Clear All Cache", help="Clear all cached data including unified model caches", use_container_width=True):
            clear_cache()
            st.success("✅ Cache cleared successfully!")
    
    # Memory monitoring
    st.markdown("---")
    st.subheader("💾 Memory Monitoring")
    monitor_memory_usage()
    
    # Performance tips
    st.markdown("---")
    st.subheader("💡 Performance Tips")
    
    tips = [
        "<strong>Unified Models</strong>: The new unified data models provide better performance and consistency.",
        "<strong>Cache Management</strong>: Use the cache management tools to clear old data and improve performance.",
        "<strong>Data Filtering</strong>: Apply filters to reduce the amount of data processed.",
        "<strong>Chart Optimization</strong>: Reduce the number of data points in charts for faster rendering.",
        "<strong>Regular Monitoring</strong>: Check the performance dashboard regularly to identify bottlenecks.",
        "<strong>System Resources</strong>: Monitor memory and CPU usage to ensure optimal performance."
    ]
    
    for tip in tips:
        st.info(tip)
    
    # Performance comparison
    st.markdown("---")
    st.subheader("📈 Performance Comparison")
    
    # Simulate different operations
    if st.button("🏃‍♂️ Run Performance Benchmark", use_container_width=True):
        with st.spinner("Running performance benchmark..."):
            results = []
            
            # Test different operations
            operations = [
                ("Load All Scenarios", lambda: load_all_scenarios()),
                ("Get Performance Metrics", lambda: get_unified_performance_metrics()),
                ("Clear Cache", lambda: clear_cache()),
            ]
            
            for op_name, operation in operations:
                start_time = time.time()
                try:
                    operation()
                    duration = time.time() - start_time
                    results.append({
                        'Operation': op_name,
                        'Duration (s)': f"{duration:.3f}",
                        'Status': '✅ Success'
                    })
                except Exception as e:
                    results.append({
                        'Operation': op_name,
                        'Duration (s)': 'N/A',
                        'Status': f'❌ Failed: {str(e)}'
                    })
            
            # Display results
            if results:
                import pandas as pd
                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)
    
    # Migration status
    st.markdown("---")
    st.subheader("🔄 Migration Status")
    
    migration_status = {
        "Data Loading": "✅ Updated to use unified models",
        "UI Components": "✅ Updated to use unified data access",
        "Financial Planner": "🔄 In progress - generating unified data",
        "Legacy Code Removal": "⏳ Pending - after full migration"
    }
    
    for component, status in migration_status.items():
        st.info(f"**{component}**: {status}")


def main() -> None:
    """Main function to render the performance monitoring page."""
    render_performance_page()


if __name__ == "__main__":
    main() 